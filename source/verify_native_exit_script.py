"""Replay only the ExitScript wrapper; intercept all native helper boundaries."""
import collections,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/emulation-deps'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_ECX,UC_X86_REG_EIP
B=(ROOT/'work/qmacro-host-image-current/runner.image-pages.bin').read_bytes()
STACK,OBJ,CTX,PARENT=0x70000000,0x71000000,0x71001000,0x71006000
def main():
    cases=[]
    for parent in (0,PARENT):
        for restart in (0,1,-1,65536):
            mu=Uc(UC_ARCH_X86,UC_MODE_32)
            mu.mem_map(0x400000,(len(B)+4095)&~4095);mu.mem_write(0x400000,B)
            mu.mem_map(STACK,0x4000);mu.mem_map(OBJ,0xb000)
            def read(p):return struct.unpack('<I',mu.mem_read(p,4))[0]
            def write(p,v):mu.mem_write(p,struct.pack('<I',v&0xffffffff))
            sp=STACK+0x2000;write(sp,0x400000);write(sp+4,restart)
            write(OBJ+0x28,CTX);write(CTX+0x3114,parent)
            mu.reg_write(UC_X86_REG_ESP,sp);mu.reg_write(UC_X86_REG_ECX,OBJ)
            calls=[]
            def boundary(cpu,address,size,_):
                current=cpu.reg_read(UC_X86_REG_ESP)
                if address==0x623e20:
                    selector=read(current+4)
                    calls.append({'helper':hex(address),'selector_vtable':hex(read(selector)),
                                  'root_context':hex(read(selector+4)),'notification':read(current+8)})
                    assert read(selector)==0x759910 and read(selector+4)==(parent or CTX)
                    assert read(current+8)==0
                    # Do not execute the helper; return at its exact call boundary.
                    cpu.reg_write(UC_X86_REG_EIP,read(current));cpu.reg_write(UC_X86_REG_ESP,current+4)
                elif address==0x628100:
                    calls.append({'helper':hex(address),'context':hex(cpu.reg_read(UC_X86_REG_ECX)),
                                  'entry_argument':read(current+4)})
                    assert cpu.reg_read(UC_X86_REG_ECX)==CTX and read(current+4)==0
                    cpu.emu_stop()
                elif not 0x65e490<=address<=0x65e4d4:
                    raise AssertionError('Unexpected execution boundary '+hex(address))
            mu.hook_add(UC_HOOK_CODE,boundary)
            mu.emu_start(0x65e490,0x400000,count=100,timeout=50000)
            assert len(calls)==(2 if restart else 1)
            cases.append({'parent_present':bool(parent),'restart_argument':restart,'calls':calls})
    source=json.loads((ROOT/'outputs/plugin-recovery/qmlibrary-exit-and-thread.json').read_text(encoding='utf-8'))
    usage=collections.Counter(r['text'] for r in source if 'ExitScript' in r['text'])
    report={'ok':True,'image_sha256':hashlib.sha256(B).hexdigest(),'wrapper_va':'0x65e490',
        'cases':cases,'preserved_source_usage':dict(usage),'restart_comparison':'full 32-bit argument nonzero',
        'system_apis_called':False,'original_process_started':False,
        'limit':'Helper calls intercepted, not executed. Root-family stop, reinitialization, and native scheduling remain unverified.',
        'dry_host_policy':'Accept explicit/default zero; reject nonzero with an unresolved lifecycle error.'}
    (ROOT/'outputs/plugin-recovery/native-exit-script-contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'cases':len(cases),'source_calls':sum(usage.values())}))
if __name__=='__main__':main()
