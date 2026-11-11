"""Owned translation checks. Original-body guest replay is a separate gate."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'outputs/QMacro-Rebuild-Development' if (ROOT/'outputs').exists() else ROOT
sys.path.insert(0,str(ROOT/'work') if (ROOT/'work').exists() else str(PROJECT))
from qmacro_revival import RevivalMachine,RevivalDependencyMissing
PLAN=json.loads((PROJECT/'data/revival-plan.json').read_text(encoding='utf-8'))

def provider(role):return {'sdk_marker':'112233','skill_worker':41,'potion_worker':42}[role]
def run(failure,invert=False,read_global=provider):
    machine=RevivalMachine(PLAN,read_global);events=[];queries=0
    for _ in range(1000):
        e=machine.step();events.append(e);kind=e['kind']
        if kind=='configure_mouse':machine.supply_mouse_configuration(1)
        elif kind=='read_cursor':machine.supply_cursor(731,419)
        elif kind in ('find_color','find_pic'):
            stage=queries%(failure or 8)+1;queries+=1;found=failure==0 or stage!=failure
            value=(1 if found else 0) if kind=='find_color' else (0 if found else -1)
            if invert:value=int(value==0)
            machine.supply_query(e['rect'][0] if found else -1,e['rect'][1] if found else -1,value)
        if machine.cycles==2:return machine,events,queries
    raise AssertionError('Unbounded owned revival fixture')

class RevivalTests(unittest.TestCase):
    def test_complete_original_record_mapping(self):
        self.assertEqual([a['record'] for a in PLAN['actions']],list(range(1551,1639)))
        self.assertFalse(PLAN['original_missing_records']);self.assertIsNone(PLAN['sdk_marker_default'])
        guest=PROJECT/'verification/original-revival-vm-test.json'
        expected=False
        if guest.exists():
            report=json.loads(guest.read_text(encoding='utf-8-sig'));expected=report.get('ok') is True and report.get('completed_cases')==18
        self.assertEqual(PLAN['original_body_guest_replay_verified'],expected)
    def test_every_failure_short_circuits_before_any_mouse_or_thread_action(self):
        for failure in range(1,9):
            for inverted in (False,True):
                with self.subTest(stage=failure,invert=inverted):
                    _,events,count=run(failure,inverted)
                    self.assertEqual(count,2*failure)
                    self.assertFalse(any(e['kind'] in ('read_cursor','move_to','mouse_click','thread_control') for e in events))
    def test_success_pauses_clicks_restores_and_resumes_in_original_order(self):
        for inverted in (False,True):
            _,events,queries=run(0,inverted);self.assertEqual(queries,16)
            actual=[]
            for e in events:
                if e['kind']=='thread_control':actual.append(('thread',e['worker_id'],e['mode']))
                elif e['kind']=='move_to':actual.append(('move',e['x'],e['y']))
                elif e['kind']=='mouse_click':actual.append(('click',e['button'],e['count']))
                elif e['kind']=='read_cursor':actual.append(('cursor',))
            one=[('cursor',),('thread',41,1),('thread',42,1),('move',1377,345),('click',0,1),('move',1377,345),('click',0,1),('move',731,419),('thread',41,2),('thread',42,2)]
            self.assertEqual(actual,one*2)
    def test_worker_ids_are_reread_before_resume(self):
        reads={'skill_worker':0,'potion_worker':0}
        def changing(role):
            if role=='sdk_marker':return '112233'
            reads[role]+=1;return (41 if role=='skill_worker' else 42)+(30 if reads[role]%2==0 else 0)
        _,events,_=run(0,read_global=changing)
        actual=[(e['worker_id'],e['mode']) for e in events if e['kind']=='thread_control']
        self.assertEqual(actual,[(41,1),(42,1),(71,2),(72,2)]*2)
    def test_missing_sdk_marker_stops_at_original_read_and_can_retry(self):
        marker=None
        def read(role):return marker if role=='sdk_marker' else provider(role)
        m=RevivalMachine(PLAN,read)
        while m.pc!=1563:
            e=m.step()
            if e['kind']=='configure_mouse':m.supply_mouse_configuration(1)
        with self.assertRaises(RevivalDependencyMissing):m.step()
        self.assertEqual(m.pc,1563);marker='112233';self.assertEqual(m.step()['value'],marker)
    def test_no_query_result_is_not_a_negative_query_result(self):
        m=RevivalMachine(PLAN,provider)
        while m.pc!=1565:
            e=m.step()
            if e['kind']=='configure_mouse':m.supply_mouse_configuration(1)
        query=m.step();self.assertEqual(query['kind'],'find_color')
        with self.assertRaises(RevivalDependencyMissing):m.step()
        with self.assertRaises(ValueError):m.supply_query(query['rect'][2],query['rect'][1],1)
        with self.assertRaises(RevivalDependencyMissing):m.step()
        # Mutation of the public event must not alter the internal capture range.
        query['rect'][2]=5000
        with self.assertRaises(ValueError):m.supply_query(4000,1,1)
        m.supply_query(-1,-1,1);self.assertEqual(m.step()['kind'],'test');m.step();self.assertEqual(m.pc,1635)
    def test_configuration_and_cursor_replies_are_explicit(self):
        m=RevivalMachine(PLAN,provider)
        while m.pc!=1556:m.step()
        self.assertEqual(m.step()['kind'],'configure_mouse')
        with self.assertRaises(RevivalDependencyMissing):m.step()
        with self.assertRaises(TypeError):m.supply_mouse_configuration(None)
        m.supply_mouse_configuration(1)
        with self.assertRaises(RevivalDependencyMissing):m.supply_cursor(1,2)

if __name__=='__main__':unittest.main(verbosity=2)
