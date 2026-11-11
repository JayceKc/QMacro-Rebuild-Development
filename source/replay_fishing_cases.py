"""Owned bounded driver. All backend replies are explicit synthetic test data."""
import copy
from qmacro_fishing import FishingMachine


def replay(plan,case,bound=5000):
    context=copy.deepcopy(case['context']);m=FishingMachine(plan,lambda role:context.get(role),case['entry'])
    events=[];queries={};records=[]
    for _ in range(bound):
        if m.done:return {'id':case['id'],'records':records,'events':events,'reason':m.reason,
                          'frame_depth':len(m.frames),'last_return':m.last_return,'query_count':sum(queries.values())}
        context.update(case.get('updates',{}).get(str(m.pc),{}));records.append(m.pc)
        event=m.step();events.append(event);kind=event['kind']
        if kind in ('find_color','find_pic'):
            record=event['record'];queries[record]=queries.get(record,0)+1
            found=not(record==case['first_failed_record'] and queries[record]==1)
            x,y=(event['rect'][0]+1,event['rect'][1]+2) if found else (-1,-1)
            ret=(1 if found else 0) if kind=='find_color' else (0 if found else -1)
            if case['inverted_return']:ret=1 if ret==0 else 0
            m.supply_query(x,y,ret)
            events.append({'kind':'query_reply','record':record,'x':x,'y':y,'return_value':ret})
        elif kind=='random_int':
            value=case[event['role']];m.supply_random(value);events.append({'kind':'random_reply','record':event['record'],'value':value})
    raise AssertionError('Owned fishing case exceeded instruction bound: '+str(case['id']))


def main():
    from pathlib import Path
    import json,hashlib
    root=Path(__file__).resolve().parents[1]
    project=root if (root/'data/fishing-routines.json').exists() else root/'outputs/QMacro-Rebuild-Development'
    plan_path=project/'data/fishing-routines.json';cases_path=project/'data/fishing-cases.json'
    plan=json.loads(plan_path.read_text(encoding='utf8'));cases=json.loads(cases_path.read_text(encoding='utf8'))['cases']
    results=[replay(plan,c) for c in cases];covered={r for result in results for r in result['records']}
    report={'ok':True,'case_count':len(results),'cases':results,'covered_records':sorted(covered),
            'uncovered_records':sorted({a['record'] for a in plan['actions']}-covered),
            'source_plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),
            'case_spec_sha256':hashlib.sha256(cases_path.read_bytes()).hexdigest(),
            'owned_source_sha256':{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ('qmacro_fishing.py','replay_fishing_cases.py')},
            'original_code_executed':False,'original_body_guest_replay_verified':bool(plan.get('original_body_guest_replay_verified')),
            'game_input_sent':False,'original_rng_equivalent':False,'full_module_restored':False}
    (project/'verification/fishing-owned-replay.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(results),'events':sum(len(c['events']) for c in results),'covered_records':len(covered),'uncovered_records':report['uncovered_records']}))


if __name__=='__main__':main()
