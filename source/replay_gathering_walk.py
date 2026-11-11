import json,hashlib
from pathlib import Path
from qmacro_gathering_walk import GatheringWalkMachine,VbsNumericOverflow
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'data/gathering-walk.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def replay(plan,case):
    m=GatheringWalkMachine(plan,case['context']);records=[];events=[];reason=None
    for _ in range(600):
        if m.done:reason='routine_return';break
        records.append(m.pc)
        try:e=m.step()
        except VbsNumericOverflow:
            assert case['expected_error'] and m.pc==714;reason='numeric_overflow';break
        events.append(e)
        if e['kind']=='random_int':m.supply_random(case['random_x' if e['name']=='X' else 'random_y'])
    assert reason and (reason=='numeric_overflow')==case['expected_error']
    return {'id':case['id'],'records':records,'events':events,'reason':reason,'angle':m.values[m.angle_name],
            'angle_is_empty':m.values[m.angle_name] is None}


def main():
    plan_path=PROJECT/'data/gathering-walk.json';case_path=PROJECT/'data/gathering-walk-cases.json'
    plan=json.loads(plan_path.read_text(encoding='utf8'));spec=json.loads(case_path.read_text(encoding='utf8'))
    cases=[replay(plan,c) for c in spec['cases']]
    report={'ok':True,'cases':cases,'case_count':len(cases),'source_plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),
            'case_spec_sha256':hashlib.sha256(case_path.read_bytes()).hexdigest(),
            'owned_source_sha256':{n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('qmacro_gathering_walk.py','replay_gathering_walk.py')},
            'original_code_executed':False,'game_input_sent':False,'full_module_restored':False}
    (PROJECT/'verification/gathering-walk-owned.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases),'numeric_overflow':sum(c['reason']=='numeric_overflow' for c in cases),
                      'records_covered':len({r for c in cases for r in c['records']})}))


if __name__=='__main__':main()
