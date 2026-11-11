"""Translate the closed skill, healing, and navigation families of 01/03/06."""
import copy
import hashlib
import json

from export_cube_routines import PROJECT, translate

CORE_STARTS = {'01': (1820,3291), '03': (966,2268), '06': (1670,3141)}
EXTRA = {
    '01': ((1740,1818,'過門'),(3293,3338,'門前G'),(3340,3477,'退出副本'),(3479,3621,'修理'),
           (3623,3640,'生命找色'),(3642,3836,'找按鈕'),(3838,3973,'找對話'),(3975,4057,'伺服器檢查')),
    '03': ((369,415,'覺醒'),(902,964,'過門'),(2270,2425,'退出副本'),(2427,2444,'生命找色'),
           (2446,2660,'找按鈕'),(2662,2744,'伺服器檢查')),
    '06': ((1590,1668,'過門'),(3143,3188,'門前G'),(3190,3327,'退出副本'),(3329,3437,'修理'),
           (3439,3456,'生命找色'),(3458,3658,'找按鈕'),(3660,3778,'找對話'),(3780,3862,'伺服器檢查')),
}
SKILLS = ('技能組一','技能組二','技能組三','技能組四','Z技能','ZX技能','不用Z','更多Z','半魔','聖騎','傘蘿')
POTION_NAMES = ('F1吃藥一','F1吃藥二','F1吃藥三','F1吃藥四','不吃藥一','不吃藥二','數字1吃藥一','數字1吃藥二','數字1吃藥三','數字1吃藥四')


def build(module, raw):
    low,high = CORE_STARTS[module]
    names = SKILLS + (POTION_NAMES[5:] if module=='03' else POTION_NAMES)
    ends = [at for at in range(low,high+1) if raw['code'][at][0]==13]
    if len(ends)!=len(names) or ends[-1]!=high:
        raise ValueError('Unexpected core routine boundaries')
    ranges = []
    entry = low
    for end,name in zip(ends,names):
        ranges.append((entry,end,name))
        entry = end+2
    ranges.extend(EXTRA[module])
    plan = translate(raw,ranges)
    by = {a['record']:a for a in plan['actions']}
    entries = {a:b for a,b,_ in ranges}
    for a in plan['actions']:
        if a['kind']=='call':
            target = a['target']
            if target not in entries or by[a['record']-1]['kind']!='frame_enter' or by[entries[target]-1]['kind']!='frame_restore_intent':
                raise ValueError(('Unreviewed call frame',a))
    plan.update(module=int(module),name='共同戰鬥與副本子程序',core_routines=len(names),
                original_body_guest_verified=False,full_module_restored=False)
    return plan


def normalized_routine(plan, routine):
    """Remove only provenance and absolute record relocation from comparisons."""
    entries = {r['entry']:r['name'] for r in plan['routines']}
    first,last = routine['entry'],routine['last']
    result = []
    for original in plan['actions']:
        if not first<=original['record']<=last:
            continue
        row = copy.deepcopy(original)
        for key in ('record','location','source_sl','operand'):
            del row[key]
        if 'target' in row:
            row['target'] = entries[row['target']] if row['kind']=='call' else row['target']-first
        result.append(row)
    return result


def main():
    plans = {}
    for module in CORE_STARTS:
        source = PROJECT/f'programs/{module}.json'
        plan = build(module,json.loads(source.read_text('utf8')))
        plan['source_program_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        (PROJECT/f'data/battle-{module}.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        plans[module] = plan
    comparisons = []
    for module,plan in plans.items():
        if module=='01':
            continue
        by_name = {r['name']:r for r in plan['routines']}
        for original in plans['01']['routines']:
            other = by_name.get(original['name'])
            if other:
                exact = normalized_routine(plans['01'],original)==normalized_routine(plan,other)
                comparisons.append(dict(module=module,name=original['name'],first_01=original['entry'],first_other=other['entry'],exact=exact))
    (PROJECT/'data/battle-family-comparison.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':{m:len(p['actions']) for m,p in plans.items()},'exact':sum(row['exact'] for row in comparisons),'comparisons':len(comparisons)}))


if __name__ == '__main__':
    main()
