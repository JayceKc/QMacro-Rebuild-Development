import copy,hashlib,json,unittest
from pathlib import Path
from export_cube_routines import translate
from qmacro_cube import CubeMachine,CubeDependencyMissing
from build_cube_reading import graph

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/07.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
PLAN=json.loads((PROJECT/'data/cube-routines.json').read_text(encoding='utf8'))
RAW=json.loads((PROJECT/'programs/07.json').read_text(encoding='utf8'))
MODE='V8080D6BCA5D6CF9E4D6A65757378756D'
NEXT='V9FC0A2A5CEBFBCC64D6A65757378756D'
COUNTER='V8080D6BCC7B6BF904D6A65757378756D'
LAST='VF0ADACDECE99BF954D6A65757378756D'
SDK='V8186B4D47378756D'


def machine(entry,mode=0,character=1,last=24,overrides=None,provider=None):
    shared={MODE:mode,NEXT:character,COUNTER:0,LAST:last,SDK:'123456','VF0ADACDECCD2BFD14D6A65757378756D':1,
            'V86C8D9CDC7B6756D':0,'V9BB6D6D67378756D':1,'VF4C1DE94BBB6BB9C4D6A65757378756D':1,'V9BD1D187A1C3CCB54D6A65757378756D':1}
    shared.update(overrides or {})
    def read(key,pc):
        if key not in shared:raise CubeDependencyMissing('Unprovided shared key '+key)
        return shared[key]
    m=CubeMachine(PLAN,entry,provider or read,{'G_ISIMULATEMODEINVBSBLOCK':0,'V9D82B7DFBEB3C69B4D6A65757378756D':0},{})
    return m,shared


def run(m,shared,query=None,limit=6000):
    events=[]
    for _ in range(limit):
        if m.done:break
        e=m.step();events.append(e)
        if e['kind']=='write_global':shared[e['key']]=e['value']
        if e['kind'] in ('find_pic','find_color'):
            hit=query(e) if query else e['record']!=5153
            m.supply_query(e['rect'][0] if hit else -1,e['rect'][1] if hit else -1,0 if hit else 1)
        if e['kind']=='random_int':m.supply_random(e['lower']+e['span']-1)
    return events


