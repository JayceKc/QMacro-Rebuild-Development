"""Controlled paths for each retained 09/10 routine and all five island workers."""
import json

from export_battle_recovery import CANDIDATES
from replay_shared_battle import build_cases, replay


ISLAND_MODE = 'VF1D6A1A9B9B5C2A84D6A65757378756D'
POTION_SWITCHES = ('VFEBEB7DC3549C9914D6A65757378756D','VFEBEB7DC42C4896D')


def empty_base(module):
    return dict(module=int(module),actions=[],routines=[])


def cases_for(module, plan):
    cases = [dict(case,worker_wrapper=False,cursor_packed=314*8192+256,max_body_steps=350)
             for case in build_cases(plan)]
    if module=='09':
        seed = next(c for c in cases if c['entry']==936 and c['default_found'])
        cases.extend(dict(seed,label=f'第一次戰鬥-模式{mode}',values=seed['values']|{ISLAND_MODE:mode})
                     for mode in range(1,6))
        cases.extend(dict(seed,label=f'工作入口-L{w["worker_entry"]}',entry=w['worker_entry'],
                          last=w['worker_entry']+2,worker_wrapper=True) for w in plan['worker_wrappers'])
    else:
        for seed in list(cases):
            if seed['label'].startswith('吃藥門檻') and not seed['default_found']:
                for switches in ((1,0),(0,1),(1,1)):
                    cases.append(dict(seed,label=f'{seed["label"]}-{switches[0]}{switches[1]}',
                                      shared=seed['shared']|dict(zip(POTION_SWITCHES,switches))))
        seed = next(c for c in cases if c['entry']==1551 and c['default_found'])
        cases.append(dict(seed,label='死亡與復活-第二組游標',cursor_packed=1820*8192+950))
    for i,case in enumerate(cases,1):
        case['id'] = i
        if module=='09' and case['entry']==936:
            case['observe_scalars'] = sorted({w['local_id_name'] for w in plan['worker_wrappers']})
    return cases


def main():
    for module in ('09','10'):
        plan = json.loads((CANDIDATES/f'skill-island-retained-{module}.json').read_text('utf8'))
        cases = cases_for(module,plan)
        results = [replay(empty_base(module),case,plan) for case in cases]
        fixture = dict(cases=cases,ranges=[[r['entry'],r['last']] for r in plan['routines']],
                       boundaries=plan['boundaries'],synthetic_context=True)
        (CANDIDATES/f'battle-small-{module}-cases.json').write_text(
            json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        starts = sorted({e['record'] for r in results for e in r['events'] if e['kind']=='worker_start'})
        assert starts==[w['start_record'] for w in plan['worker_wrappers']]
        cursors = {(e['x'],e['y']) for r in results for e in r['events'] if e['kind']=='cursor_reply'}
        print(module,len(cases),len({at for r in results for at in r['records']}),starts,sorted(cursors))


if __name__=='__main__':
    main()
