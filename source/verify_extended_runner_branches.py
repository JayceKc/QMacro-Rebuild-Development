"""Additional bounded branches from the actual dispatch table; no script/OS calls."""
from pathlib import Path
import hashlib,json,struct
import verify_runner_control_contracts as base
ROOT=Path(__file__).resolve().parents[1]
def main():
    cases=[];rows=[]
    nops=(3,15,17,18,19,20,32,34,36)
    for op in range(2,41):
        va=struct.unpack_from('<I',base.CODE,0x627c04-0x400000+(op-2)*4)[0]
        rows.append({'opcode':op,'handler_va':hex(va)})
        if op in nops or 7<=op<=11:base.ENTRY[op]=va
    for op in nops:
        assert base.ENTRY[op]==0x627834
        actual=base.run(op,pc=8);assert actual['pc']==9 and actual['boundary']=='next-dispatch'
        cases.append({'opcode':op,'inputs':{},'result':actual})
    for op in range(7,12):
        for flags in (0,1,2,3,0x100,0xfffffffc):
            taken={7:not flags&1,8:not flags&3,9:not flags&2,10:bool(flags&2),11:bool(flags&3)}[op]
            for delta in (-9,-8,-4,0,7,8):
                target=(8+delta)&0xffffffff
                actual=base.run(op,flags=flags,operand=delta)
                assert actual['pc']==(target if taken else 9),(op,flags,delta,actual)
                assert actual['boundary']==('invalid-target' if taken and target>=16 else 'next-dispatch')
                cases.append({'opcode':op,'inputs':{'flags':flags,'delta':delta},'result':actual})
    report={'ok':True,'image_sha256':hashlib.sha256(base.CODE).hexdigest(),'dispatch_table_va':'0x627c04',
        'dispatch_rows':rows,'cases':cases,'case_count':len(cases),
        'conditional_semantics':{'7':'jump if zero bit clear','8':'jump if zero and negative bits clear','9':'jump if negative bit clear','10':'jump if negative bit set','11':'jump if zero or negative bit set'},
        'advance_only_opcodes':list(nops),'original_script_executed':False,'os_api_called':False,
        'limits':['Opcode identities of erased records are still unknown; this does not restore their operands or missing text.',
                  'Taken relative jumps are checked against context record count, with 32-bit arithmetic.',
                  'Branch flag bits are supplied, not inferred from unknown original comparisons.']}
    (ROOT/'outputs/plugin-recovery/runner-extended-branches.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'cases':len(cases),'new_conditional_handlers':5,'advance_handlers':len(nops)}))
if __name__=='__main__':main()
