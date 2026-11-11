from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/gathering-worker.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_gathering_worker import GatheringGWorker,GatheringDependencyMissing
from replay_gathering_worker import replay
from compare_gathering_worker import compare
PLAN=json.loads((PROJECT/'data/gathering-worker.json').read_text())
CASES=json.loads((PROJECT/'data/gathering-worker-cases.json').read_text())['cases']


class WorkerTests(unittest.TestCase):
    def test_all_source_and_control_records_preserved(self):
        p=json.loads((PROJECT/'programs/08.json').read_text())
        self.assertEqual([a['record'] for a in PLAN['actions']],list(range(890,915)))
        for a in PLAN['actions']:
            op,loc,arg,flags=p['code'][a['record']]
            self.assertEqual((op,loc),(a['opcode'],a['location']))
            if a['source_sl'] is not None:self.assertEqual((arg,p['strings'][arg]),(a['source_sl'],a['source']))
            if op in (6,16):self.assertEqual(a['target'],a['record']+arg)

    def test_original_guest_paths_and_effects(self):
        native=json.loads((PROJECT/'verification/original-gathering-worker.json').read_text(encoding='utf-8-sig'))
        result=compare(native,{'ok':True,'cases':[replay(PLAN,c) for c in CASES]})
        self.assertEqual((result['cases'],result['records_covered']),(41,23))

    def test_g_requires_both_observations_not_return_codes(self):
        for c in CASES[:18]:
            r=replay(PLAN,c);keys=[e for e in r['events'] if e['kind']=='key_press']
            self.assertEqual(len(keys),6 if c['color_result']>=0 and c['picture_result']>=0 else 0)
            self.assertFalse(set(r['records'])&{913,914})

    def test_sdk_is_re_read_and_missing_marker_stops(self):
        r=replay(PLAN,CASES[16]);specs=[e['arguments'][4] for e in r['events'] if e['kind']=='find_color']
        self.assertEqual(specs,['112233-151515','A0B0C0-151515'])
        for bad in (None,'','bogus',0):
            m=GatheringGWorker(PLAN,lambda role:bad)
            while m.pc!=897:m.step()
            with self.assertRaises(GatheringDependencyMissing):m.step()
            self.assertEqual(m.pc,897)

    def test_cancel_pending_observation_and_exclusive_bounds(self):
        m=GatheringGWorker(PLAN,lambda role:'112233' if role=='sdk_marker' else 0)
        while not m.waiting:m.step()
        with self.assertRaises(GatheringDependencyMissing):m.step()
        with self.assertRaises(ValueError):m.supply_query(260,1,1)
        self.assertIsNotNone(m.waiting);m.stop()
        self.assertIsNone(m.waiting);self.assertEqual(m.step()['reason'],'cancelled')
        with self.assertRaises(GatheringDependencyMissing):m.supply_query(160,1,1)


if __name__=='__main__':unittest.main()
