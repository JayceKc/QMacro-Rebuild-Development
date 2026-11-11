from pathlib import Path
import ctypes,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'work' if (ROOT/'work').exists() else ROOT))
from qmacro_screen import ScreenSampler,CaptureUnavailable,W
class ScreenTests(unittest.TestCase):
    def test_native_offscreen_bitmap_channel_and_row_order(self):
        sampler=ScreenSampler(lambda:False);screen=sampler.user.GetDC(None)
        self.assertTrue(screen)
        memory=sampler.gdi.CreateCompatibleDC(screen);bitmap=sampler.gdi.CreateCompatibleBitmap(screen,2,2)
        old=sampler.gdi.SelectObject(memory,bitmap)
        try:
            sampler.gdi.SetPixel.argtypes=[W.HDC,ctypes.c_int,ctypes.c_int,W.DWORD];sampler.gdi.SetPixel.restype=W.DWORD
            colors=[(145,16,10),(0,255,0),(0,0,255),(255,255,255)]
            for i,(r,g,b) in enumerate(colors):self.assertNotEqual(sampler.gdi.SetPixel(memory,i%2,i//2,r|(g<<8)|(b<<16)),0xffffffff)
            sampler.gdi.SelectObject(memory,old);old=None
            image=sampler.read_bitmap(screen,bitmap,2,2,(10,20))
            self.assertEqual([image.pixel(10+i%2,20+i//2) for i in range(4)],colors)
        finally:
            if old:sampler.gdi.SelectObject(memory,old)
            sampler.gdi.DeleteObject(bitmap);sampler.gdi.DeleteDC(memory);sampler.user.ReleaseDC(None,screen)
    def test_no_capture_when_foreground_unverified(self):
        sampler=ScreenSampler(lambda:False)
        with self.assertRaises(CaptureUnavailable):sampler.capture_region(652,959,656,972)
        with self.assertRaises(CaptureUnavailable):sampler.capture_region(652,959,3000,972)
if __name__=='__main__':unittest.main(verbosity=2)
