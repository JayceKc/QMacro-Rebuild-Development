"""Match retained-tail PC, wait states, root slots, and effects against saved observations."""
from collections import Counter
import hashlib
import json

from compare_cube_main import owned_effects
from replay_cube_retained import PROJECT, load, replay


def compare(native, specs, tail, main, workers, child):
    assert native['ok'] and native['synthetic_prefix_values']
    assert not any(native[key] for key in ('original_native_loaded','capture_files_written','game_input_sent'))
    assert len(native['cases'])==len(specs)
    captures, missing = set(),set()
    covered = set()
    effect_count = wait_count = 0
    for original,spec in zip(native['cases'],specs):
        owned = replay(tail,main,workers,child,spec)
        for key in ('id','records','waits','reason','next_record','final_shared'):
            assert original[key]==owned[key],(spec['label'],key)
        assert original['root_slots']=={str(i):v for i,v in owned['root_slots'].items() if v is not None},(spec['label'],'root slots')
        actual = [dict(record=e['Record'],kind='thread_control_intent' if e['Kind']=='thread_control_unmatched' else e['Kind'],value=e['Value']) for e in original['events']]
        expected = owned_effects(owned)
        assert actual==expected,(spec['label'],next(((a,b) for a,b in zip(actual,expected) if a!=b),(len(actual),len(expected))))
        effect_count += len(actual)
        wait_count += len(owned['waits'])
        captures.update(e['record'] for e in actual if e['kind']=='capture_intent')
        covered.update(original['records'])
        if original['reason']=='missing_original_record':
            missing.add(original['next_record'])
    retained = covered-set(tail['missing_records'])-{tail['total_records']}
    return dict(ok=True,cases=len(specs),external_events=effect_count,wait_polls=wait_count,covered_records=sorted(retained),
                records_covered=len(retained),capture_sites=sorted(captures),observed_missing_boundaries=sorted(missing),
                stop_reasons=dict(Counter(c['reason'] for c in native['cases'])),full_module_restored=False)


def main():
    def digest(path):
        return hashlib.sha256((PROJECT/path).read_bytes()).hexdigest()
    native = load('verification/original-cube-retained.json')
    tail,main_plan,workers,child = (load('data/'+name+'.json') for name in ('cube-retained-tail','cube-main','cube-workers','cube-routines'))
    assert all(digest(path)==value for path,value in tail['input_sha256'].items())
    assert native['source_program_sha256']==digest('programs/07.json')
    assert native['runtime_sha256']==digest('bin/QMacro.Rebuild.Runtime.dll')
    assert native['case_spec_sha256']==digest('data/cube-retained-cases.json')
    report = compare(native,load('data/cube-retained-cases.json')['cases'],tail,main_plan,workers,child)
    report.update(tail_sha256=digest('data/cube-retained-tail.json'),original_guest_sha256=digest('verification/original-cube-retained.json'),
                  case_spec_sha256=native['case_spec_sha256'])
    (PROJECT/'verification/cube-retained-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='covered_records'}))


if __name__ == '__main__':
    main()
