"""Read-only SL dataflow hints for all eight modules; no branch invention."""
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'outputs/qmacro-readable-analysis';OUT=ROOT/'outputs/initialization-recovery'
TEMP='F2730835_2229_445E_97C7_l3F76l2771DA'
summary=[]
for folder in sorted(BASE.iterdir()):
    if not (folder/'字串_閱讀對照.json').exists():continue
    module=int(folder.name.split('-')[0]);pool=json.loads((folder/'字串_閱讀對照.json').read_text(encoding='utf-8-sig'))
    rows=list(csv.DictReader((folder/'指令索引.csv').open(encoding='utf-8-sig')))
    references={}
    for row in rows:
        if row['string_index']:references.setdefault(int(row['string_index']),[]).append({'record':int(row['record']),'op':int(row['opcode'])})
    controls=json.loads((BASE/'介面資料'/f'account-{module:02}.json').read_text(encoding='utf-8-sig'))['controls']
    names={c['name'] for c in controls};bindings=[]
    arrays={}
    for s in pool:
        m=re.fullmatch(r'([A-Za-z_0-9]+)=ARRAY\(([0-9, +-]+)\)',s['value'],re.I)
        if m:arrays[m[1]]={'sl':s['index'],'values':[int(x) for x in m[2].split(',')]}
    for i,s in enumerate(pool):
        m=re.fullmatch(r'Form1\.([A-Za-z_0-9]+)\.(ListIndex|Value|Text)',s['value'],re.I)
        if not m:continue
        item={'property':s['value'],'sl':i,'control_exists':m[1] in names,'surviving_records':references.get(i,[]),
              'classification':'unresolved','destination':None,'sources':[i]}
        nexts=pool[i+1:i+5]
        if nexts and nexts[0]['value'].endswith('='+TEMP):
            copied=nexts[0]['value'].split('=',1)[0];item['sources'].append(i+1)
            if len(nexts)>=4 and nexts[1]['value'].startswith(TEMP+'=') and re.fullmatch(r'[A-Za-z_0-9]+',nexts[2]['value']):
                slot=nexts[1]['value'].split('=',1)[1]
                if nexts[3]['value'].startswith(slot+'='):
                    item.update(classification='direct_shared_dataflow',destination=nexts[2]['readable'],expression=nexts[3]['readable'])
                    item['sources'] += [i+4,i+2,i+3]
            elif len(nexts)>=2 and '=' in nexts[1]['value'] and copied in nexts[1]['value'].split('=',1)[1] and not nexts[1]['value'].startswith('Sgn('):
                dest=nexts[1]['value'].split('=',1)[0]
                if re.fullmatch(r'[A-Za-z_0-9]+',dest):
                    item.update(classification='direct_local_dataflow',destination=nexts[1]['readable'].split('=',1)[0],expression=nexts[1]['readable']);item['sources'].append(i+2)
                    for name,array in arrays.items():
                        if name+'(' in nexts[1]['value']:item['index_array']=array
            elif len(nexts)>=2 and nexts[1]['value'].startswith('Sgn('):
                item.update(classification='conditional_read',condition=nexts[1]['readable']);item['sources'].append(i+2)
        if any(r['op']==38 for r in item['surviving_records']):item['classification']='surviving_ui_write'
        item['source_strings']=[{'sl':j,'readable':pool[j]['readable']} for j in item['sources']]
        item['limits']='Dataflow from retained source only; erased branch addresses and runtime ordering are not thereby recovered.'
        bindings.append(item)
    report={'module':module,'name':folder.name,'bindings':bindings,'branch_operands_recovered':False}
    (OUT/f'{module:02}-ui-bindings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary.append({'module':module,'ui_property_occurrences':len(bindings),'missing_controls':sum(not b['control_exists'] for b in bindings),
        'direct_dataflows':sum(b['classification'].startswith('direct_') for b in bindings),'conditional_reads':sum(b['classification']=='conditional_read' for b in bindings)})
(OUT/'ui-bindings-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
