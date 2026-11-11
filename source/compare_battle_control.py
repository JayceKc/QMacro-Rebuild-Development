"""Compare the battle control paths with recordings of the original instructions."""
from collections import Counter
import hashlib
import json

from compare_cube_main import owned_effects
from export_shared_battle import CORE_STARTS
from replay_shared_battle import PROJECT, load, replay


def compare(native, specs, plan, control):
    assert native['ok'] and native['synthetic_context']
    assert not native['original_native_loaded'] and not native['game_input_sent']
    assert len(native['cases']) == len(specs)
    records, starts = set(), set()
    effects = alternate_queries = 0
    for original, spec in zip(native['cases'], specs):
        model = replay(plan, spec, control)
        for key in ('id', 'records', 'reason', 'next_record', 'call_depth',
                    'comparisons', 'final_shared', 'alternate_outputs'):
            assert original[key] == model[key], (native['module'], spec['label'], key)
        if 'frame_fields' in spec:
            assert original['return_value']==model['return_value']==spec['expected_count'], (native['module'],spec['label'],'return_value')
        if 'root_slots' in spec:
            assert original['root_values']==model['root_values'], (native['module'],spec['label'],'root_values')
        if 'observe_scalars' in spec:
            assert original['scalar_values']==model['scalar_values'], (native['module'],spec['label'],'scalar_values')
        replies = [{k: v for k, v in event.items() if k != 'kind'} for event in model['events']
                   if event['kind'] == 'builtin_query_reply']
        assert original.get('builtin_replies', []) == replies, (native['module'], spec['label'], 'builtin_replies')
        captures = [{k: v for k, v in event.items() if k != 'kind'} for event in model['events']
                    if event['kind'] == 'capture_reply']
        assert original.get('capture_replies', []) == captures, (native['module'], spec['label'], 'capture_replies')
        cursor = [{k: v for k,v in e.items() if k!='kind'} for e in model['events'] if e['kind']=='cursor_reply']
        assert original.get('cursor_replies',[])==cursor, (native['module'],spec['label'],'cursor_replies')
        if 'random_replies' in original:
            random = [{k: event[k] for k in ('record','lower','span','supplied')}
                      for event in model['events'] if event['kind']=='random_int']
            assert original['random_replies'] == random, (native['module'], spec['label'], 'random_replies')
        actual = [
            dict(record=event['Record'], value=event['Value'],
                 kind='thread_control_intent' if event['Kind'] == 'thread_control_unmatched' else event['Kind'])
            for event in original['events']
        ]
        expected = owned_effects(model)
        assert actual == expected, (native['module'], spec['label'], next(
            ((a, b) for a, b in zip(actual, expected) if a != b), (len(actual), len(expected))))
        records.update(model['records'])
        starts.update(event['record'] for event in actual if event['kind'] == 'worker_start')
        effects += len(actual)
        alternate_queries += len(model['alternate_outputs'])
    return dict(ok=True, module=native['module'], cases=len(specs), external_events=effects,
                records_covered=len(records), covered_records=sorted(records), worker_start_sites=sorted(starts),
                alternate_queries=alternate_queries,
                stop_reasons=dict(Counter(case['reason'] for case in native['cases'])),
                full_module_restored=False)


def main():
    def digest(path):
        return hashlib.sha256((PROJECT / path).read_bytes()).hexdigest()

    for module in CORE_STARTS:
        native_path = f'verification/original-battle-control-{module}.json'
        case_path = f'data/battle-control-{module}-cases.json'
        plan_path = f'data/battle-{module}.json'
        control_path = f'data/battle-control-{module}.json'
        native, plan, control = load(native_path), load(plan_path), load(control_path)
        assert native['source_program_sha256'] == plan['source_program_sha256'] == control['source_program_sha256'] == digest(f'programs/{module}.json')
        assert native['runtime_sha256'] == digest('bin/QMacro.Rebuild.Runtime.dll')
        assert native['case_spec_sha256'] == digest(case_path)
        report = compare(native, load(case_path)['cases'], plan, control)
        report.update(original_guest_sha256=digest(native_path), case_spec_sha256=digest(case_path),
                      plan_sha256=digest(plan_path), control_plan_sha256=digest(control_path))
        (PROJECT / f'verification/battle-control-{module}-original-vs-rebuild.json').write_text(
            json.dumps(report, indent=2) + '\n', encoding='utf8')
        print(json.dumps({key: value for key, value in report.items() if key != 'covered_records'}))


if __name__ == '__main__':
    main()
