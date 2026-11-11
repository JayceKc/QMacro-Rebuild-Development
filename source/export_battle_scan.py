"""Link the three retained picture-count routines and inventory the remaining records."""
import hashlib
import json
from collections import Counter

from export_battle_recovery import CANDIDATES
from export_battle_tail import build_tail
from export_cube_routines import PROJECT


SCAN_RANGES = {
    '01': ((13574,13603,'逐行找圖計數'),),
    '03': ((6426,6455,'逐行找圖計數'),),
    '06': ((10258,10287,'逐行找圖計數'),),
}
ROOT_SUFFIX = {'01': (562,740,433), '06': (570,571,421)}


def build_scan(module, raw, base):
    return build_tail(module,raw,base,SCAN_RANGES[module])


def inventory(module, raw, base, control):
    code = raw['code']
    missing = set(raw['missing_records'])
    linked = {a['record'] for a in base['actions']+control['actions']}
    first = next(i for i,row in enumerate(code) if row[0]==29)
    callback = {at for info in raw['callbacks'] for at in range(info['entry'],info['return']+1)}
    suffix = set()
    if module in ROOT_SUFFIX:
        start,end,target = ROOT_SUFFIX[module]
        if code[end][0]!=16 or end+code[end][2]!=target or target not in missing:
            raise ValueError(('Unreviewed root suffix boundary',module,end,target))
        suffix = set(range(start,end+1))
    entries = {row['entry']:row['last'] for row in base['routines']+control['routines']}
    rows = []
    for at,(op,loc,arg,flag) in enumerate(code):
        if at in linked or at in missing:
            continue
        row = dict(record=at,opcode=op,location=loc,operand=arg,field_3=flag)
        if op in (2,4,27,28,30,31,33,35,37,38):
            row['source'] = raw['strings'][arg]
        if op in (5,12):
            row['target'] = arg
        elif op in (6,16,24):
            row['target'] = at+arg
        if at<=first:
            row['kind'] = 'declaration_or_dispatch'
        elif at in callback:
            row['kind'] = 'form_callback'
        elif at in suffix:
            row['kind'] = 'root_suffix'
        elif op==16 and at+1 in entries and at+arg==entries[at+1]+1:
            row.update(kind='skip_definition',target=at+arg)
        elif op in (33,35,23,22,16) and at>=SCAN_RANGES[module][0][0]-6:
            row['kind'] = 'form_wait_or_program_tail'
            if op==16:row['target']=at+arg
        else:
            raise ValueError(('Unclassified remaining record',module,row))
        rows.append(row)
    return dict(module=module,total=len(code),missing=len(missing),linked=len(linked),
                root_suffix=list(ROOT_SUFFIX[module]) if module in ROOT_SUFFIX else None,callbacks=raw['callbacks'],
                remaining=dict(Counter(row['kind'] for row in rows)),records=rows)


def main():
    CANDIDATES.mkdir(exist_ok=True)
    for module in SCAN_RANGES:
        program = (PROJECT/f'programs/{module}.json').read_bytes()
        base = (PROJECT/f'data/battle-{module}.json').read_bytes()
        raw, base_plan = json.loads(program),json.loads(base)
        plan = build_scan(module,raw,base_plan)
        plan.update(source_program_sha256=hashlib.sha256(program).hexdigest(),
                    base_plan_sha256=hashlib.sha256(base).hexdigest())
        audit = inventory(module,raw,base_plan,plan)
        for stem,value in (('battle-scan',plan),('battle-remaining',audit)):
            (CANDIDATES/f'{stem}-{module}.json').write_text(
                json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,audit['linked'],audit['remaining'])


if __name__=='__main__':
    main()
