"""Check misses, row advance and filtered off-row matches in retained FindPic counting."""
import json

from export_battle_recovery import CANDIDATES
from export_battle_scan import SCAN_RANGES
from replay_shared_battle import load, replay


FRAME_INPUTS = {
    'V9A99B28DC292756D': 100, 'V84A5B28DC292756D': 20,
    'V9EB8B28DC292756D': 110, 'V82A8B28DC292756D': 30,
    'V80D6A3D9B1CFCBDB4D6A65757378756D': 'fixture.bmp',
    'V828AAEB3C5B0756D': .8,
}
MISS = (-1,-1)
SCANS = (
    ('空畫面', (MISS,), 0),
    ('換列後繼續', ((101,20),(105,20),MISS,(104,22),MISS,MISS), 3),
    ('略過同列限制外的結果', ((101,20),(104,21),(104,21),MISS,MISS), 2),
)


def main():
    for module,((entry,last,_),) in SCAN_RANGES.items():
        base = load(f'data/battle-{module}.json')
        control = json.loads((CANDIDATES/f'battle-scan-{module}.json').read_text('utf8'))
        cases = [dict(id=i,label=label,entry=entry,last=last,frame_fields=FRAME_INPUTS,worker_wrapper=False,
                      expected_count=count,builtin_points=points,shared={},values={'DM_RET':7},
                      default_found=True,miss_budget={},return_overrides={},random_upper=False,max_body_steps=140)
                 for i,(label,points,count) in enumerate(SCANS,1)]
        for case in cases:
            observed = replay(base,case,control)
            assert observed['reason']=='routine_return' and observed['return_value']==case['expected_count']
            assert len([e for e in observed['events'] if e['kind']=='builtin_query_reply'])==len(case['builtin_points'])
        fixture = dict(cases=cases,ranges=[[entry,last]],boundaries={},synthetic_context=True)
        (CANDIDATES/f'battle-scan-{module}-cases.json').write_text(
            json.dumps(fixture,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,len(cases),[case['expected_count'] for case in cases])


if __name__=='__main__':
    main()
