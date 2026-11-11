import importlib.util,json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'qmacro_potion.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_color import PixelImage
spec=importlib.util.spec_from_file_location('potion',PROJECT/'qmacro_potion.py');potion=importlib.util.module_from_spec(spec);spec.loader.exec_module(potion)
PLANS=json.loads((PROJECT/'data/potion-plans.json').read_text(encoding='utf-8'))['plans']

def replay(plan,results,use_f1=True,use_one=False):
    m=potion.PotionMachine(plan,use_f1,use_one);events=[];index=0
    for _ in range(10000):
        event=m.step();events.append(event)
        if event['kind']=='find_color':
            found=results[index];index+=1
            m.supply_color_result(event['rect'][0] if found else -1,event['rect'][1] if found else -1)
        if m.cycles==len(results):return m,events
    raise AssertionError('unexpected loop')

class PotionTests(unittest.TestCase):
    def test_exact_preserved_coverage(self):
        self.assertEqual(sum(len(p['actions']) for p in PLANS),208)
        for p in PLANS:
            self.assertEqual([x['record'] for x in p['actions']],list(range(p['entry'],p['last']+1)))
            self.assertFalse(p['original_records_missing'])
            find=[x for x in p['actions'] if x['kind']=='find_color']
            self.assertEqual(len(find),1);self.assertEqual(find[0]['dispid'],38)
            self.assertEqual(find[0]['similarity'],0.9);self.assertEqual(find[0]['direction'],0)
            self.assertEqual(len(find[0]['color'].split('|')),17)
    def test_color_present_never_uses_potion(self):
        for p in PLANS:
            m,events=replay(p,[True]*6,True,True)
            self.assertEqual(m.state['misses'],0)
            self.assertFalse(any(e['kind'] in ('key','key_down','key_up') for e in events))
    def test_three_absences_all_key_checkbox_combinations(self):
        for p in PLANS:
            for f1 in (False,True):
                for one in (False,True):
                    with self.subTest(entry=p['entry'],f1=f1,one=one):
                        m,events=replay(p,[False]*3,f1,one)
                        actual=[(e['kind'],e['key']) for e in events if e['kind'] in ('key','key_down','key_up')]
                        expected=[]
                        for enabled,key in ((f1,'F1'),(one,'1')):
                            if enabled:expected.extend((kind,key) for kind in ('key','key_down','key_up'))
                        self.assertEqual(actual,expected);self.assertEqual(m.state['misses'],0)
    def test_nonconsecutive_absences_reset_counter(self):
        for p in PLANS:
            m,events=replay(p,[False,False,True,False,False],True,True)
            self.assertEqual(m.state['misses'],2)
            self.assertFalse(any(e['kind'].startswith('key') for e in events))
            m,events=replay(p,[False,False,True,False,False,False])
            self.assertEqual(sum(e['kind']=='key' for e in events),1)
    def test_capture_error_cannot_become_low_hp(self):
        m=potion.PotionMachine(PLANS[0])
        for _ in range(30):
            e=m.step()
            if e['kind']=='find_color':break
        else:self.fail('no color request')
        with self.assertRaises(potion.MissingColorResult):m.step()
        self.assertEqual(m.state['misses'],0)
        with self.assertRaises(TypeError):m.supply_color_result(None,None)
        with self.assertRaises(ValueError):m.supply_color_result(0,0)
        self.assertIsNotNone(m.waiting)
        m.supply_color_result(-1,-1,0)
        self.assertIsNone(m.waiting)
    def test_only_x_output_controls_branch(self):
        for p in PLANS:
            m=potion.PotionMachine(p)
            for _ in range(30):
                e=m.step()
                if e['kind']=='find_color':break
            # Return value zero must not mean failure when the output coordinate was found.
            m.supply_color_result(p['rect'][0],p['rect'][1],0)
            for _ in range(30):
                m.step()
                if m.cycles:break
            self.assertEqual(m.state['misses'],0)
    def test_repeat_trigger_and_original_hold_release_delay(self):
        for p in PLANS:
            m,events=replay(p,[False]*6,True,True)
            self.assertEqual(sum(e['kind']=='key' for e in events),4)
            for i,e in enumerate(events):
                if e['kind']=='key_down':
                    following=events[i+1:]
                    delay=next(x for x in following if x['kind']=='delay')
                    release=next(x for x in following if x['kind']=='key_up')
                    self.assertEqual(delay['milliseconds'],50);self.assertEqual(e['key'],release['key'])
    def test_captured_pixels_drive_original_counter_and_key_decision(self):
        for p in PLANS:
            sequence=iter([True,False,False,False])
            def capture(x1,y1,x2,y2):
                rgb=bytes((145,16,10)) if next(sequence) else b'\x00\x00\x00'
                return PixelImage(x2-x1,y2-y1,rgb*((x2-x1)*(y2-y1)),(x1,y1))
            controller=potion.ColorBackedPotion(p,capture,True,False);events=[]
            for _ in range(1000):
                e=controller.step();events.append(e)
                if controller.machine.cycles==4:break
            self.assertEqual([e['found'] for e in events if e['kind']=='color_result'],[True,False,False,False])
            self.assertEqual([(e['kind'],e['key']) for e in events if e['kind'].startswith('key')],[('key','F1'),('key_down','F1'),('key_up','F1')])
    def test_capture_failure_keeps_request_and_counter(self):
        def broken_capture(*args):raise OSError('frame unavailable')
        c=potion.ColorBackedPotion(PLANS[0],broken_capture)
        for _ in range(20):
            event=c.step()
            if event['kind']=='find_color':break
        for _ in range(3):
            with self.assertRaises(OSError):c.step()
            self.assertEqual(c.machine.state['misses'],0)
            self.assertIsNotNone(c.request)

    def test_exclusive_capture_edges_are_not_valid_results(self):
        for plan in PLANS:
            machine=potion.PotionMachine(plan)
            for _ in range(30):
                event=machine.step()
                if event['kind']=='find_color':break
            x1,y1,x2,y2=event['rect']
            for x,y in ((x2,y1),(x1,y2)):
                with self.assertRaises(ValueError):machine.supply_color_result(x,y,1)
                self.assertIsNotNone(machine.waiting)
                self.assertEqual(machine.state['misses'],0)
            machine.supply_color_result(x1,y1,1)
            self.assertIsNone(machine.waiting)

if __name__=='__main__':unittest.main(verbosity=2)
