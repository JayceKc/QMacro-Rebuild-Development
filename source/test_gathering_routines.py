from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/gathering-routines.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_gathering_routines import GatheringRoutinesMachine
from qmacro_fishing import FishingDependencyMissing
from replay_gathering_routines import replay
from compare_gathering_routines import compare
PLAN=json.loads((PROJECT/'data/gathering-routines.json').read_text())
CASES=json.loads((PROJECT/'data/gathering-cases.json').read_text())['cases']


class RoutineTests(unittest.TestCase):
    def test_original_703_records_and_control_operands(self):
        p=json.loads((PROJECT/'programs/08.json').read_text());self.assertEqual(len(PLAN['actions']),703)
        for a in PLAN['actions']:
            op,loc,arg,flags=p['code'][a['record']];self.assertEqual((op,loc),(a['opcode'],a['location']))
            if a['source_sl'] is not None:self.assertEqual((arg,p['strings'][arg]),(a['source_sl'],a['source']))
            if op in (6,16):self.assertEqual(a['target'],a['record']+arg)
            if op==12:self.assertEqual(a['target'],arg)

    def test_129_original_paths_effects_and_empty_returns(self):
        native=json.loads((PROJECT/'verification/original-gathering-routines.json').read_text(encoding='utf-8-sig'))
        result=compare(native,{'ok':True,'cases':[replay(PLAN,c) for c in CASES]})
        self.assertEqual((result['cases'],result['records_covered'],result['external_events']),(129,694,4869))

    def test_repair_reloads_worker_id_before_resume(self):
        r=replay(PLAN,CASES[-1]);events=[e['arguments'] for e in r['events'] if e['kind']=='thread_control']
        self.assertEqual(events,[[12345,1],[54321,2]])
        self.assertEqual((r['reason'],r['frame_depth'],r['last_return']),('routine_return',0,None))

    def test_five_missing_vitality_observations_trigger_branch(self):
        for mode,record in ((0,1397),(1,1419),(2,1468),(3,1517),(4,1560)):
            c=next(c for c in CASES if c['entry']==1344 and c['context']['vitality_finish_mode']==mode and c['miss_budget']=={str(record):5})
            r=replay(PLAN,c);replies=[e for e in r['events'] if e['kind']=='query_reply' and e['record']==record]
            self.assertEqual(len(replies),5);self.assertEqual(r['reason'],'script_stop')

    def test_unknown_sdk_cannot_become_default_color(self):
        context=dict(CASES[0]['context'],sdk_marker=None);m=GatheringRoutinesMachine(PLAN,context.get,1277)
        for _ in range(100):
            if m.pc==1332:break
            e=m.step()
            if e['kind']=='find_pic':m.supply_query(1304,279,0)
        self.assertEqual(m.pc,1332)
        with self.assertRaises(FishingDependencyMissing):m.step()
        self.assertEqual(m.pc,1332)

    def test_builtin_and_dm_roi_have_distinct_edges(self):
        context=CASES[0]['context'];m=GatheringRoutinesMachine(PLAN,context.get,1344)
        for _ in range(100):
            if m.waiting and m.waiting['kind']=='builtin_color':break
            e=m.step()
            if e['kind']=='find_color':m.supply_query(161,3,1)
        self.assertEqual(m.waiting['kind'],'builtin_color')
        m.supply_query(896,932,896*8192+932)  # Original builtin includes right/bottom.
        m.stop();self.assertIsNone(m.waiting);self.assertEqual(m.step()['reason'],'cancelled')


if __name__=='__main__':unittest.main()
