// Native mouse API observations on the fixed isolated guest, no button clicks.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
public static class MouseOracle {
 [StructLayout(LayoutKind.Sequential)]struct Point {public int X,Y;}
 [DllImport("user32.dll",SetLastError=true)]static extern bool GetCursorPos(out Point p);
 const string Root=@"C:\Users\Public\Documents\QMacroLab";
 [STAThread]public static int Main(){
  CallbackGuestTest.Guard();string error=null,version=null;var samples=new List<object>();var modes=new List<object>();
  bool pointerAccess=false;Point original=new Point();bool restored=false;
  try{
   if(Process.GetProcessesByName("LOSTARK").Length>0)throw new InvalidOperationException("No game process allowed in mouse oracle");
   pointerAccess=GetCursorPos(out original);
   using(var dm=GuestNativeDual.Open()){
    version=dm.Ver();if(version!="7.2450")throw new Exception("Unexpected native API version");dm.SetShowErrorMsg(0);
    try{
     foreach(int mode in new[]{0,2}){
      int configured=dm.EnableRealMouse(mode,10,60);modes.Add(new{mode=mode,delay=10,step=60,return_value=configured});
      var clock=Stopwatch.StartNew();int direct=dm.MoveTo(100,120);Point at;bool valid=GetCursorPos(out at);
      samples.Add(new{method="MoveTo",mode=mode,arguments=new[]{100,120},return_value=(object)direct,elapsed_ms=clock.Elapsed.TotalMilliseconds,cursor_valid=valid,cursor=new[]{at.X,at.Y}});
      foreach(int[] size in new[]{new[]{1,1},new[]{5,7},new[]{3,2}})for(int i=0;i<16;i++){
       clock.Restart();string ret=dm.MoveToEx(100,120,size[0],size[1]);valid=GetCursorPos(out at);
       samples.Add(new{method="MoveToEx",mode=mode,arguments=new[]{100,120,size[0],size[1]},return_value=(object)ret,elapsed_ms=clock.Elapsed.TotalMilliseconds,cursor_valid=valid,cursor=new[]{at.X,at.Y}});
      }
     }
    }finally{dm.EnableRealMouse(0,10,60);if(pointerAccess){dm.MoveTo(original.X,original.Y);Point now;restored=GetCursorPos(out now)&&now.X==original.X&&now.Y==original.Y;}}
   }
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(Root,"original-mouse-oracle.json"),new JavaScriptSerializer().Serialize(new{ok=error==null,error=error,version=version,samples=samples,modes=modes,
   original_cursor_accessible=pointerAccess,original_cursor_restored=restored,vmware_guest_guard=true,com_registration_changed=false,
   guest_pointer_movement_attempted=true,mouse_buttons_sent=false,game_process_absent=true,host_pointer_changed=false,
   timing_scope="Observed process runtime only; scheduling equivalence and RNG identity are not proven."}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
