from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'qmacro_builtin_picture.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_builtin_picture import find_picture
from qmacro_color import PixelImage
from qmacro_builtin_color import BuiltinContractError


class PictureTests(unittest.TestCase):
    def test_all_saved_native_pixels(self):
        p=json.loads((PROJECT/'verification/builtin-picture-observations.json').read_text())
        self.assertEqual(len(p['cases']),220)
        for c in p['cases']:
            fw,fh=c['frame_size'];tw,th=c['template_size'];x,y=c['origin']
            def image(w,h,pixels,origin=(0,0)):
                return PixelImage(w,h,b''.join(bytes.fromhex(p) for p in pixels),origin)
            key=c['explicit_transparency'];key=None if key==-1 else tuple((key>>s)&255 for s in (16,8,0))
            result=find_picture(image(fw,fh,c['frame_rgb'],(x,y)),image(tw,th,c['template_rgb']),x,y,x+fw-1,y+fh-1,c['similarity'],key)
            self.assertEqual(result,tuple(c['found_xy']),c['label'])

    def test_equal_size_and_uniform_corner_quirks(self):
        template=PixelImage(2,2,bytes.fromhex('123456'*4))
        self.assertEqual(find_picture(template,template,0,0,1,1),(-1,-1))
        self.assertEqual(find_picture(PixelImage(3,3,bytes(27)),template,0,0,2,2),(0,0))

    def test_errors_do_not_become_absence(self):
        frame=PixelImage(2,2,bytes(12));template=PixelImage(1,1,bytes(3))
        for similarity in (.05,float('nan'),True):
            with self.assertRaises(BuiltinContractError):find_picture(frame,template,0,0,1,1,similarity)
        with self.assertRaises(BuiltinContractError):find_picture(frame,template,0,0,2,2)


if __name__=='__main__':unittest.main()