class CubeTests(unittest.TestCase):
    def test_translation_matches_all_2135_original_records(self):
        rebuilt=translate(RAW)
        self.assertEqual(rebuilt['actions'],PLAN['actions'])
        self.assertEqual(hashlib.sha256((PROJECT/'programs/07.json').read_bytes()).hexdigest(),PLAN['source_program_sha256'])
        for a in PLAN['actions']:
            self.assertEqual(RAW['code'][a['record']],[a['opcode'],a['location'],a['operand'],a['field_3']])
            if a['source_sl'] is not None:self.assertEqual(RAW['strings'][a['source_sl']],a['source'])
        self.assertEqual(sum(a['kind']=='test' for a in PLAN['actions']),110)
        self.assertEqual(len(PLAN['callers']),39)
        self.assertTrue(PLAN['original_body_guest_verified'])
        self.assertFalse(PLAN['frame_lifecycle_verified'])

    def test_all_191_saved_original_paths_effects_globals_and_stop_positions(self):
        from compare_cube_cases import compare
        from replay_cube_cases import replay
        native=json.loads((PROJECT/'verification/original-cube-routines.json').read_text('utf8'))
        cases=json.loads((PROJECT/'data/cube-cases.json').read_text('utf8'))['cases']
        result=compare(native,{'ok':True,'cases':[replay(PLAN,c) for c in cases]})
        self.assertEqual((result['cases'],result['external_events'],result['records_covered']),(191,26668,2120))
        excluded={at for first,last in ((857,1493),(5020,6442),(6740,6814)) for at in graph([a for a in PLAN['actions'] if first<=a['record']<=last],first)['excluded_by_exit_or_constant_branch']}
        self.assertEqual({a['record'] for a in PLAN['actions']}-set(result['covered_records']),excluded)

    def test_all_nonconstant_conditional_edges_have_original_observations(self):
        native_path=PROJECT/'verification/original-cube-routines.json'
        native=json.loads(native_path.read_text('utf8'))
        report=json.loads((PROJECT/'verification/cube-original-vs-rebuild.json').read_text('utf8'))
        self.assertEqual(hashlib.sha256(native_path.read_bytes()).hexdigest(),report['original_guest_sha256'])
        self.assertEqual(hashlib.sha256((PROJECT/'data/cube-cases.json').read_bytes()).hexdigest(),native['case_spec_sha256'])
        successors={}
        for c in native['cases']:
            for at,nxt in zip(c['records'],c['records'][1:]):successors.setdefault(at,set()).add(nxt)
        by={a['record']:a for a in PLAN['actions']}
        constants=[];edge_count=0
        for a in PLAN['actions']:
            if a['kind']!='if_zero':continue
            at=a['record'];constant=by[at-1]['source']=='Sgn(vbTrue)'
            self.assertEqual(successors[at],{at+1} if constant else {at+1,a['target']})
            edge_count+=len(successors[at])
            if constant:constants.append(at)
        self.assertEqual((edge_count,constants),(218,[5133,6422]))

    def test_unknown_statement_is_rejected(self):
        raw=copy.deepcopy(RAW);raw['strings'][raw['code'][857][2]]='Call Unknown.Run(1)'
        with self.assertRaises(ValueError):translate(raw)

    def test_finish_modes_and_default_stop_at_original_exit(self):
        for mode,stop in ((-1,6811),(0,6746),(1,6757),(2,6796),(3,6807),(4,6811)):
            m,s=machine(6740,mode);events=run(m,s)
            self.assertEqual((m.reason,m.pc),('script_stop',stop));self.assertEqual(events[-1]['record'],stop)
            self.assertEqual([e['arguments'][0] for e in events if e['kind']=='key_press'],['F8','F8'] if mode==1 else ['Enter'] if mode==2 else [])
            self.assertEqual([e['arguments'] for e in events if e['kind']=='os_exit_intent'],[[1]] if mode==3 else [])
            self.assertFalse(m.frame_restore_requested)

    def test_each_elseif_rereads_shared_mode(self):
        def changing(key,pc):return {6741:99,6748:99,6759:99,6799:3}[pc]
        m,s=machine(6740,provider=changing);events=run(m,s)
        self.assertEqual(m.pc,6807)
        self.assertEqual([e['record'] for e in events if e['kind']=='read_global'],[6741,6748,6759,6799])

    def test_all_24_character_paths_and_global_writeback(self):
        for n in range(1,25):
            m,s=machine(5020,character=n);events=run(m,s)
            self.assertEqual(m.reason,'routine_return')
            self.assertEqual((s[NEXT],s[COUNTER]),(n+1,0));self.assertTrue(m.frame_restore_requested)
            self.assertEqual([e['record'] for e in events if e['kind']=='write_global'],[6402,6405])
            self.assertTrue(any(e['kind']=='find_pic' for e in events))
            self.assertIn(6426,[e['record'] for e in events])

    def test_equal_last_character_still_switches(self):
        m,s=machine(5020,character=24,last=24);run(m,s)
        self.assertEqual((m.reason,s[NEXT]),('routine_return',25))
        m,s=machine(5020,character=25,last=24);run(m,s)
        self.assertEqual((m.reason,m.pc,s[NEXT]),('script_stop',5052,25))

    def test_wait_loop_remains_running_and_can_be_cancelled(self):
        m,s=machine(5020);events=run(m,s,query=lambda e:False,limit=500)
        self.assertFalse(m.done);self.assertGreater(sum(e['record']==5153 for e in events),1)
        self.assertNotIn(6402,[e['record'] for e in events])
        m.stop();self.assertEqual((m.done,m.reason,m.pending),(True,'cancelled',None))

    def test_weekly_limits_skip_only_at_matching_mode_threshold(self):
        for mode in (1,2,3):
            m,s=machine(857,overrides={'V86C8D9CDC7B6756D':mode,COUNTER:mode});events=run(m,s)
            self.assertEqual(m.reason,'routine_return');self.assertFalse(any(e['kind']=='find_pic' for e in events))
            m,s=machine(857,overrides={'V86C8D9CDC7B6756D':mode,COUNTER:mode-1});events=run(m,s)
            self.assertTrue(any(e['kind']=='find_pic' for e in events));self.assertEqual(m.reason,'routine_return')

    def test_observations_and_random_samples_are_required(self):
        m,s=machine(857)
        for _ in range(700):
            e=m.step()
            if e['kind']=='find_pic':break
        with self.assertRaises(CubeDependencyMissing):m.step()
        with self.assertRaises(ValueError):m.supply_query(1920,1080,1)
        m.supply_query(e['rect'][0],e['rect'][1],0)
        for _ in range(50):
            e=m.step()
            if e['kind']=='random_int':break
        self.assertEqual((e['kind'],e['span']),('random_int',30))
        with self.assertRaises(ValueError):m.supply_random(e['lower']+e['span'])
        m.supply_random(e['lower'])
        self.assertIsNone(m.pending)

    def test_cfg_exit_boundaries_and_two_real_back_edges(self):
        for first,last in ((857,1493),(5020,6442),(6740,6814)):
            g=graph([a for a in PLAN['actions'] if first<=a['record']<=last],first)
            self.assertEqual(g['back_edges'],[{'record':5193,'target':5132},{'record':6431,'target':6421}] if first==5020 else [])
            for a in PLAN['actions']:
                if first<=a['record']<=last and a['kind']=='exit_script':self.assertEqual(g['edges'][a['record']],[])
        g=graph([a for a in PLAN['actions'] if 6740<=a['record']<=6814],6740)
        self.assertNotIn(6814,g['potentially_reachable']) # All paths stop before return; preserved, not deleted.


if __name__=='__main__':unittest.main()
