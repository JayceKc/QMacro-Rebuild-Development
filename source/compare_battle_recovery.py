"""Compare bounded recovery paths and bind reports to the original guest evidence."""
import hashlib
import json
import sys

from compare_battle_control import compare
from export_battle_recovery import CANDIDATES, RECOVERY_RANGES
from export_battle_restart import RESTART_RANGES
from export_battle_routes import ROUTE_RANGES
from export_battle_tail import TAIL_RANGES
from export_battle_scan import SCAN_RANGES
from export_battle_scan import ROOT_SUFFIX
from replay_shared_battle import PROJECT, load


def read(path):
    return json.loads(path.read_text('utf8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(family='recovery'):
    all_ranges = {'recovery': RECOVERY_RANGES, 'restart': RESTART_RANGES, 'routes': ROUTE_RANGES,
                  'tail': TAIL_RANGES, 'scan': SCAN_RANGES,
                  'root': {m:((start,last,'主流程保留尾段'),) for m,(start,last,_) in ROOT_SUFFIX.items()}}
    for module, ranges in all_ranges[family].items():
        native_path = CANDIDATES / f'original-battle-{family}-{module}.json'
        if not native_path.exists():
            native_path = PROJECT / 'verification' / native_path.name
        spec_path = CANDIDATES / f'battle-{family}-{module}-cases.json'
        plan_path = CANDIDATES / f'battle-{family}-{module}.json'
        base = load(f'data/battle-{module}.json')
        native, control = read(native_path), read(plan_path)
        assert native['source_program_sha256'] == base['source_program_sha256'] == control['source_program_sha256'] == digest(PROJECT / f'programs/{module}.json')
        assert native['runtime_sha256'] == digest(PROJECT / 'bin/QMacro.Rebuild.Runtime.dll')
        assert native['case_spec_sha256'] == digest(spec_path)
        report = compare(native, read(spec_path)['cases'], base, control)
        new_records = {at for start, end, _ in ranges for at in range(start, end+1)}
        covered = sorted(new_records.intersection(report['covered_records']))
        report.update(new_records=len(new_records), covered_new_records=covered,
                      original_guest_sha256=digest(native_path), case_spec_sha256=digest(spec_path),
                      **{f'{family}_plan_sha256':digest(plan_path)})
        if family=='routes':
            report['new_builtin_sites'] = sorted({reply['record'] for case in native['cases']
                                                 for reply in case['builtin_replies']} & new_records)
            role_traces = {
                event['Record'] for case in native['cases'] for event in case['events']
                if event['Kind']=='trace' and event['Value'].startswith('切换第') and event['Value'].endswith('个角色')
            }
            report['role_selection_sites'] = sorted(role_traces & new_records)
        if family=='tail':
            for kind in ('capture','random'):
                report[f'{kind}_sites'] = sorted({reply['record'] for case in native['cases']
                                                  for reply in case[f'{kind}_replies']} & new_records)
        (CANDIDATES / f'battle-{family}-{module}-original-vs-rebuild.json').write_text(
            json.dumps(report, indent=2) + '\n', encoding='utf8')
        print(module, report['cases'], report['external_events'], len(covered))


if __name__ == '__main__':
    main(*sys.argv[1:])
