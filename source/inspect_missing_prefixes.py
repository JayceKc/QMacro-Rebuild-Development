"""Inert inventory: source pool and surviving location groups around missing IR."""
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/initialization-recovery';OUT.mkdir(exist_ok=True)
groups=json.loads((ROOT/'outputs/qmacro-readable-analysis/總清單.json').read_text(encoding='utf-8-sig'))['groups']
summary=[]
for g in groups:
    folder=ROOT/'outputs/qmacro-readable-analysis'/g['directory']
    pool=json.loads((folder/'字串_閱讀對照.json').read_text(encoding='utf-8-sig'))
    rows=list(csv.DictReader((folder/'指令索引.csv').open(encoding='utf-8-sig')))
    used={int(r['string_index']) for r in rows if r['string_index']}
    missing=json.loads((folder/'缺失記錄.json').read_text(encoding='utf-8-sig'))
    first_text=min(int(r['record']) for r in rows if int(r['record'])>max(missing['records']) and r['opcode'] in ('2','30'))
    first_sl=int(rows[first_text]['string_index'])
    prefix=[dict(s,referenced_by_surviving_record=s['index'] in used) for s in pool if s['index']<first_sl]
    location_groups=[]
    for r in rows[:first_text]:
        key=(r['location_id'],r['location_flags'])
        if not location_groups or tuple(location_groups[-1]['key'])!=key:
            location_groups.append({'key':key,'records':[]})
        location_groups[-1]['records'].append({'record':int(r['record']),'op':int(r['opcode']),
           'sl':int(r['string_index']) if r['string_index'] else None,
           'protected_missing':r['protected_missing']=='True'})
    data={'module':g['module'],'missing_ranges':missing['ranges'],'first_preserved_text_after_missing':first_text,'first_preserved_text_sl':first_sl,
          'prefix_pool':prefix,'location_groups':location_groups,'reconstructed_instructions':0,
          'scope_limit':'SL cutoff is a reading window, not proof of a function boundary or exhaustive erased-source coverage. Compiler allocation order can defer RHS strings beyond this cutoff.'}
    (OUT/f'{g["module"]:02}-prefix-inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=[f'# {g["module"]:02} {g["name"]}：缺失初始化線索','',
           '這是線索清單，尚未將未引用字串當作原始指令。',
           'SL 截止點只供閱讀；它不是函式入口或完整缺失來源的界線。編譯器可能把右側表達式配置在截止點之後。','', '## 保留的位置群組','']
    for item in location_groups:
        lo,hi=item['records'][0]['record'],item['records'][-1]['record']
        ops=','.join(str(r['op']) for r in item['records'])
        lines.append(f'L{lo:05d}..L{hi:05d} loc={item["key"][0]} flags={item["key"][1]} count={hi-lo+1} ops={ops}')
    lines+=['','## 原 SL 字串順序','']
    for s in prefix:
        lines += [f'### SL[{s["index"]}] kind={s["kind"]}, 現有引用={s["referenced_by_surviving_record"]}','',s['readable'],'']
    (OUT/f'{g["module"]:02}-prefix-reading.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    summary.append({'module':g['module'],'missing_records':missing['count'],'prefix_pool':len(prefix),
                    'unreferenced_prefix_strings':sum(not s['referenced_by_surviving_record'] for s in prefix),
                    'location_groups':len(location_groups),'first_preserved_text_after_missing':first_text})
(OUT/'prefix-inventory-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary))
