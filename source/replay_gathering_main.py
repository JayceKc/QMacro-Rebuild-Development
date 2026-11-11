import json,hashlib,copy
from pathlib import Path
from qmacro_gathering_main import GatheringMainMachine
from qmacro_gathering_walk import VbsNumericOverflow
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'data/gathering-main-suffix.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def replay(plan,case):
    context=copy.deepcopy(case['context']);m=GatheringMainMachine(plan,context.get,case['initial'],case['entry']);records=[];events=[];queries={};reason=None
    for _ in range(15000):
        if m.done:reason=m.reason;break
        if m.pc==596 and m.main_cycles>=case['max_main_cycles']:m.stop();reason='fixture_stop';break
        at=m.pc;records.append(at)
        try:e=m.step()
        except VbsNumericOverflow:
            assert case['expected_overflow'] and at==714;reason='numeric_overflow';break
        events.append(e);kind=e['kind']
        if kind in ('find_color','find_pic','builtin_color'):
            queries[at]=queries.get(at,0)+1;found=queries[at]>case['miss_budget'].get(str(at),0)
            target=m.actions[at].get('out_roles')==['target_x','target_y'] and at in (541,667)
            x,y=(tuple(case['target_point']) if target else (e['rect'][0]+1,e['rect'][1]+2)) if found else (-1,-1)
            ret=(1 if found else 0) if kind=='find_color' else (0 if found else -1) if kind=='find_pic' else x*8192+y if found else -8193
            if case['inverted_return'] and kind!='builtin_color':ret=1 if ret==0 else 0
            m.supply_query(x,y,ret);events.append({'record':at,'kind':'query_reply','x':x,'y':y,'return_value':ret})
        elif kind=='random_int':
            value=case['random_values'][e['role']];m.supply_random(value);events.append({'record':at,'kind':'random_reply','value':value})
    if reason is None:raise AssertionError('Main suffix exceeded bound '+str(case['id'])+' PC '+str(m.pc))
    return {'id':case['id'],'records':records,'events':events,'reason':reason,'next_record':m.pc,'main_cycles':m.main_cycles,
            'query_count':sum(queries.values()),'root_current_is_nothing':len(m.frames)==1,'root_slots':{str(n):m.frames[0]['slots'].get(n) for n in range(12,17)},
            'history':{f'{a}{n}':m.values[f'history_{a}{n}'] for a in ('x','y') for n in range(1,4)}}


def main():
    path=PROJECT/'data/gathering-main-suffix.json';cp=PROJECT/'data/gathering-main-cases.json';p=json.loads(path.read_text());cases=json.loads(cp.read_text())['cases']
    results=[replay(p,c) for c in cases];covered={r for c in results for r in c['records']};root={a['record'] for a in p['root_actions']}
    out={'ok':True,'cases':results,'case_count':len(results),'covered_root_records':sorted(covered&root),'uncovered_root_records':sorted(root-covered),
         'source_plan_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'case_spec_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),
         'owned_source_sha256':{n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('qmacro_gathering_main.py','qmacro_gathering_routines.py','qmacro_fishing.py','qmacro_gathering_walk.py','replay_gathering_main.py')},
         'original_code_executed':False,'game_input_sent':False,'erased_prefix_restored':False,'full_module_restored':False}
    (PROJECT/'verification/gathering-main-owned.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'cases':len(results),'covered_root':len(covered&root),'uncovered_root':sorted(root-covered),'reasons':{r:sum(c['reason']==r for c in results) for r in sorted({c['reason'] for c in results})}}))


if __name__=='__main__':main()
