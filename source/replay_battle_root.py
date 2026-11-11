"""Replay the retained root suffixes using declared, synthetic entry state."""
import json

from export_battle_recovery import CANDIDATES
from export_battle_scan import ROOT_SUFFIX
from replay_battle_control import build_cases
from replay_shared_battle import load, replay


def root_cases(module, base, control):
    start,_,target = ROOT_SUFFIX[module]
    seed = next(case for case in build_cases(module,base,control)
                if case['entry']==start and case['default_found'])
    seed.update(root_slots={'17':3} if module=='01' else {},
                root_observe_slots=list(range(17,52)) if module=='01' else [],
                clock=[2026,1,2,3,4,5],max_body_steps=1200)
    if module=='06':
        return [dict(seed,id=1,label='等待後回到缺失位置',expected_boundary=target)]
    return [
        dict(seed,id=1,label='根流程完成後回到缺失位置',miss_budget={'8863':-1},expected_boundary=target),
        dict(seed,id=2,label='換角守衛持續命中'),
        dict(seed,id=3,label='等待色碼持續未命中',default_found=False),
    ]


def main():
    for module in ROOT_SUFFIX:
        base = load(f'data/battle-{module}.json')
        control = json.loads((CANDIDATES/f'battle-root-{module}.json').read_text('utf8'))
        cases = root_cases(module,base,control)
        for case in cases:
            result = replay(base,case,control)
            boundary = case.get('expected_boundary')
            if boundary is not None:
                assert result['reason']=='missing_original_record' and result['next_record']==boundary
                assert result['call_depth']==0
            else:
                assert result['reason']=='fixture_stop'
            print(module,case['id'],result['reason'],result['next_record'],len(result['records']))
        fixture = dict(cases=cases,ranges=[[r['entry'],r['last']] for r in base['routines']+control['routines']],
                       boundaries=control['boundaries'],synthetic_context=True)
        (CANDIDATES/f'battle-root-{module}-cases.json').write_text(
            json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':
    main()
