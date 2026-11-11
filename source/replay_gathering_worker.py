import json,hashlib
from pathlib import Path
from qmacro_gathering_worker import GatheringGWorker
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/gathering-worker.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def replay(plan,case):
    holder={};records=[];events=[]
    def context(role):
        return case['simulation_mode'] if role=='simulation_mode' else case['sdk_markers'][holder['m'].loops%len(case['sdk_markers'])]
    m=holder['m']=GatheringGWorker(plan,context)
    for _ in range(600):
        if m.pc==case['stop_before_record'] or m.loops>=case['iterations']:break
        records.append(m.pc);e=m.step();events.append(e)
        if e['kind'] in ('find_color','find_pic'):
            x=case['color_result' if e['kind']=='find_color' else 'picture_result'];y=-1 if x<0 else e['arguments'][1]+1
            ret=(1 if x>=0 else 0) if e['kind']=='find_color' else (0 if x>=0 else -1)
            if case['invert_return']:ret=1 if ret==0 else 0
            m.supply_query(x,y,ret);e.update(x=x,y=y,return_value=ret)
    else:raise ValueError('Worker replay bound exceeded')
    at=m.pc;m.stop()
    return {'id':case['id'],'records':records,'events':events,'next_record':at,'loops':m.loops,'reason':'fixture_stop'}


def main():
    p=PROJECT/'data/gathering-worker.json';c=PROJECT/'data/gathering-worker-cases.json'
    plan=json.loads(p.read_text());spec=json.loads(c.read_text());cases=[replay(plan,s) for s in spec['cases']]
    result={'ok':True,'cases':cases,'case_count':len(cases),'source_plan_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'case_spec_sha256':hashlib.sha256(c.read_bytes()).hexdigest(),
            'owned_source_sha256':{n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('qmacro_gathering_worker.py','replay_gathering_worker.py')},
            'original_code_executed':False,'game_input_sent':False,'full_module_restored':False}
    (PROJECT/'verification/gathering-worker-owned.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'cases':len(cases),'covered':len({r for c in cases for r in c['records']})}))


if __name__=='__main__':main()
