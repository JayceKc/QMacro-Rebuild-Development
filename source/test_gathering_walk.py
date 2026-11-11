from pathlib import Path
import json,sys,math,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'qmacro_gathering_walk.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_gathering_walk import Expression,evaluate,GatheringWalkMachine,WalkDependencyMissing,VbsNumericOverflow
from replay_gathering_walk import replay
PLAN=json.loads((PROJECT/'data/gathering-walk.json').read_text(encoding='utf8'))
CASES=json.loads((PROJECT/'data/gathering-walk-cases.json').read_text(encoding='utf8'))['cases']


class WalkTests(unittest.TestCase):
    def test_all_original_records_and_control_operands(self):
        source=json.loads((PROJECT/'programs/08.json').read_text(encoding='utf8'))
        self.assertEqual([a['record'] for a in PLAN['actions']],list(range(689,889)))
        for a in PLAN['actions']:
            op,location,arg,flags=source['code'][a['record']]
            self.assertEqual((op,location),(a['opcode'],a['location']))
            if a['source_sl'] is not None:self.assertEqual((a['source_sl'],a['source']),(arg,source['strings'][arg]))
            if op in (5,6,16):self.assertEqual(a['target'],arg if op==5 else a['record']+arg)

    def test_every_saved_native_path_angle_and_external_event(self):
        native=json.loads((PROJECT/'verification/original-gathering-walk.json').read_text(encoding='utf-8-sig'))
        self.assertTrue(native['ok']);self.assertEqual(len(native['cases']),146);covered=set()
        for case,original in zip(CASES,native['cases']):
            result=replay(PLAN,case);covered.update(result['records'])
            self.assertEqual((result['records'],result['reason'],result['angle_is_empty']),(original['records'],original['reason'],original['angle_is_empty']))
            if result['angle'] is None:self.assertIsNone(original['angle'])
            else:self.assertTrue(math.isclose(result['angle'],original['angle'],rel_tol=1e-12,abs_tol=1e-10))
            expected=[(e['record'],e['kind'],e['value']) for e in result['events'] if e['kind'] in ('delay','move_to','mouse_click')]
            self.assertEqual(expected,[(e['Record'],e['Kind'],e['Value']) for e in original['events']])
            if original['reason']=='numeric_overflow':self.assertIn('scode=800a0006',original['error_evidence'].lower())
        self.assertEqual(covered,set(range(689,889)))

    def test_coincident_target_keeps_original_error(self):
        a,b=[replay(PLAN,c) for c in CASES if c['expected_error']]
        self.assertEqual((a['reason'],b['reason']),('numeric_overflow','numeric_overflow'))
        self.assertEqual((a['angle'],b['angle']),(None,271))
        self.assertFalse(any(e['kind'] in ('move_to','mouse_click') for c in (a,b) for e in c['events']))

    def test_pending_rng_and_missing_pi_are_not_defaulted(self):
        case=next(c for c in CASES if c['label']=='ray' and c['context']['INTXX']!=1743 and c['context']['INTYY']!=168)
        context=dict(case['context']);context.pop(PLAN['pi_name']);m=GatheringWalkMachine(PLAN,context)
        while m.pc!=716:
            e=m.step()
            if e['kind']=='random_int':
                with self.assertRaises(WalkDependencyMissing):m.step()
                with self.assertRaises(ValueError):m.supply_random(0)
                m.supply_random(-1)
        with self.assertRaises(WalkDependencyMissing):m.step()
        self.assertEqual(m.pc,716)

    def test_numeric_grammar_excludes_source_execution(self):
        self.assertEqual(evaluate(Expression('Sgn((1<2) and (3>=2))').parse(),lambda n:None),-1)
        for source in ('CreateObject(1)','X[0]','Call Foo','1;2','"text"'):
            with self.assertRaises(ValueError):Expression(source).parse()
        with self.assertRaises(VbsNumericOverflow):evaluate(Expression('ATN((0)/(0))').parse(),lambda n:None)


if __name__=='__main__':unittest.main()
