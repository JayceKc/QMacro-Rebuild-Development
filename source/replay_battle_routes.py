"""Bounded cases for retained map and character selection subroutines."""
import json

from export_battle_recovery import CANDIDATES
from export_battle_routes import MAP_SCAN_CHECKPOINTS, ROUTE_RANGES
from replay_battle_control import build_cases
from replay_shared_battle import load, replay


ROLE_SELECTED = 'VF0ADACDECCD2BFD14D6A65757378756D'
ROLE_PREVIOUS = 'VF0ADACDECE99BF954D6A65757378756D'
ROLE_PANEL_GUARD = {'01': 8863, '03': 3323}


def route_cases(module, base, control):
    entries = {start for start,_,_ in ROUTE_RANGES[module]}
    if module=='03':
        entries.add(5397)
    seeds = [case for case in build_cases(module,base,control) if case['entry'] in entries]
    cases = [dict(case,max_body_steps=480) for case in seeds]
    for case in seeds:
        if not case['default_found'] or case['worker_wrapper']:
            continue
        label = case['label']
        if label=='換角色-hit':
            cases.extend(dict(case,label=f'換角色-{role+1}',max_body_steps=580,
                              miss_budget={str(ROLE_PANEL_GUARD[module]):-1},
                              values=case['values']|{ROLE_SELECTED:role,ROLE_PREVIOUS:29})
                         for role in range(30))
        elif label=='圖二-hit':
            checkpoint,_ = MAP_SCAN_CHECKPOINTS[module]
            cases.append(dict(case,label='圖二-略過掃描後獨立測試-命中',entry=checkpoint,max_body_steps=560))
            cases.append(dict(case,label='圖二-略過掃描後獨立測試-未命中',entry=checkpoint,
                              max_body_steps=560,default_found=False))
            queries = [a for a in control['actions'] if checkpoint<=a['record']<=case['last']
                       and a['kind'] in ('builtin_color','builtin_picture','find_color','find_pic')]
            for target in (a for a in queries if a.get('out_names') in (
                    ['INTX16','INTY16'],['INTX12','INTY12'],['INTX122','INTY122'])
                    or (a['kind']=='builtin_color' and a['record']==checkpoint+200)):
                at = target['record']
                prerequisite = at-12 if target.get('out_names')==['INTX122','INTY122'] else at-4
                prerequisites = {prerequisite,at}
                blocked = {str(a['record']):-1 for a in queries if a['record']<at and a['record'] not in prerequisites}
                for hit in (True,False):
                    misses = blocked if hit else blocked|{str(at):-1}
                    cases.append(dict(case,label=f'圖二-獨立座標-L{at}-{hit}',entry=checkpoint,
                                      miss_budget=misses,max_body_steps=560))
    for i,case in enumerate(cases,1):
        case['id'] = i
        case['clock'] = [2026,1,2,3,4,5]
    return cases


def main():
    for module,ranges in ROUTE_RANGES.items():
        base = load(f'data/battle-{module}.json')
        control = json.loads((CANDIDATES/f'battle-routes-{module}.json').read_text('utf8'))
        cases = route_cases(module,base,control)
        results = [replay(base,case,control) for case in cases]
        fixture = dict(cases=cases,ranges=[[r['entry'],r['last']] for r in base['routines']+control['routines']],
                       boundaries=control['boundaries'],synthetic_context=True)
        (CANDIDATES/f'battle-routes-{module}-cases.json').write_text(
            json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        selected = {at for lo,hi,_ in ranges for at in range(lo,hi+1)}
        observed = {at for result in results for at in result['records']} & selected
        builtin = {event['record'] for result in results for event in result['events']
                   if event['kind']=='builtin_query_reply'} & selected
        expected_builtins = {a['record'] for a in control['actions'] if a['record'] in selected
                             and a['kind'] in ('builtin_color','builtin_picture')}
        assert expected_builtins == builtin, (module, expected_builtins-builtin)
        print(module,len(cases),len(observed),sorted(builtin))


if __name__=='__main__':
    main()
