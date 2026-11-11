"""Bounded cases for callable instance entry, item bars and capture routines."""
import json

from export_battle_recovery import CANDIDATES
from export_battle_tail import ENTRY_VERSION, ENTRY_VERSION_CHECKPOINTS, TAIL_RANGES
from replay_battle_control import build_cases
from replay_shared_battle import load, replay


ITEM_BAR = 'VF8AADBAAB3C0756D'


def tail_cases(module, base, control):
    entries = {start for start,_,_ in TAIL_RANGES[module]}
    if module=='06':
        entries.add(843)
    seeds = [case for case in build_cases(module,base,control) if case['entry'] in entries]
    cases = [dict(case,max_body_steps=550) for case in seeds]
    for seed in seeds:
        if not seed['default_found'] or seed['worker_wrapper']:
            continue
        if seed['label']=='切換道具欄-hit':
            cases.extend(dict(seed,label=f'切換道具欄-{bar}',shared=seed['shared']|{ITEM_BAR:bar})
                         for bar in range(1,5))
        elif seed['label']=='按鈕進本-hit':
            for version in (3,4):
                for upper in (False,True):
                    cases.append(dict(seed,label=f'按鈕進本-版本{version}-座標檢查點-上緣{upper}',
                                      entry=ENTRY_VERSION_CHECKPOINTS[module],
                                      shared=seed['shared']|{ENTRY_VERSION:version},
                                      random_upper=upper,max_body_steps=550))
    for i,case in enumerate(cases,1):
        case.update(id=i,clock=[2026,1,2,3,4,5])
    return cases


def main():
    for module,ranges in TAIL_RANGES.items():
        base = load(f'data/battle-{module}.json')
        control = json.loads((CANDIDATES/f'battle-tail-{module}.json').read_text('utf8'))
        cases = tail_cases(module,base,control)
        results = [replay(base,case,control) for case in cases]
        selected = {at for lo,hi,_ in ranges for at in range(lo,hi+1)}
        captures = {a['record'] for a in control['actions'] if a['record'] in selected and a['kind']=='capture_intent'}
        observed = {at for result in results for at in result['records']} & selected
        if not captures <= observed:
            raise ValueError(('Unobserved skill capture',module,captures-observed))
        entry,last,_ = next(r for r in ranges if r[2]=='按鈕進本')
        first_coordinate_group = [a['record'] for a in control['actions'] if entry<=a['record']<=last
                                  and a['kind']=='random_int'][:4]
        assert set(first_coordinate_group) <= observed, (module, first_coordinate_group)
        fixture = dict(cases=cases,ranges=[[r['entry'],r['last']] for r in base['routines']+control['routines']],
                       boundaries=control['boundaries'],synthetic_context=True)
        (CANDIDATES/f'battle-tail-{module}-cases.json').write_text(
            json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,len(cases),len(observed),len(captures))


if __name__=='__main__':
    main()
