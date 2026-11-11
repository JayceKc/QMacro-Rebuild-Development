"""Portable owned decoder comparison to saved native row/conversion outputs."""
from pathlib import Path
import hashlib,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'qmacro_picture.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_picture import load_bmp


class BitmapTests(unittest.TestCase):
    def test_native_conversion_for_every_original_bmp_content(self):
        report=json.loads((PROJECT/'verification/builtin-bitmap-conversion.json').read_text())
        cases=[c for c in report['cases'] if c['kind']=='recovered_asset']
        self.assertEqual(len(cases),377)
        for c in cases:
            path=PROJECT/c['bundle_path'];raw=path.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),c['bmp_sha256'])
            frame=load_bmp(path)
            self.assertEqual(hashlib.sha256(frame.rgb).hexdigest(),c['native_rgb_sha256'],c['filename'])
            self.assertTrue(c['native_high_byte_zero'])

    def test_native_signed_height_and_padding(self):
        report=json.loads((PROJECT/'verification/builtin-bitmap-conversion.json').read_text())
        cases=[c for c in report['cases'] if c['kind']=='owned_fixture']
        self.assertEqual(len(cases),10)
        with tempfile.TemporaryDirectory(prefix='qmacro-owned-bmp-') as directory:
            path=Path(directory)/'fixture.bmp'
            for c in cases:
                path.write_bytes(bytes.fromhex(c['bmp_hex']));frame=load_bmp(path)
                self.assertEqual(hashlib.sha256(frame.rgb).hexdigest(),c['native_rgb_sha256'])


if __name__=='__main__':unittest.main()
