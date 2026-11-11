import unittest

from compare_cube_workers import compare
from export_cube_workers import build
from replay_cube_workers import load, replay


class CubeWorkerTests(unittest.TestCase):
    def test_worker_wrapper_inventory_matches_original_dispatch(self):
        raw = load('programs/07.json')
        saved = load('data/cube-workers.json')
        plan = build(raw)
        self.assertEqual(plan['actions'], saved['actions'])
        self.assertEqual(len(plan['actions']), 1976)
        self.assertEqual([(w['start_record'], w['worker_entry']) for w in plan['worker_wrappers']],
                         [(w['record'], w['entry']) for w in raw['worker_starts']])
        self.assertEqual(plan['worker_wrappers'][0]['parent_slot_scope'], 'root_slot')
        self.assertEqual({w['parent_slot_scope'] for w in plan['worker_wrappers'][1:]}, {'slot'})

    def test_fixed_guest_worker_dispatch_and_potion_roi(self):
        plan, child = load('data/cube-workers.json'), load('data/cube-routines.json')
        specs = load('data/cube-worker-cases.json')['cases']
        report = compare(load('verification/original-cube-workers.json'), specs, plan, child)
        self.assertEqual((report['cases'],report['external_events'],report['shared_writes']), (28,3145,42))
        self.assertEqual(report['spawn_sites'], [w['start_record'] for w in plan['worker_wrappers']])
        self.assertEqual(report['worker_wrapper_entries'], [w['worker_entry'] for w in plan['worker_wrappers']])
        spec = next(s for s in specs if s['label']=='worker-4889-three-misses')
        result = replay(plan,child,spec)
        self.assertEqual(next(e['rect'] for e in result['events'] if e['record']==6492), [652,959,656,972])
        first_key = next(i for i,e in enumerate(result['events']) if e['kind']=='key_press')
        self.assertEqual(sum(e['kind']=='query_reply' for e in result['events'][:first_key]), 3)
        self.assertEqual(result['events'][first_key]['arguments'][0], '1')
