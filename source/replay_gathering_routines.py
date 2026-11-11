import json,hashlib,copy
from pathlib import Path
from qmacro_gathering_routines import GatheringRoutinesMachine
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/gathering-routines.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def replay(plan,case):
    context=copy.deepcopy(case['context']);m=GatheringRoutinesMachine(plan,lambda role:context.get(role),case['entry'])
    records=[];events=[];queries={}
    for _ in range(8000):
        if m.done:return {'id':case['id'],'records':records,'events':events,'reason':m.reason,'frame_depth':len(m.frames),'last_return':m.last_return,'query_count':sum(queries.values())}
        context.update(case['updates'].get(str(m.pc),{}));records.append(m.pc);e=m.step();events.append(e);kind=e['kind']
        if kind in ('find_color','find_pic','builtin_color'):
            at=e['record'];queries[at]=queries.get(at,0)+1;found=queries[at]>case['miss_budget'].get(str(at),0)
            x,y=(e['rect'][0]+1,e['rect'][1]+2) if found else (-1,-1)
            ret=(1 if found else 0) if kind=='find_color' else (0 if found else -1) if kind=='find_pic' else x*8192+y if found else -8193
            if case['inverted_return'] and kind!='builtin_color':ret=1 if ret==0 else 0
            m.supply_query(x,y,ret);events.append({'record':at,'kind':'query_reply','x':x,'y':y,'return_value':ret})
        elif kind=='random_int':
            value=case[e['role']];m.supply_random(value);events.append({'record':e['record'],'kind':'random_reply','value':value})
    raise AssertionError('Gathering case '+str(case['id'])+' bound exceeded, last PC '+str(m.pc))


def main():
    p=PROJECT/'data/gathering-routines.json';c=PROJECT/'data/gathering-cases.json';plan=json.loads(p.read_text());spec=json.loads(c.read_text())
    cases=[replay(plan,s) for s in spec['cases']];covered={r for c in cases for r in c['records']}
    result={'ok':True,'cases':cases,'case_count':len(cases),'covered_records':sorted(covered),'uncovered_records':sorted({a['record'] for a in plan['actions']}-covered),
            'source_plan_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'case_spec_sha256':hashlib.sha256(c.read_bytes()).hexdigest(),
            'owned_source_sha256':{n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('qmacro_gathering_routines.py','qmacro_fishing.py','qmacro_gathering_walk.py','replay_gathering_routines.py')},
            'original_code_executed':False,'game_input_sent':False,'full_module_restored':False}
    (PROJECT/'verification/gathering-routines-owned.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'cases':len(cases),'covered_records':len(covered),'uncovered_records':result['uncovered_records']}))


if __name__=='__main__':main()
