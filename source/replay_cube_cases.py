"""Replay cube fixtures with owned events only; does not run original source."""
import copy,hashlib,json
from pathlib import Path
from export_cube_routines import PROJECT
from qmacro_cube import CubeMachine,CubeDependencyMissing


def replay(plan,spec):
    shared=copy.deepcopy(spec['shared']);seen={};events=[];records=[];access=[]
    def read(key,pc):
        if key not in shared:raise CubeDependencyMissing('Missing fixture global '+key)
        access.append({'record':pc,'kind':'read_global','key':key,'value':shared[key]});return shared[key]
    m=CubeMachine(plan,spec['entry'],read,spec['values'],{int(k):v for k,v in spec['frame_slots'].items()})
    for _ in range(spec['max_body_steps']):
        if m.done:break
        for key,value in spec['updates'].get(str(m.pc),{}).items():shared[key]=value
        records.append(m.pc);e=m.step();events.append(e);k=e['kind']
        if k=='write_global':
            shared[e['key']]=e['value'];access.append({a:e[a] for a in ('record','kind','key','value')})
        if k in ('find_color','find_pic'):
            at=e['record'];seen[at]=seen.get(at,0)+1;budget=spec['miss_budget'].get(str(at))
            found=spec['default_found'] if budget is None else budget>=0 and seen[at]>budget
            x,y=(e['rect'][0]+1,e['rect'][1]+2) if found else (-1,-1)
            ret=(1 if found else 0) if k=='find_color' else (0 if found else -1)
            if spec['inverted_return']:ret=1 if ret==0 else 0
            m.supply_query(x,y,ret);events.append({'kind':'query_reply','record':at,'x':x,'y':y,'return_value':ret})
        if k=='random_int':m.supply_random(e['lower']+(e['span']-1 if spec['random_upper'] else 0))
    return {'id':spec['id'],'records':records,'events':events,'reason':m.reason or 'fixture_stop','next_record':m.pc,
            'query_count':sum(seen.values()),'shared_accesses':access,'final_shared':shared,'frame_restore_requested':m.frame_restore_requested}


def main():
    planpath=PROJECT/'data/cube-routines.json';casepath=PROJECT/'data/cube-cases.json'
    p=json.loads(planpath.read_text('utf8'));cases=json.loads(casepath.read_text('utf8'))['cases']
    result={'ok':True,'cases':[replay(p,c) for c in cases],'case_spec_sha256':hashlib.sha256(casepath.read_bytes()).hexdigest(),
            'source_program_sha256':p['source_program_sha256'],'source_plan_sha256':hashlib.sha256(planpath.read_bytes()).hexdigest(),
            'owned_source_sha256':{n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('qmacro_cube.py','qmacro_gathering_walk.py','replay_cube_cases.py')},
            'original_code_executed':False,'game_input_sent':False,'full_module_restored':False}
    (PROJECT/'verification/cube-owned.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases),'records_covered':len({r for c in result['cases'] for r in c['records']}),'reasons':{r:sum(c['reason']==r for c in result['cases']) for r in {c['reason'] for c in result['cases']}}}))


if __name__=='__main__':main()
