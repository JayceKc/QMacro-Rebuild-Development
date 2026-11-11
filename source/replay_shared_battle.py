"""Build and replay explicit controlled cases for the battle families."""
import json

from export_shared_battle import CORE_STARTS
from qmacro_battle_retained import RetainedBattleMachine
from qmacro_shared_battle import SharedBattleMachine
from replay_cube_main import PROJECT,load,scalar_names


def build_cases(plan):
    cases = []
    shared = {a['key']:0 for a in plan['actions'] if a['kind'] in ('read_global','write_global')}
    if 'V8186B4D47378756D' in shared:
        shared['V8186B4D47378756D'] = '123456'
    values = {name:0 for name in sorted(set(scalar_names(plan['actions'])))}
    values.update(YC=100,DM_RET=0)

    def add(routine, found, upper=False, overrides=None):
        cases.append(dict(id=len(cases)+1,label=routine['name']+('-hit' if found else '-miss'),entry=routine['entry'],last=routine['last'],
                          shared=shared,values=values,default_found=found,miss_budget={},inverted_return=False,
                          random_upper=upper,return_overrides=overrides or {},max_body_steps=220))

    for routine in plan['routines']:
        add(routine,True)
        add(routine,False,True)
    for routine in plan['routines']:
        comparisons = {str(a['record']):1 for a in plan['actions']
                       if routine['entry']<=a['record']<=routine['last'] and 'return_comparison' in a}
        if comparisons:
            add(routine,True,overrides=comparisons)
    return cases


def replay(plan,spec,control=None):
    shared = dict(spec['shared'])
    read_global = lambda key,at:shared[key]
    if plan['module'] in (9,10):
        machine = RetainedBattleMachine(plan,control,spec['entry'],read_global,spec['values'],
                                        clock=spec.get('clock'),root_slots=spec.get('root_slots'))
    else:
        machine = SharedBattleMachine(plan,spec['entry'],read_global,spec['values'],control=control,
                                      clock=spec.get('clock'),frame_fields=spec.get('frame_fields'),root_slots=spec.get('root_slots'))
    builtin_points = iter(spec['builtin_points']) if 'builtin_points' in spec else None
    records,events,comparisons,alternate_outputs = [],[],[],[]
    for _ in range(spec['max_body_steps']):
        if machine.done:
            break
        event = machine.step()
        at,kind = event['record'],event['kind']
        records.append(at)
        if kind=='capture_clock':
            y,m,d,h,minute,s = spec['clock']
            source = machine.actions[at]['source']
            clock = f'(DateSerial({y},{m},{d}) + TimeSerial({h},{minute},{s}))'
            events.append(dict(kind='source_rewrite',record=at,value=[source,source.replace('NOW',clock)]))
        elif kind=='exit_script' and event['arguments']==[1]:
            events.append(dict(kind='source_rewrite',record=at,value=[
                machine.actions[at]['source'],'Call QMacroRestartRecorder.RequestRestart(1)']))
        events.append(event)
        if kind=='write_global':
            shared[event['key']] = event['value']
        elif kind=='worker_start':
            event['worker_id']=10000+at
            machine.supply_worker_id(event['worker_id'])
        elif kind=='dm_real_mouse_intent':
            machine.supply_dm_return(1)
        elif kind=='capture_intent':
            capture_result = int(spec['default_found'])
            machine.supply_capture_return(capture_result)
            events.append(dict(kind='capture_reply',record=at,dm_ret=capture_result))
        elif kind=='builtin_cursor':
            x,y = machine.supply_cursor(spec['cursor_packed'])
            events.append(dict(kind='cursor_reply',record=at,x=x,y=y))
        elif kind in ('builtin_color','builtin_picture'):
            left,top,right,bottom = event['rect']
            found = spec['default_found'] and str(at) not in spec['miss_budget']
            if builtin_points is not None:
                x,y = next(builtin_points)
            else:
                x,y = (min(left+1,right),min(top+2,bottom)) if found else (-1,-1)
            machine.supply_builtin(x,y)
            events.append(dict(kind='builtin_query_reply',record=at,x=x,y=y,dm_ret=machine.values.get('DM_RET')))
        elif kind in ('find_color','find_pic'):
            l,t,r,b = event['rect']
            found = spec['default_found'] and str(at) not in spec['miss_budget'] and l<r and t<b
            x,y = (min(l+1,r-1),min(t+2,b-1)) if found else (-1,-1)
            ret = (1 if found else 0) if kind=='find_color' else (0 if found else -1)
            ret = spec['return_overrides'].get(str(at),ret)
            result = machine.supply_query(x,y,ret)
            events.append(dict(kind='query_reply',record=at,x=x,y=y,return_value=ret))
            if result is not None:
                comparisons.append(dict(record=at,value=result,dm_ret=machine.values['DM_RET']))
            if 'out_names' in machine.actions[at]:
                alternate_outputs.append(dict(record=at,values=[machine.values.get(n) for n in ('INTX','INTY','INTXX','INTYY')]))
        elif kind=='random_int':
            value = event['lower']+(event['span']-1 if spec['random_upper'] else 0)
            machine.supply_random(value)
            event['supplied'] = value
    return dict(id=spec['id'],records=records,events=events,comparisons=comparisons,final_shared=shared,
                reason=machine.reason or 'fixture_stop',next_record=machine.pc,call_depth=len(machine.returns),
                alternate_outputs=alternate_outputs,return_value=machine.temporary if machine.reason=='routine_return' else None,
                root_values=[machine.root_slots.get(slot) for slot in spec.get('root_observe_slots',())],
                scalar_values=[machine.values.get(name) for name in spec.get('observe_scalars',())])


def main():
    for module in CORE_STARTS:
        plan = load(f'data/battle-{module}.json')
        cases = build_cases(plan)
        results = [replay(plan,c) for c in cases]
        ranges = [[r['entry'],r['last']] for r in plan['routines']]
        (PROJECT/f'data/battle-{module}-cases.json').write_text(json.dumps({'cases':cases,'ranges':ranges,'synthetic_context':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'module':module,'cases':len(cases),'coverage':len({at for r in results for at in r['records']}),
                          'comparison_results':sorted({c['value'] for r in results for c in r['comparisons']})}))


if __name__ == '__main__':
    main()
