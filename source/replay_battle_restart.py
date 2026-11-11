"""Exercise every preserved restart branch with a fixed local clock."""
import json

from export_battle_recovery import CANDIDATES
from export_battle_restart import RESTART_RANGES
from replay_battle_control import build_cases
from replay_shared_battle import load, replay


def restart_cases(module, base, control):
    entry, last, _ = RESTART_RANGES[module][0]
    seed = next(c for c in build_cases(module,base,control) if c['entry']==entry and c['default_found'])
    queries = [a['record'] for a in control['actions']
               if entry<=a['record']<=last and a['kind']=='builtin_color']
    cases = []
    for clock in ([2026,1,2,3,4,5], [2026,11,9,16,20,33]):
        for misses in range(len(queries)+1):
            cases.append(dict(seed,id=len(cases)+1,label=f'重新啟動-未命中{misses}次-{clock[1]}月',
                              clock=clock,miss_budget={str(at):-1 for at in queries[:misses]}))
    return cases


def main():
    for module in RESTART_RANGES:
        control = json.loads((CANDIDATES/f'battle-restart-{module}.json').read_text('utf8'))
        base = load(f'data/battle-{module}.json')
        cases = restart_cases(module,base,control)
        for case in cases:
            result = replay(base,case,control)
            assert result['reason']=='restart_requested'
            captures = [event['arguments'] for event in result['events'] if event['kind']=='screenshot_intent']
            timestamp = ''.join(map(str,case['clock']))
            assert captures == [[0,0,1920,1080,'C:\\方舟混沌\\'+timestamp+'.bmp']]
            assert sum(e['kind']=='key_press' and e['arguments'][0]=='Esc' for e in result['events']) == (
                len(case['miss_budget'])==sum(e['kind']=='builtin_query_reply' for e in result['events']))
        fixture = dict(cases=cases,ranges=[[r['entry'],r['last']] for r in base['routines']+control['routines']],
                       boundaries=control['boundaries'],synthetic_context=True)
        (CANDIDATES/f'battle-restart-{module}-cases.json').write_text(
            json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,len(cases))


if __name__=='__main__':
    main()
