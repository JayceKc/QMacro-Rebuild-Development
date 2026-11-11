"""Compare original Form1 wait and tail records with a closed control-flow replay."""
import hashlib
import json

from export_battle_recovery import CANDIDATES
from export_cube_routines import PROJECT
from qmacro_battle_retained import RetainedBattleMachine
from replay_shared_battle import load


def replay_tail(base, control, entry, continue_iteration, wait_then_close):
    machine = RetainedBattleMachine(base,control,entry,lambda key,at:None,{},
                                    message_ready=not wait_then_close,ui_open=wait_then_close,
                                    continue_iteration=continue_iteration)
    states = observe_tail(machine)
    expected = ('Finished',control['total_records']) if continue_iteration else ('IterationEnded',control['form_gate']+2)
    assert (states[-1]['state'],machine.pc)==expected
    return states


def observe_tail(machine):
    states = []
    for _ in range(12):
        event = machine.step()
        state = {'program_end':'Finished','iteration_end':'IterationEnded','waiting_message':'WaitingForMessage',
                 'waiting_ui':'WaitingForUi'}.get(event['kind'],'Ready')
        states.append(dict(record=event['record'],next=machine.pc,state=state,depth=len(machine.returns)))
        if state=='WaitingForMessage':
            machine.message_ready = True
        if state=='WaitingForUi':
            machine.ui_open = False
        if machine.done:
            break
    return states


def replay_default(base, control):
    machine = RetainedBattleMachine(base,control,0,lambda key,at:None,{})
    records = []
    for _ in range(130):
        event = machine.step()
        records.append(event['record'])
        assert event['kind'] in ('declaration','entry_dispatch','missing_original_record')
        if machine.done:
            break
    assert machine.reason=='missing_original_record'
    return dict(records=records,missing_record=machine.pc,call_depth=len(machine.returns))


def replay_callback(base, control, original):
    machine = RetainedBattleMachine(base,control,original['pump_record'],lambda key,at:None,{})
    assert machine.step()['kind']=='waiting_ui'
    requested, notices, counts = [], [], []
    loads = 0
    for expected in original['observations']:
        machine.queue_ui_event('CLICK.FORM1.BUTTON1')
        assert machine.step()['target']==original['entry']
        for _ in range(20):
            event = machine.step()
            kind = event['kind']
            if kind=='delete_folder_intent':
                requested.append(event['path'])
            elif kind=='message_notify':
                notices.append(dict(Record=event['record'],Kind=kind,Value=[event['level'],event['message']]))
            elif kind=='load_service_intent':
                loads += 1
            if machine.pc==original['pump_record']:
                break
        actual = dict(delete_intents=len(requested),return_pc=machine.pc,frame_restored=not machine.frames)
        assert actual==expected and not machine.returns
        assert machine.step()['kind']=='waiting_ui'
        counts.append(len(requested))
    assert requested==original['delete_intents'] and loads==original['owned_library_loads']==1
    assert notices==[{k:v for k,v in e.items() if k!='Module'} for e in original['events']]
    return dict(clicks=len(counts),delete_intents=len(requested),file_loads=loads)


def compare(original, callback, plans):
    assert original['ok'] and not original['original_native_loaded'] and not original['game_input_sent']
    assert {row['module'] for row in original['modules']}=={'01','03','06'} and len(original['modules'])==3
    assert callback['ok'] and callback['filesystem_deletions']==0
    observed = 0
    default_boundaries = {}
    for row in original['modules']:
        module = row['module']
        base,control = plans[module]
        assert row['source_program_sha256']==base['source_program_sha256']==control['source_program_sha256']
        gate = control['form_gate']
        default = replay_default(base,control)
        assert default==row['default_entry']
        default_boundaries[module] = default['missing_record']
        modes = ((gate,False,True),(gate,True,True),(gate-1,True,False))
        assert len(row['cases'])==len(modes)
        for original_case,(entry,continues,wait_then_close) in zip(row['cases'],modes):
            assert (original_case['entry'],original_case['continue_iteration'],original_case['wait_then_close'])==(
                entry,continues,wait_then_close)
            expected = replay_tail(base,control,entry,continues,wait_then_close)
            assert expected==original_case['observations'], (module,entry,expected,original_case['observations'])
            observed += len(expected)
    callback_result = replay_callback(*plans['06'],next(c for c in callback['callbacks'] if c['module']==6))
    return dict(ok=True,modules=3,form_cases=9,observed_steps=observed,default_entry_boundaries=default_boundaries,
                callback=callback_result,real_ui_created=False,full_program_restored=False)


def main():
    original_path = CANDIDATES/'original-battle-form.json'
    if not original_path.exists():
        original_path = PROJECT/'verification/original-battle-form.json'
    callback_path = PROJECT/'verification/original-callback-vm-test.json'
    original = json.loads(original_path.read_text('utf8'))
    assert original['runtime_sha256']==hashlib.sha256((PROJECT/'bin/QMacro.Rebuild.Runtime.dll').read_bytes()).hexdigest()
    plans = {}
    for module in ('01','03','06'):
        name = f'battle-retained-{module}.json'
        plan_path = CANDIDATES/name
        if not plan_path.exists():
            plan_path = PROJECT/'data'/name
        control = json.loads(plan_path.read_text('utf8'))
        assert control['source_program_sha256']==hashlib.sha256((PROJECT/f'programs/{module}.json').read_bytes()).hexdigest()
        plans[module] = (load(f'data/battle-{module}.json'),control)
    CANDIDATES.mkdir(exist_ok=True)
    report = compare(original,json.loads(callback_path.read_text('utf8')),plans)
    report.update(original_guest_sha256=hashlib.sha256(original_path.read_bytes()).hexdigest(),
                  original_callback_sha256=hashlib.sha256(callback_path.read_bytes()).hexdigest())
    (CANDIDATES/'battle-form-original-vs-rebuild.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))


if __name__=='__main__':
    main()
