"""Bind retained 09/10 behavior to recorded guest paths and the textbox callback."""
import hashlib
import json

from compare_battle_control import compare as compare_routines
from compare_battle_form import replay_default, replay_tail
from export_battle_recovery import CANDIDATES
from qmacro_battle_retained import RetainedBattleMachine
from replay_shared_battle import PROJECT, load
from replay_skill_island_retained import empty_base


def compare_host(original, callbacks, plans):
    assert original['ok'] and not original['original_native_loaded'] and not original['game_input_sent']
    assert len(original['modules'])==2 and {r['module'] for r in original['modules']}=={'09','10'}
    default, steps = {}, 0
    for row in original['modules']:
        module = row['module']
        base, plan = empty_base(module), plans[module]
        assert plan['source_program_sha256']==row['source_program_sha256']
        expected = replay_default(base,plan)
        assert expected==row['default_entry']
        default[module] = expected['missing_record']
        gate = plan['form_gate']
        modes = ((gate,False,True),(gate,True,True),(gate-1,True,False))
        assert len(row['cases'])==len(modes)
        for native,(entry,continues,wait) in zip(row['cases'],modes):
            assert (native['entry'],native['continue_iteration'],native['wait_then_close'])==(entry,continues,wait)
            result = replay_tail(base,plan,entry,continues,wait)
            assert native['observations']==result
            steps += len(result)
    assert callbacks['ok'] and callbacks['filesystem_deletions']==0
    original_ui = next(c for c in callbacks['callbacks'] if c['module']==10)
    context = RetainedBattleMachine(empty_base('10'),plans['10'],original_ui['pump_record'],lambda k,a:None,{})
    path = 'Form1.InputBox1.Text'
    effects = []
    for native in original_ui['observations']:
        assert context.step()['kind']=='waiting_ui'
        context.ui_values[path] = native['input']
        context.queue_ui_event('CHANGE.FORM1.INPUTBOX1')
        assert context.step()['target']==original_ui['entry']
        for _ in range(8):
            event = context.step()
            if event['kind']=='ui_write':
                effects.append(dict(Kind=event['kind'],Record=event['record'],Value=[event['path'],event['value']]))
        assert context.pc==native['return_pc'] and not context.returns
        assert (not context.frames)==native['frame_restored']
        assert context.ui_values[path]==native['result']
    assert effects==[{k:v for k,v in e.items() if k!='Module'} for e in original_ui['events']]
    return dict(ok=True,default_boundaries=default,form_cases=6,form_steps=steps,callback_cases=len(effects),
                full_module_restored=False)


def read_artifact(name, folder):
    path = CANDIDATES/name
    if not path.exists():
        path = PROJECT/folder/name
    return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_module(module, plan, specs, native):
    report = compare_routines(native,specs['cases'],empty_base(module),plan)
    assert report['worker_start_sites']==[w['start_record'] for w in plan['worker_wrappers']]
    report['cursor_positions'] = sorted({(r['x'],r['y']) for case in native['cases'] for r in case['cursor_replies']})
    return report


def main():
    runtime = digest(PROJECT/'bin/QMacro.Rebuild.Runtime.dll')
    plans = {}
    CANDIDATES.mkdir(exist_ok=True)
    for module in ('09','10'):
        plan_path = read_artifact(f'skill-island-retained-{module}.json','data')
        case_path = read_artifact(f'battle-small-{module}-cases.json','data')
        native_path = read_artifact(f'original-battle-small-{module}.json','verification')
        plan, cases, native = (json.loads(p.read_text('utf8')) for p in (plan_path,case_path,native_path))
        assert native['source_program_sha256']==plan['source_program_sha256']==digest(PROJECT/f'programs/{module}.json')
        assert native['runtime_sha256']==runtime and native['case_spec_sha256']==digest(case_path)
        report = compare_module(module,plan,cases,native)
        report.update(original_guest_sha256=digest(native_path),case_spec_sha256=digest(case_path),plan_sha256=digest(plan_path))
        (CANDIDATES/f'skill-island-{module}-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
        print({k:v for k,v in report.items() if k!='covered_records'})
        plans[module] = plan
    host_path = read_artifact('original-skill-island-host.json','verification')
    host = json.loads(host_path.read_text('utf8'))
    assert host['runtime_sha256']==runtime
    callback_path = PROJECT/'verification/original-callback-vm-test.json'
    report = compare_host(host,load('verification/original-callback-vm-test.json'),plans)
    report.update(original_guest_sha256=digest(host_path),original_callback_sha256=digest(callback_path))
    (CANDIDATES/'skill-island-host-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(report)


if __name__=='__main__':
    main()
