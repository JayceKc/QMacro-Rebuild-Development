"""Small read-only Windows screen regions for original absolute-coordinate scripts."""
import ctypes
from ctypes import wintypes as W
from qmacro_color import PixelImage

class CaptureUnavailable(RuntimeError):pass
class RECT(ctypes.Structure):_fields_=[('left',W.LONG),('top',W.LONG),('right',W.LONG),('bottom',W.LONG)]
class POINT(ctypes.Structure):_fields_=[('x',W.LONG),('y',W.LONG)]
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_=[('biSize',W.DWORD),('biWidth',W.LONG),('biHeight',W.LONG),('biPlanes',W.WORD),('biBitCount',W.WORD),
              ('biCompression',W.DWORD),('biSizeImage',W.DWORD),('biXPelsPerMeter',W.LONG),('biYPelsPerMeter',W.LONG),('biClrUsed',W.DWORD),('biClrImportant',W.DWORD)]
class BITMAPINFO(ctypes.Structure):_fields_=[('header',BITMAPINFOHEADER),('colors',W.DWORD*1)]

class ScreenSampler:
    def __init__(self,game_ready):
        self.game_ready=game_ready;self.user=ctypes.WinDLL('user32',use_last_error=True);self.gdi=ctypes.WinDLL('gdi32',use_last_error=True)
        signature={
          'GetDC':([W.HWND],W.HDC),'ReleaseDC':([W.HWND,W.HDC],ctypes.c_int),
          'GetForegroundWindow':([],W.HWND),'GetClientRect':([W.HWND,ctypes.POINTER(RECT)],W.BOOL),
          'ClientToScreen':([W.HWND,ctypes.POINTER(POINT)],W.BOOL),
          'SetThreadDpiAwarenessContext':([W.HANDLE],W.HANDLE)}
        for name,(args,ret) in signature.items():fn=getattr(self.user,name);fn.argtypes=args;fn.restype=ret
        signature={
          'CreateCompatibleDC':([W.HDC],W.HDC),'DeleteDC':([W.HDC],W.BOOL),
          'CreateCompatibleBitmap':([W.HDC,ctypes.c_int,ctypes.c_int],W.HBITMAP),
          'SelectObject':([W.HDC,W.HANDLE],W.HANDLE),'DeleteObject':([W.HANDLE],W.BOOL),
          'BitBlt':([W.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,W.HDC,ctypes.c_int,ctypes.c_int,W.DWORD],W.BOOL),
          'GetDIBits':([W.HDC,W.HBITMAP,W.UINT,W.UINT,ctypes.c_void_p,ctypes.POINTER(BITMAPINFO),W.UINT],ctypes.c_int)}
        for name,(args,ret) in signature.items():fn=getattr(self.gdi,name);fn.argtypes=args;fn.restype=ret
    def read_bitmap(self,dc,bitmap,width,height,origin=(0,0)):
        info=BITMAPINFO();info.header.biSize=ctypes.sizeof(BITMAPINFOHEADER)
        info.header.biWidth=width;info.header.biHeight=-height;info.header.biPlanes=1;info.header.biBitCount=32
        buffer=ctypes.create_string_buffer(width*height*4)
        if self.gdi.GetDIBits(dc,bitmap,0,height,buffer,ctypes.byref(info),0)!=height:
            raise CaptureUnavailable('GetDIBits failed: '+str(ctypes.get_last_error()))
        raw=buffer.raw;rgb=bytearray(width*height*3)
        rgb[0::3]=raw[2::4];rgb[1::3]=raw[1::4];rgb[2::3]=raw[0::4]
        return PixelImage(width,height,rgb,origin)
    def capture_region(self,x1,y1,x2,y2):
        if not (0<=x1<x2<=1920 and 0<=y1<y2<=1080):raise CaptureUnavailable('Invalid original 1920x1080 rectangle')
        if not self.game_ready():raise CaptureUnavailable('Game is not in foreground')
        prior=self.user.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
        if not prior:raise CaptureUnavailable('Cannot establish physical pixel coordinates')
        screen=memory=bitmap=selected=None
        try:
            window=self.user.GetForegroundWindow();rect=RECT();origin=POINT()
            if not window or not self.user.GetClientRect(window,ctypes.byref(rect)) or not self.user.ClientToScreen(window,ctypes.byref(origin)):
                raise CaptureUnavailable('Cannot read client geometry')
            if (rect.right-rect.left,rect.bottom-rect.top,origin.x,origin.y)!=(1920,1080,0,0):
                raise CaptureUnavailable('Original image coordinates require client 1920x1080 at screen origin (0,0)')
            screen=self.user.GetDC(None);memory=self.gdi.CreateCompatibleDC(screen)
            bitmap=self.gdi.CreateCompatibleBitmap(screen,x2-x1,y2-y1)
            if not screen or not memory or not bitmap:raise CaptureUnavailable('Cannot create capture buffers')
            selected=self.gdi.SelectObject(memory,bitmap)
            if not selected or selected==ctypes.c_void_p(-1).value:
                selected=None;raise CaptureUnavailable('Cannot select capture bitmap')
            if not self.gdi.BitBlt(memory,0,0,x2-x1,y2-y1,screen,x1,y1,0x00CC0020|0x40000000):raise CaptureUnavailable('Screen copy failed')
            # GetDIBits requires that the bitmap is not selected into a DC.
            self.gdi.SelectObject(memory,selected);selected=None
            image=self.read_bitmap(screen,bitmap,x2-x1,y2-y1,(x1,y1))
            if self.user.GetForegroundWindow()!=window or not self.game_ready():raise CaptureUnavailable('Foreground changed during capture')
            return image
        finally:
            if selected and memory:self.gdi.SelectObject(memory,selected)
            if bitmap:self.gdi.DeleteObject(bitmap)
            if memory:self.gdi.DeleteDC(memory)
            if screen:self.user.ReleaseDC(None,screen)
            self.user.SetThreadDpiAwarenessContext(prior)
