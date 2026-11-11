// Read-only GDI capture for the original physical-coordinate contract.
using System;
using System.Runtime.InteropServices;
namespace QMacroRebuild {
 public sealed class CaptureUnavailableException:InvalidOperationException {
  public CaptureUnavailableException(string message):base(message){}
 }
 public sealed class GdiFrameSampler {
  readonly Func<IntPtr,bool> acceptedForeground;
  public GdiFrameSampler(Func<IntPtr,bool> foregroundPolicy){if(foregroundPolicy==null)throw new ArgumentNullException("foregroundPolicy");acceptedForeground=foregroundPolicy;}
  [StructLayout(LayoutKind.Sequential)]struct Rect {public int Left,Top,Right,Bottom;}
  [StructLayout(LayoutKind.Sequential)]struct Point {public int X,Y;}
  [StructLayout(LayoutKind.Sequential)]struct BitmapInfo {
   public uint Size;public int Width,Height;public ushort Planes,Depth;public uint Compression,SizeImage;
   public int XPels,YPels;public uint ColorsUsed,ColorsImportant,FirstColor;
  }
  [DllImport("user32.dll")]static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")]static extern uint GetWindowThreadProcessId(IntPtr window,out uint processId);
  public static GdiFrameSampler ForLostArk(){return new GdiFrameSampler(window=>{
   uint pid;GetWindowThreadProcessId(window,out pid);if(pid==0)return false;
   try{using(var process=System.Diagnostics.Process.GetProcessById(checked((int)pid)))return String.Equals(process.ProcessName,"LOSTARK",StringComparison.OrdinalIgnoreCase);}catch(ArgumentException){return false;}catch(System.ComponentModel.Win32Exception){return false;}
  });}
  [DllImport("user32.dll",SetLastError=true)]static extern bool GetClientRect(IntPtr window,out Rect rect);
  [DllImport("user32.dll",SetLastError=true)]static extern bool ClientToScreen(IntPtr window,ref Point point);
  [DllImport("user32.dll",SetLastError=true)]static extern IntPtr SetThreadDpiAwarenessContext(IntPtr context);
  [DllImport("user32.dll",SetLastError=true)]static extern IntPtr GetDC(IntPtr window);
  [DllImport("user32.dll")]static extern int ReleaseDC(IntPtr window,IntPtr dc);
  [DllImport("gdi32.dll",SetLastError=true)]static extern IntPtr CreateCompatibleDC(IntPtr dc);
  [DllImport("gdi32.dll")]static extern bool DeleteDC(IntPtr dc);
  [DllImport("gdi32.dll",SetLastError=true)]static extern IntPtr CreateCompatibleBitmap(IntPtr dc,int width,int height);
  [DllImport("gdi32.dll",SetLastError=true)]static extern IntPtr SelectObject(IntPtr dc,IntPtr value);
  [DllImport("gdi32.dll")]static extern bool DeleteObject(IntPtr value);
  [DllImport("gdi32.dll",SetLastError=true)]static extern bool BitBlt(IntPtr dest,int x,int y,int width,int height,IntPtr source,int sx,int sy,uint operation);
  [DllImport("gdi32.dll",SetLastError=true)]static extern int GetDIBits(IntPtr dc,IntPtr bitmap,uint first,uint count,[Out] byte[] bits,ref BitmapInfo info,uint usage);
  [DllImport("gdi32.dll",SetLastError=true)]static extern uint SetPixel(IntPtr dc,int x,int y,uint color);
  static CaptureUnavailableException Fail(string message){return new CaptureUnavailableException(message+" (Win32 "+Marshal.GetLastWin32Error()+")");}
  internal static VisionFrame ReadBitmap(IntPtr dc,IntPtr bitmap,int width,int height,int originX,int originY){
   if(width<=0||height<=0||(long)width*height>1920*1080)throw new ArgumentException("Invalid capture dimensions");
   var info=new BitmapInfo(){Size=40,Width=width,Height=-height,Planes=1,Depth=32};
   var bgra=new byte[checked(width*height*4)];
   if(GetDIBits(dc,bitmap,0,(uint)height,bgra,ref info,0)!=height)throw Fail("GetDIBits failed");
   var rgb=new byte[checked(width*height*3)];for(int i=0,j=0;i<bgra.Length;i+=4,j+=3){rgb[j]=bgra[i+2];rgb[j+1]=bgra[i+1];rgb[j+2]=bgra[i];}
   return new VisionFrame(width,height,rgb,originX,originY);
  }
  public VisionFrame Capture(int x1,int y1,int x2,int y2){
   if(x1<0||y1<0||x1>=x2||y1>=y2||x2>1920||y2>1080)throw new CaptureUnavailableException("Invalid original 1920x1080 capture rectangle");
   IntPtr window=GetForegroundWindow();if(window==IntPtr.Zero||!acceptedForeground(window))throw new CaptureUnavailableException("Foreground is not accepted by the game policy");
   IntPtr prior;
   try{prior=SetThreadDpiAwarenessContext(new IntPtr(-4));}catch(EntryPointNotFoundException){throw new CaptureUnavailableException("Physical DPI context API unavailable");}
   if(prior==IntPtr.Zero)throw Fail("Cannot establish physical DPI coordinates");
   IntPtr screen=IntPtr.Zero,memory=IntPtr.Zero,bitmap=IntPtr.Zero,selected=IntPtr.Zero;
   try{
    Rect rect;Point origin=new Point();
    if(!GetClientRect(window,out rect)||!ClientToScreen(window,ref origin))throw Fail("Cannot read client geometry");
    if((long)rect.Right-rect.Left!=1920||(long)rect.Bottom-rect.Top!=1080||origin.X!=0||origin.Y!=0)throw new CaptureUnavailableException("Requires 1920x1080 client at physical screen origin (0,0)");
    screen=GetDC(IntPtr.Zero);if(screen==IntPtr.Zero)throw Fail("Cannot open capture DC");
    memory=CreateCompatibleDC(screen);if(memory==IntPtr.Zero)throw Fail("Cannot create memory DC");
    bitmap=CreateCompatibleBitmap(screen,x2-x1,y2-y1);if(bitmap==IntPtr.Zero)throw Fail("Cannot create capture bitmap");
    selected=SelectObject(memory,bitmap);if(selected==IntPtr.Zero||selected==new IntPtr(-1)){selected=IntPtr.Zero;throw Fail("Cannot select capture bitmap");}
    if(!BitBlt(memory,0,0,x2-x1,y2-y1,screen,x1,y1,0x00cc0020|0x40000000))throw Fail("Screen copy failed");
    IntPtr deselected=SelectObject(memory,selected);if(deselected==IntPtr.Zero||deselected==new IntPtr(-1))throw Fail("Cannot deselect capture bitmap");selected=IntPtr.Zero;
    var frame=ReadBitmap(screen,bitmap,x2-x1,y2-y1,x1,y1);
    if(GetForegroundWindow()!=window||!acceptedForeground(window))throw new CaptureUnavailableException("Foreground changed during capture");
    Rect after;Point afterOrigin=new Point();if(!GetClientRect(window,out after)||!ClientToScreen(window,ref afterOrigin)||after.Left!=rect.Left||after.Top!=rect.Top||after.Right!=rect.Right||after.Bottom!=rect.Bottom||afterOrigin.X!=origin.X||afterOrigin.Y!=origin.Y)throw new CaptureUnavailableException("Client geometry changed during capture");
    return frame;
   }finally{
    if(selected!=IntPtr.Zero&&memory!=IntPtr.Zero)SelectObject(memory,selected);
    if(bitmap!=IntPtr.Zero)DeleteObject(bitmap);if(memory!=IntPtr.Zero)DeleteDC(memory);if(screen!=IntPtr.Zero)ReleaseDC(IntPtr.Zero,screen);
    SetThreadDpiAwarenessContext(prior);
   }
  }
  // Only an owned 2x2 offscreen bitmap is read. This does not prove live capture.
  public static bool VerifyOffscreenPixelConversion(){
   IntPtr screen=GetDC(IntPtr.Zero),memory=IntPtr.Zero,bitmap=IntPtr.Zero,selected=IntPtr.Zero;
   try{
    if(screen==IntPtr.Zero)throw Fail("Offscreen test DC unavailable");memory=CreateCompatibleDC(screen);bitmap=CreateCompatibleBitmap(screen,2,2);
    if(memory==IntPtr.Zero||bitmap==IntPtr.Zero)throw Fail("Offscreen allocation failed");selected=SelectObject(memory,bitmap);
    if(selected==IntPtr.Zero||selected==new IntPtr(-1)){selected=IntPtr.Zero;throw Fail("Offscreen select failed");}
    byte[] expected={145,16,10,0,255,0,0,0,255,255,255,255};
    for(int i=0;i<4;i++){uint color=(uint)(expected[i*3]|expected[i*3+1]<<8|expected[i*3+2]<<16);if(SetPixel(memory,i%2,i/2,color)==0xffffffff)throw Fail("Offscreen SetPixel failed");}
    SelectObject(memory,selected);selected=IntPtr.Zero;var frame=ReadBitmap(screen,bitmap,2,2,10,20);byte[] actual=frame.CopyRgb();
    for(int i=0;i<expected.Length;i++)if(actual[i]!=expected[i])return false;return frame.OriginX==10&&frame.OriginY==20;
   }finally{if(selected!=IntPtr.Zero&&memory!=IntPtr.Zero)SelectObject(memory,selected);if(bitmap!=IntPtr.Zero)DeleteObject(bitmap);if(memory!=IntPtr.Zero)DeleteDC(memory);if(screen!=IntPtr.Zero)ReleaseDC(IntPtr.Zero,screen);}
  }
 }
}
