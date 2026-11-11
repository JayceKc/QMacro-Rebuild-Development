"""Compare the 05 root suffix, default dispatch and Form1 with controlled guest observations."""
import hashlib
import json

from compare_battle_form import observe_tail
from compare_original_fishing_vm import owned_events
from export_fishing_routines import PROJECT
from qmacro_fishing_retained import FishingRetainedMachine


CASES = ((2,0,True,False,115),(4,1,True,True,115),(0,1,False,True,501),(4,0,False,False,519))
CONTEXT = {'saved_cursor_x':314,'saved_cursor_y':256,'simulation_mode':0}


def replay_suffix(routines, plan, count, rebait, found, inverted):
    machine = FishingRetainedMachine(routines,plan,CONTEXT.get,504,
                                     initial={'failure_count':count,'rebait':rebait,'cycle_count':13})
    records, events = [], []
    queries = 0
    for _ in range(40):
        event = machine.step()
        records.append(event['record'])
        events.append(event)
        if event['kind']=='find_color':
            queries += 1
            x,y = (event['rect'][0]+1,event['rect'][1]+2) if found else (-1,-1)
            result = int(found!=inverted)
            machine.supply_query(x,y,result)
            events.append(dict(kind='query_reply',record=event['record'],x=x,y=y,return_value=result))
        if machine.done:
            break
    assert machine.done
    return dict(records=records,events=events,reason=machine.reason,next_record=machine.pc,
                final_failure_count=machine.values['failure_count'],final_cycle_count=machine.values['cycle_count'],
                query_count=queries)


def compare(original, routines, plan):
    assert original['ok'] and not any(original[k] for k in ('original_native_loaded','game_input_sent','os_exit_called'))
    assert original['source_program_sha256']==plan['source_program_sha256']==routines['source_program_sha256']
    default = FishingRetainedMachine(routines,plan,CONTEXT.get)
    startup = [default.step()['record'] for _ in range(5)]
    assert default.reason=='missing_original_record' and default.pc==4
    assert original['default_entry']==dict(records=startup,missing_record=4,call_depth=0)
    observed, covered, effects = [], set(), 0
    assert len(original['cases'])==len(CASES)
    for i,(native,(count,rebait,found,inverted,stop)) in enumerate(zip(original['cases'],CASES),1):
        assert (native['id'],native['failure_count'],native['rebait'],native['found'],native['inverted'])==(
            i,count,rebait,found,inverted)
        model = replay_suffix(routines,plan,count,rebait,found,inverted)
        assert model['next_record']==stop
        for key in ('records','reason','next_record','final_failure_count','final_cycle_count','query_count'):
            assert native[key]==model[key],(i,key,native[key],model[key])
        actual = [dict(record=e['Record'],kind=e['Kind'],value=e['Value']) for e in native['events']]
        assert actual==owned_events(model),(i,actual,owned_events(model))
        observed.append(dict(case=i,next_record=stop,reason=model['reason'],event_count=len(actual)))
        covered.update(at for at in native['records'] if 504<=at<=539)
        effects += len(actual)
    steps = 0
    modes = ((925,False,True),(925,True,True),(924,True,False))
    assert len(original['form'])==len(modes)
    for native,(entry,continues,wait_then_close) in zip(original['form'],modes):
        assert (native['entry'],native['continue_iteration'],native['wait_then_close'])==(entry,continues,wait_then_close)
        machine = FishingRetainedMachine(routines,plan,CONTEXT.get,entry)
        machine.message_ready = not wait_then_close
        machine.ui_open = wait_then_close
        machine.continue_iteration = continues
        states = observe_tail(machine)
        assert states==native['observations']
        steps += len(states)
    return dict(ok=True,suffix_cases=len(CASES),suffix_events=effects,suffix_observed_records=sorted(covered),paths=observed,
                form_cases=len(modes),form_steps=steps,default_boundary=4,full_module_restored=False)


def main():
    evidence = PROJECT/'verification'
    original_path = evidence/'original-fishing-suffix.json'
    original = json.loads(original_path.read_text('utf8'))
    assert original['runtime_sha256']==hashlib.sha256((PROJECT/'bin/QMacro.Rebuild.Runtime.dll').read_bytes()).hexdigest()
    routine_path = PROJECT/'data/fishing-routines.json'
    plan_path = PROJECT/'data/fishing-retained.json'
    routine,plan = (json.loads(path.read_text('utf8')) for path in (routine_path,plan_path))
    assert plan['routine_plan_sha256']==hashlib.sha256(routine_path.read_bytes()).hexdigest()
    assert plan['source_program_sha256']==hashlib.sha256((PROJECT/'programs/05.json').read_bytes()).hexdigest()
    report = compare(original,routine,plan)
    report.update(original_guest_sha256=hashlib.sha256(original_path.read_bytes()).hexdigest(),
                  retained_plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest())
    (evidence/'fishing-suffix-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
