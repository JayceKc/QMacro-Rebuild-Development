"""Audit text opcode choice against retained SL encoding metadata across all groups."""
from pathlib import Path
import collections,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    counts=collections.Counter();modules=[];errors=[]
    for path in sorted((ROOT/'outputs/QMacro-Rebuild-Development/programs').glob('[0-9][0-9].json')):
        p=json.loads(path.read_text(encoding='utf-8'));folder=next((ROOT/'outputs/qmacro-readable-analysis').glob(path.stem+'-*'))
        source=folder/'字串_閱讀對照.json';pool=json.loads(source.read_text(encoding='utf-8-sig'));n=0
        for i,(op,location,arg,field) in enumerate(p['code']):
            if op not in (2,30):continue
            kind=pool[arg]['kind'];expected=30 if kind=='decoded-text' else 2;counts[str(op)+'/'+kind]+=1;n+=1
            if op!=expected:errors.append({'module':p['module'],'record':i,'actual':op,'sl':arg,'kind':kind})
        modules.append({'module':p['module'],'checked_records':n,'program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'reading_pool_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    report={'ok':not errors,'checked_records':sum(counts.values()),'counts':dict(counts),'modules':modules,'mismatches':errors,
            'rule':'decoded-text ->30; retained plain text ->2','original_missing_operands_recovered':False,
            'limit':'Corroborates choosing text execution opcodes from retained encoding; does not recover absent branch/call operands or original record bytes.'}
    (ROOT/'outputs/initialization-recovery/text-opcode-encoding-contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'ok':report['ok'],'checked':report['checked_records'],'counts':dict(counts)}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
