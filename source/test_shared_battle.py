import unittest

from compare_battle_form import compare as compare_form
from compare_battle_control import compare as compare_control
from compare_shared_battle import compare
from export_battle_control import build as build_control
from export_battle_restart import build_restart
from export_battle_routes import MAP_SCAN_CHECKPOINTS, ROUTE_RANGES, build_routes
from export_battle_root import build_root
from export_battle_retained import build_retained
from export_battle_scan import ROOT_SUFFIX, SCAN_RANGES, build_scan, inventory
from export_battle_tail import ENTRY_VERSION_CHECKPOINTS, TAIL_RANGES, build_tail
from export_shared_battle import CORE_STARTS,build
from replay_shared_battle import load
from qmacro_cube import CubeDependencyMissing
from qmacro_shared_battle import SharedBattleMachine


class SharedBattleTests(unittest.TestCase):
    def test_each_version_keeps_original_records_and_random_bounds(self):
        for module,count in (('01',2290),('03',1870),('06',2245)):
            plan = load(f'data/battle-{module}.json')
            rebuilt = build(module,load(f'programs/{module}.json'))
            self.assertEqual(rebuilt['actions'],plan['actions'])
            self.assertEqual(len(plan['actions']),count)
        plan = load('data/battle-03.json')
        for at in (2389,2407):
            action = next(a for a in plan['actions'] if a['record']==at)
            self.assertEqual((action['kind'],action['name'],action['span']),('random_int','YYY',10))

    def test_fixed_guest_paths_effects_and_boolean_query_assignment(self):
        cases = events = 0
        for module in CORE_STARTS:
            native = load(f'verification/original-battle-{module}.json')
            specs = load(f'data/battle-{module}-cases.json')['cases']
            result = compare(native,specs,load(f'data/battle-{module}.json'))
            cases += result['cases']
            events += result['external_events']
            self.assertEqual({r['value'] for r in result['observed_comparisons']},{False,True})
            self.assertTrue(all(type(c['value']) is bool for case in native['cases'] for c in case['comparisons']))
        self.assertEqual((cases,events),(165,13844))

    def test_control_preserves_worker_writebacks_and_external_calls(self):
        for module, count, boundaries in (
            ('01', 2163, {742, 838, 6783, 11725}),
            ('03', 397, {417, 5885}),
            ('06', 2146, {6620, 8621}),
        ):
            plan = load(f'data/battle-control-{module}.json')
            rebuilt = build_control(module, load(f'programs/{module}.json'), load(f'data/battle-{module}.json'))
            self.assertEqual(len(plan['actions']), count)
            self.assertEqual(plan['actions'], rebuilt['actions'])
            self.assertEqual(plan['worker_wrappers'], rebuilt['worker_wrappers'])
            self.assertEqual(set(map(int, plan['boundaries'])), boundaries)

    def test_control_fixed_guest_paths_and_all_worker_sites(self):
        totals = []
        for module in CORE_STARTS:
            control = load(f'data/battle-control-{module}.json')
            report = compare_control(load(f'verification/original-battle-control-{module}.json'),
                                     load(f'data/battle-control-{module}-cases.json')['cases'],
                                     load(f'data/battle-{module}.json'), control)
            self.assertEqual(report['worker_start_sites'], [w['start_record'] for w in control['worker_wrappers']])
            totals.append((report['cases'], report['external_events'], report['alternate_queries']))
        self.assertEqual(tuple(map(sum, zip(*totals))), (160, 8382, 50))

    def test_linked_restart_retains_original_records_and_capture_fields(self):
        for module in CORE_STARTS:
            base = load(f'data/battle-{module}.json')
            linked = load(f'data/battle-restart-{module}.json')
            rebuilt = build_restart(module, load(f'programs/{module}.json'), base)
            self.assertFalse(linked['boundaries'])
            self.assertEqual(linked['actions'], rebuilt['actions'])
            frames = [a['initial_fields'] for a in linked['actions'] if 'initial_fields' in a]
            self.assertEqual(len(frames), 1)
            self.assertEqual([node['const'] if 'const' in node else node['numeric']['const']
                              for node in frames[0].values()], [0, 0, 1920, 1080, 'C:\\方舟混沌\\', 'bmp'])

    def test_recovery_and_restart_preserve_original_recordings(self):
        totals = {}
        for family in ('recovery','restart'):
            counts = []
            for module in CORE_STARTS:
                stem = f'battle-{family}-{module}'
                original = load(f'verification/original-{stem}.json')
                cases = load(f'data/{stem}-cases.json')['cases']
                report = compare_control(original, cases, load(f'data/battle-{module}.json'), load(f'data/{stem}.json'))
                counts.append((report['cases'], report['external_events']))
                if family=='restart':
                    self.assertEqual(report['stop_reasons'], {'restart_requested':len(cases)})
            totals[family] = tuple(map(sum,zip(*counts)))
        self.assertEqual(totals, {'recovery':(28,2774),'restart':(16,1814)})

    def test_route_boundaries_and_bypass_are_preserved(self):
        for module in CORE_STARTS:
            linked = load(f'data/battle-routes-{module}.json')
            original = load(f'programs/{module}.json')
            rebuilt = build_routes(module, original, load(f'data/battle-{module}.json'))
            self.assertFalse(linked['boundaries'])
            self.assertEqual(linked['actions'], rebuilt['actions'])
            if module in MAP_SCAN_CHECKPOINTS:
                start,target = MAP_SCAN_CHECKPOINTS[module]
                self.assertEqual(linked['reviewed_checkpoints'], [start])
                self.assertEqual(original['code'][start-1][2], target)

    def test_route_guest_observes_all_role_traces_and_builtin_sites(self):
        for module in CORE_STARTS:
            stem = f'battle-routes-{module}'
            control = load(f'data/{stem}.json')
            original = load(f'verification/original-{stem}.json')
            cases = load(f'data/{stem}-cases.json')['cases']
            result = compare_control(original, cases, load(f'data/battle-{module}.json'), control)
            selected = {at for start,last,_ in ROUTE_RANGES[module] for at in range(start,last+1)}
            builtins = {a['record'] for a in control['actions'] if a['record'] in selected
                        and a['kind'] in ('builtin_color','builtin_picture')}
            replies = {e['record'] for case in original['cases'] for e in case['builtin_replies']}
            self.assertTrue(builtins <= replies)
            labels = {e['Value'] for case in original['cases'] for e in case['events']
                      if e['Kind']=='trace' and e['Value'].startswith('切换第') and e['Value'].endswith('个角色')}
            self.assertEqual(len(labels), 30 if module in ('01','03') else 0)
            self.assertEqual(result['cases'],len(cases))

    def test_tail_original_effects_capture_results_and_coordinate_ranges(self):
        total_cases = 0
        for module in CORE_STARTS:
            stem = f'battle-tail-{module}'
            base = load(f'data/battle-{module}.json')
            control = load(f'data/{stem}.json')
            self.assertEqual(build_tail(module,load(f'programs/{module}.json'),base)['actions'],control['actions'])
            original = load(f'verification/original-{stem}.json')
            cases = load(f'data/{stem}-cases.json')['cases']
            report = compare_control(original,cases,base,control)
            total_cases += report['cases']
            selected = {at for start,last,_ in TAIL_RANGES[module] for at in range(start,last+1)}
            captures = [(r['record'],r['dm_ret']) for case in original['cases']
                        for r in case['capture_replies'] if r['record'] in selected]
            self.assertEqual(len(set(captures)),16 if module in ('01','06') else 0)
            entry,last,_ = next(r for r in TAIL_RANGES[module] if r[2]=='按鈕進本')
            first = {a['record'] for a in [a for a in control['actions']
                     if entry<=a['record']<=last and a['kind']=='random_int'][:4]}
            checkpoints = [r for r,s in zip(original['cases'],cases)
                           if s['entry']==ENTRY_VERSION_CHECKPOINTS[module]]
            sampled = {(event['record'],event['supplied']==event['lower']) for r in checkpoints
                       for event in r['random_replies'] if event['record'] in first}
            self.assertEqual(sampled,{(at,lower) for at in first for lower in (True,False)})
        self.assertEqual(total_cases,63)

    def test_scan_counts_and_remaining_inventory_are_bound_to_original_records(self):
        for module in CORE_STARTS:
            stem = f'battle-scan-{module}'
            raw = load(f'programs/{module}.json')
            base = load(f'data/battle-{module}.json')
            linked = load(f'data/{stem}.json')
            self.assertEqual(build_scan(module,raw,base)['actions'],linked['actions'])
            audit = inventory(module,raw,base,linked)
            self.assertEqual(audit,load(f'data/battle-remaining-{module}.json'))
            self.assertEqual(audit['total'],audit['missing']+audit['linked']+len(audit['records']))
            if module in ROOT_SUFFIX:
                self.assertIn(ROOT_SUFFIX[module][2],raw['missing_records'])
            specs = load(f'data/{stem}-cases.json')['cases']
            native = load(f'verification/original-{stem}.json')
            report = compare_control(native,specs,base,linked)
            self.assertEqual(report['cases'],3)
            self.assertEqual([case['return_value'] for case in native['cases']],[0,3,2])
            start,last,_ = SCAN_RANGES[module][0]
            self.assertEqual(set(range(start,last+1))-set(report['covered_records']),{start+21})

    def test_root_suffix_matches_original_slots_and_preserves_missing_boundary(self):
        for module,(entry,_,boundary) in ROOT_SUFFIX.items():
            stem = f'battle-root-{module}'
            base = load(f'data/battle-{module}.json')
            program = load(f'programs/{module}.json')
            control = load(f'data/{stem}.json')
            rebuilt = build_root(module,program,base)
            self.assertEqual(rebuilt['actions'],control['actions'])
            self.assertEqual(control['boundaries'],{str(boundary):'missing_original_record'})
            self.assertIn(boundary,program['missing_records'])
            specs = load(f'data/{stem}-cases.json')['cases']
            original = load(f'verification/original-{stem}.json')
            result = compare_control(original,specs,base,control)
            self.assertEqual(result['stop_reasons'].get('missing_original_record'),1)
            case = original['cases'][0]
            self.assertEqual((case['next_record'],case['call_depth']),(boundary,0))
            if module=='01':
                self.assertEqual(case['root_values'][0],3)
                with self.assertRaisesRegex(CubeDependencyMissing,'Missing explicit retained root slots'):
                    SharedBattleMachine(base,entry,lambda key,at:None,{},control=control)

    def test_retained_join_preserves_each_record_and_form_state(self):
        plans = {}
        retained_count = missing_count = 0
        for module in CORE_STARTS:
            raw = load(f'programs/{module}.json')
            base = load(f'data/battle-{module}.json')
            control = load(f'data/battle-retained-{module}.json')
            plans[module] = (base,control)
            rebuilt = build_retained(module,raw,base)
            self.assertEqual(rebuilt['actions'],control['actions'])
            actions = base['actions']+control['actions']
            for a in actions:
                self.assertEqual([a[k] for k in ('opcode','location','operand','field_3')],raw['code'][a['record']])
                if a['source_sl'] is not None:
                    self.assertEqual(a['source'],raw['strings'][a['source_sl']])
            self.assertEqual(set(map(int,control['boundaries'])),set(raw['missing_records']))
            retained_count += len(actions)
            missing_count += len(control['boundaries'])
        self.assertEqual((retained_count,missing_count),(29041,1328))
        report = compare_form(load('verification/original-battle-form.json'),
                              load('verification/original-callback-vm-test.json'),plans)
        self.assertEqual(report['default_entry_boundaries'],{'01':62,'03':40,'06':56})
        self.assertEqual((report['form_cases'],report['observed_steps']),(9,63))
        self.assertEqual(report['callback'],{'clicks':2,'delete_intents':10,'file_loads':1})
