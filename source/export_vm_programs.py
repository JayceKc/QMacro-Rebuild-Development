"""Export exact preserved instruction programs, keeping missing spans explicit."""
from pathlib import Path
import csv,hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/QMacro-Rebuild-Development/programs'
NEGATE=bytes((-v)&255 for v in range(256))


def main():
    OUT.mkdir(exist_ok=True)
    manifest=[]
    groups=json.loads((ROOT/'outputs/qmacro-readable-analysis/總清單.json').read_text(encoding='utf-8-sig'))['groups']
    for group in groups:
        module=group['module'];folder=ROOT/f'outputs/restored-files/account/{module:02}/qmcfile-streams'
        script=(folder/'Script.decoded.bin').read_bytes()
        count=struct.unpack('<H',script[:2].translate(NEGATE))[0]
        code=list(struct.iter_unpack('<Biii',script[2:2+count*13].translate(NEGATE)))
        assert count==group['records'] and code[-1]==(22,0,0,0)
        rows=list(csv.DictReader((ROOT/'outputs/qmacro-readable-analysis'/group['directory']/'指令索引.csv').open(encoding='utf-8-sig')))
        assert len(rows)==count
        missing=[]
        for i,(op,location,operand,field3) in enumerate(code):
            row=rows[i]
            assert int(row['opcode'])==op and int(row['operand'])==operand and int(row['field_3'])==field3
            assert int(row['location_id'])==location&0xfffff
            if row['protected_missing']=='True':missing.append(i)
        assert len(missing)==group['missing_records']
        strings=json.loads((folder/'SL.full-text.json').read_text(encoding='utf-8-sig'))
        assert all(s['index']==i for i,s in enumerate(strings))
        metadata=json.loads((ROOT/'outputs/QMacro-Rebuild/modules'/group['directory']/'結構.json').read_text(encoding='utf-8-sig'))
        program={'schema':1,'module':module,'name':group['name'],
                 'source_script_sha256':hashlib.sha256(script).hexdigest(),
                 'source_sl_sha256':hashlib.sha256((folder/'SL.full-text.json').read_bytes()).hexdigest(),
                 'record_tuple_layout':['opcode','location','operand','field_3'],
                 'code':code,'strings':[s['value'] for s in strings],
                 'missing_records':missing,'callbacks':metadata['events'],
                 'worker_starts':[{'record':i,'entry':i+r[2]} for i,r in enumerate(code) if r[0]==24],
                 'full_program_restored':False,'default_missing_policy':'stop with exact record; do not treat as recovered NOP',
                 'execution_policy':'Text is preserved data. Original COM creation, DLL registration, filesystem and OS calls require explicit owned adapters.'}
        file=OUT/f'{module:02}.json';file.write_text(json.dumps(program,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
        manifest.append({'module':module,'file':file.name,'records':count,'missing_records':len(missing),
                         'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    summary={'modules':manifest,'record_total':sum(m['records'] for m in manifest),
             'missing_total':sum(m['missing_records'] for m in manifest),'full_program_restored':False}
    (OUT/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='modules'}))


if __name__=='__main__':main()
