"""Emulate only bounded Runner arithmetic/branch handlers in isolated CPU memory.

Stops before dispatcher, exception builders, interpreter calls, or external APIs.
This neither launches the executable nor loads a DLL into Windows.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'work/emulation-deps')]
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP,UC_X86_REG_ESP,UC_X86_REG_EIP

IMAGE=ROOT/'work/qmacro-host-image-current/runner.image-pages.bin'
CODE=IMAGE.read_bytes()
CTX,RECORD,STACK,RETURNS=0x70000000,0x71000000,0x72000000,0x73000000
ENTRY={4:0x62609a,5:0x626e48,6:0x62611c,12:0x6261f2,13:0x626275,16:0x626126,23:0x626415}
BOUNDARIES={0x625da7:'next-dispatch',0x626e5e:'invalid-target',0x62613c:'invalid-target',
            0x62629d:'empty-return-error',0x6261fc:'call-depth-error',0x6260ef:'array-bounds-error',
            0x625e5a:'iteration-exit'}


def run(op,operand=0,pc=8,flags=0,depth=0,capacity=8192,top=3,eval_word=0,iteration_flag=1):
    mu=Uc(UC_ARCH_X86,UC_MODE_32)
    mu.mem_map(0x400000,(len(CODE)+4095)&~4095);mu.mem_write(0x400000,CODE)
    for base,size in ((CTX,0x4000),(RECORD,0x1000),(STACK,0x4000),(RETURNS,0x9000)):mu.mem_map(base,size)
    def write(address,value):mu.mem_write(address,struct.pack('<I',value&0xffffffff))
    write(CTX+4,flags);write(CTX+0x20,pc);write(CTX+0x3248,16)
    write(CTX+0x0c,RETURNS);write(CTX+0x10,capacity);write(CTX+0x1c,depth)
    mu.mem_write(RECORD,struct.pack('<Biii',op,0,operand,0))
    if 0<depth<=8192:write(RETURNS+(depth-1)*4,top)
    bp=STACK+0x2000;write(bp-0x190,eval_word);write(bp-0x4c,iteration_flag)
    for reg,value in ((UC_X86_REG_ESI,CTX),(UC_X86_REG_EDI,RECORD),(UC_X86_REG_EBP,bp),(UC_X86_REG_ESP,bp-0x300)):
        mu.reg_write(reg,value)
    reached=[]
    def boundary(cpu,address,size,_):
        if address in BOUNDARIES:reached.append(address);cpu.emu_stop()
    mu.hook_add(UC_HOOK_CODE,boundary)
    mu.emu_start(ENTRY[op],0x400000,count=100,timeout=50000)
    assert reached,('Handler failed to reach declared boundary',op,hex(mu.reg_read(UC_X86_REG_EIP)))
    def read(address):return struct.unpack('<I',mu.mem_read(address,4))[0]
    return {'boundary':BOUNDARIES[reached[0]],'boundary_va':hex(reached[0]),'pc':read(CTX+0x20),
            'flags':read(CTX+4),'depth':read(CTX+0x1c),'saved_return':read(RETURNS+depth*4) if depth<8192 else None}


def main():
    samples=[]
    def check(op,expected,**kwargs):
        actual=run(op,**kwargs)
        for key,value in expected.items():assert actual[key]==value,(op,kwargs,expected,actual)
        samples.append({'opcode':op,'handler_va':hex(ENTRY[op]),'inputs':kwargs,'result':actual})
    for initial in (0,3,0xa4,0xffffffff):
        for word in (0,1,0xffff,0x8000,0x7fff,0x10000):
            low=word&0xffff;bits=(1 if low==0 else 0)|(2 if low&0x8000 else 0)
            check(4,{'pc':9,'flags':(initial&0xfffffffc)|bits,'boundary':'next-dispatch'},flags=initial,eval_word=word)
    for target in (0,15,16,-1):
        check(5,{'boundary':'next-dispatch' if 0<=target<16 else 'invalid-target','pc':target if 0<=target<16 else 8},operand=target)
    for operand in (-9,-8,-4,0,7,8):
        target=(8+operand)&0xffffffff
        check(16,{'boundary':'next-dispatch' if target<16 else 'invalid-target','pc':target},operand=operand)
        for flags in (0,1,2,3,0x100):
            taken=flags&1
            check(6,{'boundary':'invalid-target' if taken and target>=16 else 'next-dispatch','pc':target if taken else 9},operand=operand,flags=flags)
    for depth in (0,1,8191):
        check(12,{'boundary':'next-dispatch','pc':3,'depth':depth+1,'saved_return':9},depth=depth,operand=3)
    check(12,{'boundary':'call-depth-error','depth':8192},depth=8192,operand=3)
    check(12,{'boundary':'array-bounds-error'},depth=1,capacity=1,operand=3)
    check(12,{'boundary':'invalid-target','depth':1,'saved_return':9},operand=16)
    for depth in (1,2,8192):check(13,{'boundary':'next-dispatch','depth':depth-1,'pc':3},depth=depth)
    check(13,{'boundary':'empty-return-error','depth':0},depth=0)
    for flag in (0,1):check(23,{'boundary':'iteration-exit' if flag==0 else 'next-dispatch','pc':8 if flag==0 else 9},iteration_flag=flag)
    report={'ok':True,'image_sha256':hashlib.sha256(CODE).hexdigest(),'cases':len(samples),'samples':samples,
            'os_executable_launched':False,'plugins_loaded':False,'original_script_executed':False,
            'limits':['op4 starts after interpreter evaluation: only its low-16-bit flag conversion is exercised.',
                      'op23 local iteration flag is supplied; its caller initialization is not inferred.',
                      'All paths stop before native exception construction and any OS API.']}
    (ROOT/'outputs/plugin-recovery/runner-control-contracts.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('samples','limits')}))


if __name__=='__main__':main()
