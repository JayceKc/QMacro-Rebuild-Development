import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
REPORT=json.loads((PROJECT/'verification/runner-record-field3.json').read_text(encoding='utf8'))


class FieldTests(unittest.TestCase):
    def test_normal_success_failure_and_encoded_buffers(self):
        self.assertTrue(REPORT['ok']);cases=REPORT['normal_text_cases'];self.assertEqual(len(cases),48)
        for c in cases:
            self.assertEqual((c['pc_after'],c['location_after'],c['buffer_restored']),(9,471,True))
            self.assertEqual(c['calls'][0]['text'],c['source'])
            self.assertEqual(len(c['calls']),1 if c['success'] else 2)
            self.assertFalse(any(r['offset']<13 and r['offset']+r['size']>9 for r in c['record_reads']))
    def test_final_dword_variants_have_identical_semantic_results(self):
        groups={}
        for c in REPORT['normal_text_cases']+REPORT['debug_dispatch_cases']:
            key=tuple(c[k] for k in ('opcode','source','success','debug_enabled','debug_mode','breakpoint_present','same_source_line','notify_debug_line','source_location'))
            semantic={k:c[k] for k in ('boundary','calls','record_reads','pc_after','location_after','buffer_restored')}
            if key in groups:self.assertEqual(groups[key],semantic)
            else:groups[key]=semantic
    def test_debug_step_and_breakpoint_boundaries_are_observed(self):
        cases=REPORT['debug_dispatch_cases'];self.assertEqual(len(cases),288)
        self.assertEqual({c['boundary'] for c in cases},{'next_dispatch','debug_pause_boundary'})
        for c in cases:
            self.assertFalse(any(r['offset']<13 and r['offset']+r['size']>9 for r in c['record_reads']))
    def test_scope_does_not_claim_all_field_semantics(self):
        self.assertFalse(REPORT['all_field_3_semantics_verified'])
        self.assertFalse(REPORT['original_script_executed']);self.assertFalse(REPORT['os_api_called'])


if __name__=='__main__':unittest.main()
