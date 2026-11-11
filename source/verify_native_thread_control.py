"""Prove ThreadControl routing and cooperative pause-bit arithmetic with Unicorn.
No original Windows process, thread API, or plugin is started.
"""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/emulation-deps'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ESP,UC_X86_REG_ESI,UC_X86_REG_ECX,UC_X86_REG_EAX
B=(ROOT/'work/qmacro-host-image-current/runner.image-pages.bin').read_bytes()
STACK,CONTEXT=0x70000000,0x71000000


def machine():
    mu=Uc(UC_ARCH_X86,UC_MODE_32);mu.mem_map(0x400000,(len(B)+4095)&~4095);mu.mem_write(0x400000,B)
    mu.mem_map(STACK,0x4000);mu.mem_map(CONTEXT,0x4000);return mu


def read(mu,where):return struct.unpack('<I',mu.mem_read(where,4))[0]
def write(mu,where,value):mu.mem_write(where,struct.pack('<I',value&0xffffffff))


def main():
    cases=[]
    for operation in (-1,0,1,2,3,65537,65538):
        mu=machine();sp=STACK+0x2000
        write(mu,sp,0);write(mu,sp+4,42);write(mu,sp+8,operation);mu.reg_write(UC_X86_REG_ESP,sp)
        boundary=[]
        def stop(cpu,address,size,_):
            if address in (0x623ac0,0x623e20,0x65f820):boundary.append(address);cpu.emu_stop()
        mu.hook_add(UC_HOOK_CODE,stop);mu.emu_start(0x65f940,0x400000,count=50,timeout=50000)
        mode=operation&0xffff
        expected=0x623e20 if mode==0 else 0x623ac0 if mode in (1,2) else 0x65f820
        assert boundary==[expected],(operation,boundary)
        result={'mode':operation,'callee':hex(expected)}
        if mode in (0,1,2):
            current=mu.reg_read(UC_X86_REG_ESP);selector=read(mu,current+4);control=read(mu,current+8)
            assert read(mu,selector+4)==42
            assert control==(0 if mode==2 else 1)
            result.update(selector_worker=42,control_argument=control)
        cases.append(result)
    for flags in (0,8,0xa5,0xffffffff):
        for pause in (-1,0,1):
            mu=machine();bp=STACK+0x2000;write(mu,bp+12,pause);write(mu,CONTEXT+4,flags)
            mu.reg_write(UC_X86_REG_EBP,bp);mu.reg_write(UC_X86_REG_ESI,CONTEXT)
            mu.emu_start(0x623b73,0x623ba9,count=40,timeout=50000)
            actual=read(mu,CONTEXT+4)
            expected=(flags^8) if pause<0 else (flags&~8)|(8 if pause else 0)
            assert actual==expected,(flags,pause,actual,expected)
            cases.append({'initial_flags':flags,'pause_argument':pause,'result_flags':actual})
    selectors=[]
    for wanted in (0,42,-1):
        for actual in (0,42,43):
            mu=machine();sp=STACK+0x2000;selector=STACK+0x1000
            write(mu,sp,0x400000);write(mu,sp+4,CONTEXT);write(mu,selector+4,wanted);write(mu,CONTEXT+0x30f8,actual)
            mu.reg_write(UC_X86_REG_ESP,sp);mu.reg_write(UC_X86_REG_ECX,selector)
            mu.emu_start(0x60a120,0x400000,count=30,timeout=50000)
            result=mu.reg_read(UC_X86_REG_EAX);assert result==int(wanted==actual)
            selectors.append({'wanted_id':wanted,'context_id':actual,'matches':result})
    stop_bits=[]
    for flags in (0,4,8,0xffffffff):
        for request in (0,1,-1,2):
            mu=machine();bp=STACK+0x2000;write(mu,bp+8,request);write(mu,CONTEXT+4,flags)
            mu.reg_write(UC_X86_REG_EBP,bp);mu.reg_write(UC_X86_REG_ESI,CONTEXT)
            mu.reg_write(UC_X86_REG_ESP,bp-0x100)
            mu.emu_start(0x6301b4,0x6301c8,count=20,timeout=50000)
            actual=read(mu,CONTEXT+4);expected=(flags&~4)|((request&1)<<2)
            assert actual==expected
            stop_bits.append({'initial_flags':flags,'request':request,'result_flags':actual})
    report={'ok':True,'image_sha256':hashlib.sha256(B).hexdigest(),'cases':cases,'selector_cases':selectors,'stop_bit_cases':stop_bits,
       'selector_va':'0x60a120','selector_behavior':'Exact equality with context+0x30f8; absent ids produce no matched context.',
       'mapping':{'0':'stop selector through 0x623e20','1':'set cooperative pause bit 0x8','2':'clear cooperative pause bit 0x8'},
       'mode_conversion':'signed low 16 bits in wrapper',
       'pause_checkpoint_va':'0x625f10..0x625f42','script_dispatch_table_va':'0x7b72d8',
       'threadcontrol_wrapper_va':'0x65f940','pause_helper_va':'0x623ac0','stop_flag_helper_va':'0x6301a0','stop_flag':4,
       'os_executable_launched':False,'system_apis_called':False,
       'limit':'Pause/stop-bit arithmetic and mode routing verified; stop scan, UI notification, native cleanup and wall-clock scheduling not executed.'}
    (ROOT/'outputs/plugin-recovery/native-thread-control-contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'cases':len(cases),'selector_cases':len(selectors),'native_mode_mapping_verified':True,'native_scheduling_verified':False}))


if __name__=='__main__':main()
