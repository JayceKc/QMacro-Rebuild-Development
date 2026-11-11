"""Compare saved guest observations with the linked cube event model."""
import hashlib
import json

from compare_cube_cases import effects
from replay_cube_main import PROJECT, load, replay


def owned_effects(result):
    base = iter(effects(result))
    records = []
    for event in result['events']:
        kind, at = event['kind'], event['record']
        if kind in ('delay', 'trace', 'exit_script', 'key_press', 'mouse_click', 'move_to',
                    'os_exit_intent', 'load_service_intent', 'query_reply'):
            records.append(next(base))
        elif kind in ('dm_error_policy_intent', 'dm_real_mouse_intent', 'thread_control_intent', 'key_down', 'key_up'):
            records.append(dict(record=at, kind=kind, value=event['arguments']))
        elif kind == 'ui_write':
            records.append(dict(record=at, kind=kind, value=[event['path'], event['value']]))
        elif kind == 'create_dm_intent':
            records.append(dict(record=at, kind='source_rewrite', value=['SET DM=CREATEOBJECT("dm.dmsoft")', 'Set DM=QMacroCubeMainVision']))
        elif kind == 'worker_start':
            records.append(dict(record=at, kind=kind, value=[event['worker_id'], event['target']]))
        elif kind == 'capture_intent':
            records.append(dict(record=at, kind=kind, value=event['rect']+[event['path']]))
        elif kind == 'open_log_intent':
            records.append(dict(record=at, kind='open_log', value=event['arguments']))
        elif kind == 'mouse_move':
            args = event['arguments']
            records.append(dict(record=at, kind=kind, value=[args[:2], *args[2:]]))
        elif kind == 'screenshot_intent':
            records.append(dict(record=at, kind=kind, value=event['arguments']))
        elif kind == 'source_rewrite':
            records.append(dict(record=at, kind=kind, value=event['value']))
        elif kind in ('builtin_color', 'builtin_picture'):
            arguments = event['rect'] + [event['spec']]
            if kind == 'builtin_color':
                arguments.append(event['direction'])
            arguments.append(event['similarity'])
            records.append(dict(record=at, kind=kind, value=arguments))
        elif kind == 'builtin_cursor':
            records.append(dict(record=at,kind=kind,value=[]))
    assert next(base, None) is None
    return records


def compare(native, specs, plan, child):
    assert native['ok'] and native['rewritten_records'] == [1678]
    assert native['synthetic_root_frame'] and not native['original_native_loaded'] and not native['game_input_sent']
    assert len(native['cases']) == len(specs)
    coverage, calls, ui = set(), set(), set()
    count = restores = 0
    for original, spec in zip(native['cases'], specs):
        owned = replay(plan, child, spec)
        for key in ('id', 'records', 'reason', 'next_record', 'shared_accesses', 'final_shared', 'restores', 'root_slots', 'frame_depth'):
            assert original[key] == owned[key], (spec['label'], key)
        expected = owned_effects(owned)
        actual = [dict(record=e['Record'], kind='thread_control_intent' if e['Kind']=='thread_control_unmatched' else e['Kind'],
                       value=e['Value']) for e in original['events']]
        assert actual == expected, (spec['label'], next(((a,b) for a,b in zip(actual, expected) if a!=b), (len(actual),len(expected))))
        count += len(actual)
        restores += len(original['restores'])
        coverage.update(original['records'])
        calls.update(e['record'] for e in owned['events'] if e['kind']=='call')
        ui.update(e['record'] for e in actual if e['kind']=='ui_write')
    return dict(ok=True, cases=len(specs), external_events=count, frame_restorations=restores,
                records_covered=len(coverage), covered_records=sorted(coverage), covered_call_sites=sorted(calls),
                ui_write_records=sorted(ui), full_module_restored=False, real_worker_control_verified=False)


def main():
    native = load('verification/original-cube-main.json')
    plan, child = load('data/cube-main.json'), load('data/cube-routines.json')
    def digest(path):
        return hashlib.sha256((PROJECT/path).read_bytes()).hexdigest()
    assert native['case_spec_sha256'] == digest('data/cube-main-cases.json')
    assert native['source_program_sha256'] == plan['source_program_sha256'] == digest('programs/07.json')
    assert native['runtime_sha256'] == digest('bin/QMacro.Rebuild.Runtime.dll')
    report = compare(native, load('data/cube-main-cases.json')['cases'], plan, child)
    report.update(original_guest_sha256=digest('verification/original-cube-main.json'),
                  case_spec_sha256=native['case_spec_sha256'], plan_sha256=digest('data/cube-main.json'))
    (PROJECT/'verification/cube-main-original-vs-rebuild.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='covered_records'}))


if __name__ == '__main__':
    main()
