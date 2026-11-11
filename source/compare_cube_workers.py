"""Compare coordinator ID flow and worker body effects against fixed guest output."""
from collections import Counter
import hashlib
import json

from compare_cube_main import owned_effects
from replay_cube_workers import PROJECT, load, replay


def compare(native, specs, plan, child):
    assert native['ok'] and native['synthetic_worker_ids']
    assert not native['original_native_loaded'] and not native['game_input_sent']
    assert len(native['cases']) == len(specs)
    covered, spawn_sites, body_entries = set(), set(), set()
    event_count = write_count = 0
    for original, spec in zip(native['cases'],specs):
        owned = replay(plan,child,spec)
        for key in ('id','records','reason','next_record','final_shared'):
            assert original[key] == owned[key], (spec['label'],key,original[key] if key!='records' else 'PC trace')
        assert original['call_depth'] == len(owned['returns']), spec['label']
        assert original['root_slots'] == {str(i):v for i,v in owned['root_slots'].items() if i in (36,37)}, spec['label']
        writes = [{k:e[k] for k in ('record','key','value')} for e in owned['events'] if e['kind']=='write_global']
        assert original['writes'] == writes, (spec['label'],'shared writes')
        expected = owned_effects(owned)
        actual = [dict(record=e['Record'],kind='thread_control_intent' if e['Kind']=='thread_control_unmatched' else e['Kind'],value=e['Value']) for e in original['events']]
        assert actual == expected, (spec['label'],next(((a,b) for a,b in zip(actual,expected) if a!=b),(len(actual),len(expected))))
        covered.update(original['records'])
        spawn_sites.update(e['record'] for e in actual if e['kind']=='worker_start')
        if spec['entry'] in {w['worker_entry'] for w in plan['worker_wrappers']}:
            body_entries.add(spec['entry'])
        event_count += len(actual)
        write_count += len(writes)
    return dict(ok=True,cases=len(specs),external_events=event_count,shared_writes=write_count,records_covered=len(covered),
                covered_records=sorted(covered),spawn_sites=sorted(spawn_sites),worker_wrapper_entries=sorted(body_entries),
                stop_reasons=dict(Counter(c['reason'] for c in native['cases'])),
                real_worker_timing_verified=False,full_module_restored=False)


def main():
    def digest(path):
        return hashlib.sha256((PROJECT/path).read_bytes()).hexdigest()
    native = load('verification/original-cube-workers.json')
    plan = load('data/cube-workers.json')
    assert native['source_program_sha256'] == plan['source_program_sha256'] == digest('programs/07.json')
    assert native['case_spec_sha256'] == digest('data/cube-worker-cases.json')
    assert native['runtime_sha256'] == digest('bin/QMacro.Rebuild.Runtime.dll')
    report = compare(native,load('data/cube-worker-cases.json')['cases'],plan,load('data/cube-routines.json'))
    report.update(plan_sha256=digest('data/cube-workers.json'),original_guest_sha256=digest('verification/original-cube-workers.json'),case_spec_sha256=native['case_spec_sha256'])
    (PROJECT/'verification/cube-workers-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='covered_records'}))


if __name__ == '__main__':
    main()
