"""Compile preserved code without evaluating it; retain record/SL provenance."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work'
OUT=ROOT/'outputs/plugin-recovery'


def main():
    selftest=json.loads((OUT/'vbs-engine-self-test.json').read_text(encoding='utf-8-sig'))
    assert selftest['ok'] and 'compile_only_no_side_effect' in selftest['checks']
    modules=[]
    groups=json.loads((ROOT/'outputs/qmacro-readable-analysis/總清單.json').read_text(encoding='utf-8-sig'))['groups']
    for g in groups:
        textpath=ROOT/'outputs/restored-files/account'/f'{g["module"]:02}'/'qmcfile-streams/SL.full-text.json'
        sl={s['index']:s for s in json.loads(textpath.read_text(encoding='utf-8-sig'))}
        rows=list(csv.DictReader((ROOT/'outputs/qmacro-readable-analysis'/g['directory']/'指令索引.csv').open(encoding='utf-8-sig')))
        fragments=[];seen=set()
        for r in rows:
            op=int(r['opcode'])
            if op not in (2,4,30) or not r['string_index']:continue
            index=int(r['string_index'])
            if (op,index) in seen:continue
            seen.add((op,index))
            s=sl[index];assert s['kind'] in ('decoded-text','text','empty')
            code=s['value']
            if op==4:code='qmacro_compile_audit_result=('+code+')'
            fragments.append({'record':int(r['record']),'sl':index,'opcode':op,'text':code})
        modules.append({'module':g['module'],'source_sha256':hashlib.sha256(textpath.read_bytes()).hexdigest(),'fragments':fragments})
    path=WORK/'vbs-compile-audit-input.json'
    path.write_text(json.dumps(modules,ensure_ascii=False),encoding='utf-8')
    output=OUT/'vbs-preserved-compile-audit.json'
    p=subprocess.run([str(WORK/'QMacroVbsEngineSelfTest.exe'),'--compile-audit',str(path),str(output)],
                     timeout=60,creationflags=subprocess.CREATE_NO_WINDOW,capture_output=True)
    report=json.loads(output.read_text(encoding='utf-8-sig'))
    report['input_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    report['engine_source_sha256']=hashlib.sha256((WORK/'QMacroVbsEngine.cs').read_bytes()).hexdigest()
    report['engine_exe_sha256']=hashlib.sha256((WORK/'QMacroVbsEngineSelfTest.exe').read_bytes()).hexdigest()
    report['scope']='Only preserved op2/op30 statements and op4 expressions; missing records and runtime behavior not validated.'
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':report['ok'],'fragments':report['total_fragments'],'failed':report['failed'],
                      'modules':len(report['modules']),'original_script_executed':False}))
    return p.returncode


if __name__=='__main__':sys.exit(main())
