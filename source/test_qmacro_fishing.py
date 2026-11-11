from pathlib import Path
import collections,copy,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'qmacro_fishing.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_fishing import FishingMachine,FishingDependencyMissing
from replay_fishing_cases import replay
from compare_fishing_retained import compare as compare_retained
from export_fishing_retained import build as build_retained
from qmacro_fishing_retained import FishingRetainedMachine
PLAN=json.loads((PROJECT/'data/fishing-routines.json').read_text(encoding='utf8'))
CASES=json.loads((PROJECT/'data/fishing-cases.json').read_text(encoding='utf8'))['cases']


class FishingTests(unittest.TestCase):
    def test_retained_join_matches_suffix_and_form_observations(self):
        program=json.loads((PROJECT/'programs/05.json').read_text('utf8'))
        plan=json.loads((PROJECT/'data/fishing-retained.json').read_text('utf8'))
        original=json.loads((PROJECT/'verification/original-fishing-suffix.json').read_text('utf8'))
        rebuilt=build_retained(program,PLAN)
        self.assertEqual(rebuilt['actions'],plan['actions'])
        self.assertEqual(len(plan['actions']),429)
        self.assertEqual(plan['missing_records'],list(range(4,504)))
        for a in plan['actions']:
            self.assertEqual([a[k] for k in ('opcode','location','operand','field_3')],program['code'][a['record']])
        report=compare_retained(original,PLAN,plan)
        self.assertEqual([p['next_record'] for p in report['paths']],[115,115,501,519])
        self.assertEqual((report['suffix_events'],report['form_steps']),(33,15))
        with self.assertRaises(FishingDependencyMissing):
            FishingRetainedMachine(PLAN,plan,lambda role:None,504)

    def test_all_preserved_records_and_closed_cfg(self):
        self.assertEqual([a['record'] for a in PLAN['actions']],list(range(541,878))+list(range(879,924)))
        program=json.loads((PROJECT/'programs/05.json').read_text(encoding='utf8'))
        for a in PLAN['actions']:
            op,location,arg,flags=program['code'][a['record']]
            self.assertEqual((a['opcode'],a['location']),(op,location))
            if a['source_sl'] is not None:self.assertEqual((a['source_sl'],a['source']),(arg,program['strings'][arg]))
            if op in (6,16):self.assertEqual(a['target'],a['record']+arg)
            if op==12:self.assertEqual(a['target'],arg)

    def test_bounded_case_matrix(self):
        self.assertEqual(len(CASES),77)
        results=[replay(PLAN,c) for c in CASES]
        visited=set(r for result in results for r in result['records'])
        reachable={a['record'] for a in PLAN['actions']}
        self.assertTrue(visited<=reachable)
        self.assertTrue({541,559,561,618,650,655,668,672,676,729,759,769,786,804,868,879,923}<=visited)
        for case,result in zip(CASES,results):
            self.assertIn(result['reason'],('routine_return','script_stop'))
            if result['reason']=='routine_return':self.assertEqual((result['frame_depth'],result['last_return']),(0,None))
            if case['context']['repair_mode']==0:self.assertEqual(result['query_count'],0)
        dynamic=results[-1];self.assertEqual([e['record'] for e in dynamic['events'] if e['kind']=='os_exit_intent'],[868])

    def test_return_value_does_not_override_coordinates(self):
        groups=collections.defaultdict(list)
        for c in CASES:
            key=json.dumps({k:v for k,v in c.items() if k not in ('id','inverted_return')},sort_keys=True);groups[key].append(c)
        for pair in groups.values():
            if len(pair)!=2:continue
            a,b=[replay(PLAN,c) for c in pair]
            self.assertEqual(a['records'],b['records'])

    def test_missing_context_blocks_at_actual_use(self):
        context=copy.deepcopy(CASES[0]['context']);context.pop('saved_cursor_x')
        m=FishingMachine(PLAN,context.get)
        for _ in range(300):
            if m.pc==604:break
            e=m.step()
            if e['kind']=='random_int':m.supply_random(e['lower'])
        self.assertEqual(m.pc,604)
        with self.assertRaises(FishingDependencyMissing):m.step()
        self.assertEqual(m.pc,604)
        context['saved_cursor_x']=731;self.assertEqual(m.step()['arguments'],[731,419])

    def test_query_pending_and_reply_immutability(self):
        m=FishingMachine(PLAN,CASES[0]['context'].get,879)
        while m.pc!=885:m.step()
        e=m.step();next_pc=m.pc;e['rect'][0]=0
        with self.assertRaises(FishingDependencyMissing):m.step()
        self.assertEqual(m.pc,next_pc)
        with self.assertRaises(ValueError):m.supply_query(0,0,0)
        m.supply_query(1304,279,999);self.assertEqual(m.values['query_return'],999)
        self.assertTrue(m.step()['result'])

    def test_rng_range_no_default_and_stop(self):
        m=FishingMachine(PLAN,CASES[0]['context'].get)
        while m.pc!=559:m.step()
        m.step()
        with self.assertRaises(FishingDependencyMissing):m.step()
        for value in (True,1232,1243):
            with self.assertRaises(ValueError):m.supply_random(value)
        m.stop();self.assertEqual(m.step()['reason'],'cancelled')
        with self.assertRaises(FishingDependencyMissing):m.supply_random(1233)

    def test_marker_is_explicit_and_reread(self):
        context=copy.deepcopy(CASES[0]['context']);context.pop('sdk_marker')
        m=FishingMachine(PLAN,context.get,879)
        while m.pc!=915:
            e=m.step()
            if e['kind']=='find_pic':m.supply_query(1304,279,0)
        with self.assertRaises(FishingDependencyMissing):m.step()
        self.assertEqual(m.pc,915);context['sdk_marker']='a1b2c3'
        e=m.step();self.assertEqual(e['color'],'a1b2c3-151515');m.supply_query(-1,-1,0)
        while m.pc!=915:m.step()
        context['sdk_marker']='332211';self.assertEqual(m.step()['color'],'332211-151515')

    def test_plan_is_snapshotted(self):
        plan=copy.deepcopy(PLAN);m=FishingMachine(plan,CASES[0]['context'].get)
        plan['actions'][0]['milliseconds']=999999
        self.assertEqual(m.step()['milliseconds'],145)


if __name__=='__main__':unittest.main()
