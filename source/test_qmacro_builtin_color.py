"""Portable regression against saved bounded CPU observations, no emulation needed."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'qmacro_builtin_color.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_builtin_color import BuiltinContractError,color_contract,scan_points,find_color_ex,unpack_coordinates
from qmacro_color import PixelImage


class BuiltinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((PROJECT/'verification/builtin-color-contract.json').read_text())

    def test_original_thresholds(self):
        for c in self.report['threshold_cases']:
            rgb,threshold,exact=color_contract('40752b',c['similarity'])
            self.assertEqual(rgb,(43,117,64));self.assertEqual((threshold,exact),(c['threshold'],c['exact']))

    def test_all_saved_original_frames(self):
        for c in self.report['owned_replay_cases']:
            rgb=bytes(v for text in c['pixels_rgb'] for v in bytes.fromhex(text))
            x,y=c['origin'];w,h=c['width'],c['height']
            frame=PixelImage(w,h,rgb,(x,y))
            got=find_color_ex(frame,x,y,x+w-1,y+h-1,c['target_bgr'],c['scan_type'],c['similarity'])
            self.assertEqual(got,(c['packed'],*c['expected_xy']))

    def test_center_order_not_euclidean(self):
        for c in self.report['center_removal_cases']:
            x,y=c['origin']
            self.assertEqual([list(p) for p in scan_points(x,y,x+c['width']-1,y+c['height']-1,1)],c['order'])

    def test_wrapper_rounding_and_negative_mod(self):
        for packed,xy in ((-8193,(-1,-1)),(-1,(0,-1)),(8192+4096,(2,4096)),(2*8192+4096,(2,4096)),(8191,(1,8191))):
            self.assertEqual(unpack_coordinates(packed),xy)

    def test_capture_errors_not_misses(self):
        class Broken:
            origin=(0,0);width=height=1
            def pixel(self,x,y):raise OSError('capture failed')
        with self.assertRaises(OSError):find_color_ex(Broken(),0,0,0,0,'000000')
        with self.assertRaises(BuiltinContractError):find_color_ex(PixelImage(1,1,b'\0\0\0'),0,0,1,1,'000000')

    def test_unverified_api_shapes_rejected(self):
        for color,similarity in (('ffffff|000000',.9),('ffffff-010101',.9),('ffffff',float('nan')),('ffffff',.05)):
            with self.assertRaises(BuiltinContractError):color_contract(color,similarity)
        with self.assertRaises(BuiltinContractError):list(scan_points(0,0,1,1,2))


if __name__=='__main__':unittest.main()
