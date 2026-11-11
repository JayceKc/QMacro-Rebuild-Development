"""Compare the retained 08 host paths against isolated original-record observations."""
import hashlib
import json

from compare_battle_form import observe_tail
from export_cube_routines import PROJECT
from qmacro_gathering_retained import GatheringHostMachine


def compare(original, plan):
    assert original['ok'] and not any(original[k] for k in ('original_native_loaded','game_input_sent','real_ui_created'))
    assert original['source_program_sha256']==plan['source_program_sha256']
    default = GatheringHostMachine(plan,0)
    startup = [default.step()['record'] for _ in range(8)]
    assert default.reason=='missing_original_record' and default.pc==7
    assert original['default_entry']==dict(records=startup,missing_record=7,call_depth=0)
    modes = ((1622,False,True),(1622,True,True),(1621,True,False))
    steps = 0
    assert len(original['form'])==len(modes)
    for native,(entry,continues,wait_then_close) in zip(original['form'],modes):
        assert (native['entry'],native['continue_iteration'],native['wait_then_close'])==(entry,continues,wait_then_close)
        model = GatheringHostMachine(plan,entry)
        model.message_ready = not wait_then_close
        model.ui_open = wait_then_close
        model.continue_iteration = continues
        states = observe_tail(model)
        assert states==native['observations'], (entry,states,native['observations'])
        assert model.reason==('program_end' if continues else 'iteration_end')
        steps += len(states)
    return dict(ok=True,default_boundary=7,form_cases=len(modes),form_steps=steps,retained_records=plan['retained_records'],
                original_missing=len(plan['missing_records']),full_module_restored=False)


def main():
    evidence = PROJECT/'verification'
    original_path = evidence/'original-gathering-host.json'
    plan_path = PROJECT/'data/gathering-retained.json'
    original,plan = (json.loads(path.read_text('utf8')) for path in (original_path,plan_path))
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    assert original['runtime_sha256']==digest(PROJECT/'bin/QMacro.Rebuild.Runtime.dll')
    assert plan['source_program_sha256']==digest(PROJECT/'programs/08.json')
    assert plan['main_plan_sha256']==digest(PROJECT/'data/gathering-main-suffix.json')
    assert plan['worker_plan_sha256']==digest(PROJECT/'data/gathering-worker.json')
    report = compare(original,plan)
    report.update(original_guest_sha256=digest(original_path),retained_plan_sha256=digest(plan_path))
    (evidence/'gathering-host-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
