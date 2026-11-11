import unittest

from compare_cube_retained import compare
from export_cube_retained import build
from replay_cube_retained import load


class CubeRetainedTests(unittest.TestCase):
    def test_union_has_every_retained_record_and_keeps_missing_branch(self):
        original = load('programs/07.json')
        main,workers = load('data/cube-main.json'),load('data/cube-workers.json')
        plan = build(original,main,workers)
        saved = load('data/cube-retained-tail.json')
        self.assertEqual(plan['actions'],saved['actions'])
        self.assertEqual((len(plan['actions']),plan['retained_records'],len(plan['missing_records'])),(367,6320,500))
        self.assertEqual([e for e in plan['explicit_edges'] if e['target_missing']],
                         [{'record':853,'target':451,'kind':'jump','target_missing':True}])

    def test_saved_original_entry_wait_skip_and_capture_paths(self):
        tail,main,workers,child = (load('data/'+name+'.json') for name in ('cube-retained-tail','cube-main','cube-workers','cube-routines'))
        native = load('verification/original-cube-retained.json')
        specs = load('data/cube-retained-cases.json')['cases']
        result = compare(native,specs,tail,main,workers,child)
        self.assertEqual((result['cases'],result['external_events'],result['wait_polls']),(20,694,17))
        self.assertEqual(result['observed_missing_boundaries'],[31,451])
        self.assertEqual(result['capture_sites'],list(range(6457,6472,2)))
        self.assertEqual(result['stop_reasons']['program_end'],1)
        self.assertEqual(result['stop_reasons']['iteration_end'],1)
