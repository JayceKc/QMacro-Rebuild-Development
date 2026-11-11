import hashlib,json,struct,unittest
from pathlib import Path
from recover_qmacro_key_info import restore_records,NEGATE
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
REPORT=json.loads((PROJECT/'verification/runner-protected-pairs.json').read_text())


class PairTests(unittest.TestCase):
    def test_native_cap_and_low_bit_selection(self):
        self.assertTrue(REPORT['ok']);rows={c['label']:c for c in REPORT['cases']}
        self.assertEqual(rows['cap-500']['eligible_positions'],list(range(500)))
        self.assertEqual(rows['cap-500']['export_count'],500)
        self.assertEqual(rows['no-protected-bit']['export_count'],0)
        self.assertEqual(rows['mixed-flags-17']['eligible_positions'],[i for i in range(17) if [0,1,2,3,0x80000001][i%5]&1])
        self.assertEqual(rows['partial-three']['changed_positions'],[0,1,2])
    def test_all_original_layouts_match_native_merge_byte_for_byte(self):
        self.assertEqual(len(REPORT['original_layout_cases']),8)
        for c in REPORT['original_layout_cases']:
            module=c['label'].rsplit('-',1)[1];path=PROJECT/'programs'/f'{module}.json';p=json.loads(path.read_text())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),c['source_program_sha256'])
            raw=b''.join(struct.pack('<BiiI',op,loc,arg,flag&0xffffffff) for op,loc,arg,flag in p['code'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),c['scrubbed_records_sha256'])
            decoded=struct.pack('<H',len(p['code'])).translate(NEGATE)+raw.translate(NEGATE);pairs=[(30,0)]*len(p['missing_records'])
            out,changes=restore_records(decoded,pairs,len(p['strings']))
            self.assertEqual(hashlib.sha256(out[2:].translate(NEGATE)).hexdigest(),c['native_restored_records_sha256'])
            self.assertEqual([x['record'] for x in changes],p['missing_records'])
    def test_synthetic_pairs_are_not_original_recovery(self):
        self.assertEqual(REPORT['original_missing_values_recovered'],0)
        self.assertTrue(REPORT['synthetic_pairs_only']);self.assertFalse(REPORT['native_script_or_os_calls_executed'])
        self.assertTrue(all(c['synthetic_pair_contents'] for c in REPORT['original_layout_cases']))


if __name__=='__main__':unittest.main()
