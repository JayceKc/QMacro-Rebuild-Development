"""Compare three separately preserved battle variants with fixed guest traces."""
from collections import Counter
import hashlib
import json

from compare_cube_main import owned_effects
from export_shared_battle import CORE_STARTS
from replay_shared_battle import PROJECT,load,replay


def compare(native, specs, plan):
    assert native['ok'] and native['synthetic_context']
    assert not native['original_native_loaded'] and not native['game_input_sent']
    assert len(native['cases'])==len(specs)
    records, comparisons = set(),set()
    count = 0
    for original,spec in zip(native['cases'],specs):
        model = replay(plan,spec)
        for key in ('id','records','reason','next_record','call_depth','comparisons','final_shared'):
            assert original[key]==model[key], (native['module'],spec['id'],spec['label'],key)
        expected = owned_effects(model)
        actual = [dict(record=e['Record'],kind='thread_control_intent' if e['Kind']=='thread_control_unmatched' else e['Kind'],value=e['Value']) for e in original['events']]
        assert actual==expected, (native['module'],spec['label'],next(((a,b) for a,b in zip(actual,expected) if a!=b),(len(actual),len(expected))))
        records.update(model['records'])
        comparisons.update((c['record'],c['value']) for c in model['comparisons'])
        count += len(actual)
    return dict(ok=True,module=native['module'],cases=len(specs),external_events=count,records_covered=len(records),covered_records=sorted(records),
                observed_comparisons=[dict(record=at,value=value) for at,value in sorted(comparisons)],
                stop_reasons=dict(Counter(c['reason'] for c in native['cases'])),full_module_restored=False)


def main():
    def digest(path):
        return hashlib.sha256((PROJECT/path).read_bytes()).hexdigest()
    for module in CORE_STARTS:
        path=f'verification/original-battle-{module}.json'
        case_path=f'data/battle-{module}-cases.json'
        plan_path=f'data/battle-{module}.json'
        native,plan = load(path),load(plan_path)
        assert native['source_program_sha256']==plan['source_program_sha256']==digest(f'programs/{module}.json')
        assert native['runtime_sha256']==digest('bin/QMacro.Rebuild.Runtime.dll')
        assert native['case_spec_sha256']==digest(case_path)
        report = compare(native,load(case_path)['cases'],plan)
        report.update(original_guest_sha256=digest(path),case_spec_sha256=digest(case_path),plan_sha256=digest(plan_path))
        (PROJECT/f'verification/battle-{module}-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
        print(json.dumps({k:v for k,v in report.items() if k!='covered_records'}))


if __name__ == '__main__':
    main()
