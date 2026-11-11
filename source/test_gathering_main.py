import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_gathering_main import GatheringMainMachine
from qmacro_fishing import FishingDependencyMissing
from replay_gathering_main import replay
from compare_gathering_main import compare
from compare_gathering_retained import compare as compare_host
from export_gathering_retained import build as build_retained
from qmacro_gathering_retained import make_context
from qmacro_gathering_worker import GatheringGWorker
PLAN=json.loads((PROJECT/'data/gathering-main-suffix.json').read_text());CASES=json.loads((PROJECT/'data/gathering-main-cases.json').read_text())['cases']


class MainTests(unittest.TestCase):
    def test_retained_dispatch_accounts_for_every_record(self):
        raw=json.loads((PROJECT/'programs/08.json').read_text('utf8'))
        plan=json.loads((PROJECT/'data/gathering-retained.json').read_text('utf8'))
        worker=json.loads((PROJECT/'data/gathering-worker.json').read_text('utf8'))
        native=json.loads((PROJECT/'verification/original-gathering-host.json').read_text('utf8'))
        self.assertEqual(build_retained(raw,PLAN,worker)['actions'],plan['actions'])
        self.assertEqual(len(plan['actions']),1126)
        self.assertEqual(plan['missing_records'],list(range(7,507)))
        report=compare_host(native,plan)
        self.assertEqual((report['default_boundary'],report['form_steps']),(7,15))
        self.assertIsInstance(make_context(plan,PLAN,worker,890,lambda key:None),GatheringGWorker)
        case=CASES[0]
        self.assertIsInstance(make_context(plan,PLAN,worker,case['entry'],case['context'].get,
                                           initial=case['initial']),GatheringMainMachine)

    def test_all_original_tuple_fields_and_child_targets(self):
        p=json.loads((PROJECT/'programs/08.json').read_text());self.assertEqual(len(PLAN['actions']),1091)
        for a in PLAN['actions']:
            op,loc,arg,field=p['code'][a['record']];self.assertEqual((op,loc,field),(a['opcode'],a['location'],a['field_3']))
            if a['source_sl'] is not None:self.assertEqual((arg,p['strings'][arg]),(a['source_sl'],a['source']))
            if op in (6,16):self.assertEqual(a['target'],a['record']+arg)
            if op==12:self.assertEqual(a['target'],arg)
        self.assertFalse(PLAN['field_3_semantics_verified'])

    def test_74_original_paths_frames_history_and_events(self):
        native=json.loads((PROJECT/'verification/original-gathering-main.json').read_text(encoding='utf-8-sig'))
        result=compare(native,{'ok':True,'cases':[replay(PLAN,c) for c in CASES]})
        self.assertEqual((result['cases'],result['external_events']),(74,6393))

    def test_missing_prefix_is_a_boundary_not_silent_noop(self):
        r=replay(PLAN,CASES[0]);self.assertEqual((r['reason'],r['next_record']),('missing_original_record',432))
        self.assertEqual(r['records'][-1],432);self.assertEqual(r['events'][-1],{'record':432,'kind':'missing_original_record'})
        self.assertNotIn(433,r['records']);self.assertEqual(len(PLAN['missing_records']),500)

    def test_recovery_threshold_is_strictly_more_than_five(self):
        for value,count in ((4,0),(5,7)):
            c=next(c for c in CASES if c['entry']==507 and c['initial']['fallback_attempts']==value and c['random_values']['recovery_delay']==66)
            r=replay(PLAN,c);keys=[e['arguments'][0] for e in r['events'] if e['kind']=='key_press']
            self.assertEqual(len(keys),count)
            if count:self.assertEqual(keys,['Q','F','E','A','D','R','S'])

    def test_third_identical_mineral_position_gets_offset_click(self):
        r=replay(PLAN,CASES[-2]);self.assertEqual(r['main_cycles'],3)
        offsets=[e for e in r['events'] if e['record']==658];self.assertEqual(len(offsets),1)
        self.assertEqual(offsets[0]['arguments'],[12,63]);self.assertEqual(r['history']['x2'],0)

    def test_real_skip_chain_finishes_without_entering_ui_or_bodies(self):
        c=next(c for c in CASES if c['entry']==593 and c['context']['gather_mode']==0);r=replay(PLAN,c)
        self.assertEqual(r['records'],[593,594,688,889,915,1276,1343,1621,1625]);self.assertEqual(r['reason'],'program_end')
        self.assertEqual(r['next_record'],1626);self.assertTrue(r['root_current_is_nothing'])

    def test_prefix_state_must_be_explicit_and_target_queries_are_separate(self):
        with self.assertRaises(FishingDependencyMissing):GatheringMainMachine(PLAN,CASES[0]['context'].get,{},507)
        c=next(c for c in CASES if c['entry']==540);m=GatheringMainMachine(PLAN,c['context'].get,c['initial'],540)
        m.values.update(query_x=161,query_y=3)
        m.step();request=m.step();self.assertEqual(request['kind'],'find_color');m.supply_query(1800,120,1)
        self.assertEqual((m.values['query_x'],m.values['query_y']),(161,3));self.assertEqual((m.values['target_x'],m.values['target_y']),(1800,120))


if __name__=='__main__':unittest.main()
