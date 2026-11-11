"""Bounded native CPU evidence for packed record's final DWORD.

Executes no script or Windows API. Interpreter/error reporter are explicit
recording boundaries. Cached text getter and encoded-buffer negation are real
Runner instructions; BSTR length is supplied from an owned buffer's byte length.
"""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'work/emulation-deps')]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ESP,UC_X86_REG_EBP,UC_X86_REG_EIP

IMAGE=ROOT/'work/qmacro-host-image-current/runner.image-pages.bin'
CODE=IMAGE.read_bytes()
CTX,RECORD,STACK,CACHE,WRAPPER,CHAR=0x70000000,0x71000000,0x72000000,0x73000000,0x74000000,0x75000000


def text_case(op,field3,text,success,debug=False,trace_debug=False,debug_mode=0,breakpoint=False,same_line=False,notify=False,location=471):
    assert op in (2,30)
    mu=Uc(UC_ARCH_X86,UC_MODE_32);mu.mem_map(0x400000,(len(CODE)+4095)&~4095);mu.mem_write(0x400000,CODE)
    for base,size in ((CTX,0x4000),(RECORD,0x1000),(STACK,0x4000),(CACHE,0x1000),(WRAPPER,0x1000),(CHAR-0x1000,0x3000),
                      (0x76e54000,0x2000),(0x77411000,0x2000),(0x74fa8000,0x1000)):mu.mem_map(base,size)
    put=lambda at,n:mu.mem_write(at,struct.pack('<I',n&0xffffffff))
    get=lambda at:struct.unpack('<I',mu.mem_read(at,4))[0]
    operand=3;pc=8;bp=STACK+0x2000
    put(CTX+0x20,pc);put(CTX+0x3248,20);put(CTX+0x30b4,CACHE);put(CTX+0x30b8,8)
    put(CTX+0x24,location if same_line else 0);put(CTX+0x3128,(debug_mode<<1)|(8 if notify else 0));put(WRAPPER+0x104,1)
    put(CACHE+operand*4,WRAPPER);put(WRAPPER,CHAR);put(CHAR-4,len(text.encode('utf-16le')))
    source=text.encode('utf-16le');words=struct.unpack('<'+'H'*(len(source)//2),source)
    encoded=struct.pack('<'+'H'*len(words),*[(-v)&0xffff for v in words])
    initial=encoded if op==30 else source;mu.mem_write(CHAR,initial+b'\0\0')
    mu.mem_write(RECORD,struct.pack('<BiiI',op,location,operand,field3));put(bp-0x158,int(debug))
    for reg,value in ((UC_X86_REG_ESI,CTX),(UC_X86_REG_EDI,RECORD),(UC_X86_REG_EBP,bp),(UC_X86_REG_ESP,bp-0x300)):mu.reg_write(reg,value)
    reads=[];calls=[];boundaries=[];steps=0
    def ret(pop,eax=0):
        sp=mu.reg_read(UC_X86_REG_ESP);target=get(sp);mu.reg_write(UC_X86_REG_EAX,eax);mu.reg_write(UC_X86_REG_ESP,sp+4+pop);mu.reg_write(UC_X86_REG_EIP,target)
    def read_hook(cpu,access,address,size,value,user):
        if address<RECORD+13 and address+size>RECORD:reads.append({'offset':address-RECORD,'size':size})
    def hook(cpu,address,size,user):
        nonlocal steps
        steps+=1
        if address==0x625da7:boundaries.append('next_dispatch');cpu.emu_stop();return
        if address==0x6307d0 and not trace_debug:boundaries.append('debugger_callback');cpu.emu_stop();return
        if address==0x630260:boundaries.append('debug_pause_boundary');cpu.emu_stop();return
        if address in (0x774125e0,0x77411660):ret(4);return
        if address==0x74fa80c0:
            sp=cpu.reg_read(UC_X86_REG_ESP);calls.append({'kind':'debug_message_boundary','hwnd':get(sp+4),'message':get(sp+8),'location':get(sp+12),'flag':get(sp+16)});ret(16,1);return
        if address==0x622c40:
            calls.append({'kind':'breakpoint_lookup_boundary','found':breakpoint});ret(12,WRAPPER+0x100 if breakpoint else 0);return
        if address==0x62a730:
            sp=cpu.reg_read(UC_X86_REG_ESP);arg=get(sp+4);assert arg==CACHE+operand*4
            decoded=bytes(cpu.mem_read(get(get(arg)),len(source))).decode('utf-16le')
            calls.append({'kind':'interpreter_boundary','text':decoded,'context_offset':cpu.reg_read(UC_X86_REG_ECX)-CTX,'return_success':success});ret(4,int(success));return
        if address==0x76e54e10:
            sp=cpu.reg_read(UC_X86_REG_ESP);pointer=get(sp+4);assert pointer==CHAR;ret(4,len(source)//2);return
        if address==0x6236e0:
            sp=cpu.reg_read(UC_X86_REG_ESP);calls.append({'kind':'error_report_boundary','location':get(sp+4),'flag':get(sp+8)});ret(8);return
        assert 0x400000<=address<0x400000+len(CODE),hex(address)
    mu.hook_add(UC_HOOK_MEM_READ,read_hook);mu.hook_add(UC_HOOK_CODE,hook)
    mu.emu_start(0x625f4a,0x400000,count=5000,timeout=100000)
    assert boundaries,('No declared boundary',hex(mu.reg_read(UC_X86_REG_EIP)))
    assert not any(r['offset']<13 and r['offset']+r['size']>9 for r in reads),reads
    actual=bytes(mu.mem_read(CHAR,len(initial)))
    if not debug:
        assert calls[0]['text']==text and actual==initial
        assert get(CTX+0x20)==pc+1 and get(CTX+0x24)==location
        assert len(calls)==(1 if success else 2)
    return {'opcode':op,'field_3':field3,'source':text,'success':success,'debug_enabled':debug,'trace_debug':trace_debug,'debug_mode':debug_mode,
            'breakpoint_present':breakpoint,'same_source_line':same_line,'notify_debug_line':notify,'source_location':location,'boundary':boundaries[0],
            'calls':calls,'record_reads':reads,'pc_after':get(CTX+0x20),'location_after':get(CTX+0x24),
            'buffer_restored':actual==initial,'cpu_instructions':steps}


def main():
    cases=[]
    for op in (2,30):
        for text in ('YC=66','Call QMLibrary.TracePrint("測試")',''):
            for success in (False,True):
                baseline=None
                for field in (0,1,0x80000000,0xffffffff):
                    actual=text_case(op,field,text,success);semantic={k:actual[k] for k in ('boundary','calls','record_reads','pc_after','location_after','buffer_restored')}
                    if baseline is None:baseline=semantic
                    else:assert baseline==semantic
                    cases.append(actual)
    debug=[text_case(op,field,'YC=66',True,True) for op in (2,30) for field in (0,1)]
    debug_paths=[]
    for op in (2,30):
        for mode in (0,1,2):
            for same in (False,True):
                for bp in (False,True):
                    for notify in (False,True):
                        for loc in (0,471):
                            baseline=None
                            for field in (0,1,0xffffffff):
                                value=text_case(op,field,'YC=66',True,True,True,mode,bp,same,notify,loc)
                                semantic={k:value[k] for k in ('boundary','calls','record_reads','pc_after','location_after','buffer_restored')}
                                if baseline is None:baseline=semantic
                                else:assert baseline==semantic
                                debug_paths.append(value)
    report={'ok':True,'image_sha256':hashlib.sha256(CODE).hexdigest(),'record_layout':'<BiiI, 13 bytes; final DWORD at +9',
        'entry_va':'0x625f4a','cached_text_getter_va':'0x623030','interpreter_boundary_va':'0x62a730','error_report_boundary_va':'0x6236e0',
        'normal_text_cases':cases,'debug_callback_boundaries':debug,'debug_dispatch_cases':debug_paths,'case_count':len(cases),'debug_boundary_cases':len(debug),'debug_dispatch_case_count':len(debug_paths),
        'normal_cached_text_field_3_neutral_verified':True,'all_field_3_semantics_verified':False,
        'original_script_executed':False,'os_api_called':False,
        'limits':['Only cached-string, normal text success/failure dispatch paths are followed completely.',
                  'Debug callback paths are followed to normal dispatch or before the pause-wait function; breakpoint lookup/critical sections/messages are explicit supplied boundaries.',
                  'Interpreter and error reporter return values are supplied; their internals are not executed.',
                  'Uncached allocation/decoding, loader, unrelated opcodes and whole Runner lifecycle are not proved.']}
    out=ROOT/'outputs/plugin-recovery/runner-record-field3.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'ok':True,'normal_text_cases':len(cases),'debug_boundaries':len(debug),'debug_dispatch_cases':len(debug_paths)}))


if __name__=='__main__':main()
