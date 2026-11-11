from pathlib import Path
import collections,csv,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/initialization-recovery'
templates=collections.defaultdict(list)
for folder in sorted((ROOT/'outputs/qmacro-readable-analysis').iterdir()):
    source=folder/'指令索引.csv'
    if not source.exists():continue
    pool=json.loads((folder/'字串_閱讀對照.json').read_text(encoding='utf-8-sig'))
    rows=list(csv.DictReader(source.open(encoding='utf-8-sig')))
    groups=[]
    for row in rows:
        if not groups or groups[-1][0]['location_id']!=row['location_id']:groups.append([])
        groups[-1].append(row)
    for group in groups:
        if any(r['protected_missing']=='True' for r in group):continue
        if not any(r['opcode'] in ('27','28','24','37','38') for r in group):continue
        refs=[int(r['string_index']) for r in group if r['string_index']]
        if not refs:continue
        lo,hi=min(refs),max(refs)
        if hi-lo>15:continue
        signature=','.join(r['opcode'] for r in group)
        if len(templates[signature])>=4:continue
        templates[signature].append({'module':folder.name,'first':int(group[0]['record']),
           'last':int(group[-1]['record']),'refs':refs,'pool':pool[max(0,lo-2):hi+3],
           'records':[{'record':int(r['record']),'opcode':int(r['opcode']),'sl':r['string_index'],'text':r['readable_statement']} for r in group]})
(OUT/'preserved-line-templates.json').write_text(json.dumps(templates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for signature,examples in templates.items():
    if '28' in signature:print(signature,json.dumps(examples[:1],ensure_ascii=False))
