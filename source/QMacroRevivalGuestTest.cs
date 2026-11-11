// Fixed guest only. Original death-monitor body, synthetic query results,
// recording-only mouse/cursor/thread ports. No original native code or input.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class RevivalFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly int failAt;readonly bool inverted;
 [ComVisible(false)]public int Queries;
 public RevivalFixture(DryRunHost h,RecordVm context,int failure,bool flip){host=h;vm=context;failAt=failure;inverted=flip;}
 public int SetShowErrorMsg(int value){host.Record(vm,"set_error_display",value);return 1;}
 public int EnableRealMouse(int mode,int min,int max){host.Record(vm,"mouse_mode_request",new[]{mode,min,max});return 1;}
 int Result(string kind,object args,int hitX,int hitY,out object x,out object y){
  int slot=Queries++%(failAt==0?8:failAt);bool found=failAt==0||slot+1!=failAt;
  x=found?hitX:-1;y=found?hitY:-1;int ret=kind=="find_pic"?(found?0:-1):(found?1:0);
  if(inverted)ret=ret==0?1:0;
  host.Record(vm,kind,new{arguments=args,found=found,x=x,y=y,return_value=ret});return ret;
 }
 public int FindColor(int x1,int y1,int x2,int y2,string color,double sim,int direction,out object x,out object y){return Result("find_color",new object[]{x1,y1,x2,y2,color,sim,direction},x1,y1,out x,out y);}
 public int FindPic(int x1,int y1,int x2,int y2,string path,string delta,double sim,int direction,out object x,out object y){return Result("find_pic",new object[]{x1,y1,x2,y2,path,delta,sim,direction},x1,y1,out x,out y);}
 public void ReadCursor(out object x,out object y){x=731;y=419;host.Record(vm,"cursor_read",new[]{731,419});}
 public int MoveTo(int x,int y){host.Record(vm,"move_to",new[]{x,y});return 1;}
}
public static class RevivalGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Require(bool value,string message){if(!value)throw new Exception(message);}
 static void Reach(RecordVm vm,int pc){int n=0;while(vm.Pc!=pc&&n++<500)vm.Step();Require(vm.Pc==pc,"Unreachable fixture entry");}
 [STAThread]public static int Main(){
  var cases=new List<object>();string error=null;
  try{
   CallbackGuestTest.Guard();
   MacroProgram p=ProgramReader.Read(Path.Combine(Lab,"10.json"),CallbackProgramDigests.Module10);
   var data=(Dictionary<string,object>)new JavaScriptSerializer().DeserializeObject(File.ReadAllText(Path.Combine(Lab,"skill-vm-plan.json")));
   // Verify the plan just as other original-body fixtures do.
   using(var hash=System.Security.Cryptography.SHA256.Create())Require(BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes(Path.Combine(Lab,"skill-vm-plan.json")))).Replace("-","").ToLowerInvariant()==SkillPlanDigest.Value,"Class map digest mismatch");
   var classes=(Dictionary<string,object>)data["classes"];
   var frame=Regex.Match(p.Strings[p.Code[0].Operand],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Require(frame.Success,"Frame not identified");
   var allowed=new HashSet<string>(StringComparer.Ordinal);int headerEnd=Array.FindIndex(p.Code,r=>r.Op==29);
   for(int i=0;i<p.Code.Length;i++)if((i<headerEnd||i>=1551&&i<=1638)&&(p.Code[i].Op==2||p.Code[i].Op==30))allowed.Add(p.Strings[p.Code[i].Operand]);
   for(int failure=0;failure<=8;failure++)for(int flip=0;flip<2;flip++){
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,1551)){
     var fixture=new RevivalFixture(host,vm,failure,flip!=0);vm.AddOwnedObject("QMacroRevivalFixture",fixture);
     host.SourceRewrite=(context,s)=>s.Trim().Equals("SET DM=CREATEOBJECT(\"dm.dmsoft\")",StringComparison.OrdinalIgnoreCase)?"Set DM=QMacroRevivalFixture":s.Trim().Equals("Call GetCursorPos(MX,MY)",StringComparison.OrdinalIgnoreCase)?"Call QMacroRevivalFixture.ReadCursor(MX,MY)":s;
     // This marker is test data only; production SDK marker remains unknown.
     host.Globals.Set(p.Strings[p.Code[1563].Operand],"112233");
     host.Globals.Set(p.Strings[p.Code[1606].Operand],41);host.Globals.Set(p.Strings[p.Code[1610].Operand],42);
     Reach(vm,1551);vm.ExecuteOwnedSetup("Set "+frame.Groups[1].Value+"=New "+(string)classes["监控死亡"]+":g_iSimulateModeInVBSBlock=0");Reach(vm,1560);
     for(int cycle=0;cycle<2;cycle++){int steps=0;do{vm.Step();steps++;}while(vm.Pc!=1560&&steps<500);Require(vm.Pc==1560,"Monitor failed to return to loop");}
     Require(fixture.Queries==2*(failure==0?8:failure),"Wrong short-circuit query count");
     int clicks=0,moves=0,cursors=0,controls=0;var lifecycle=new List<string>();
     foreach(var e in host.Snapshot()){
      if(e.Kind=="mouse_click"){clicks++;lifecycle.Add("click");}
      if(e.Kind=="move_to"){moves++;int[] xy=(int[])e.Value;lifecycle.Add("move:"+xy[0]+","+xy[1]);}
      if(e.Kind=="cursor_read"){cursors++;lifecycle.Add("cursor");}
      if(e.Kind=="thread_control_unmatched"){controls++;int[] arg=(int[])e.Value;lifecycle.Add("thread:"+arg[0]+","+arg[1]);}
     }
     Require(clicks==(failure==0?4:0)&&moves==(failure==0?6:0)&&cursors==(failure==0?2:0)&&controls==(failure==0?8:0),"Premature/missing revival actions");
     if(failure==0){string expected="cursor|thread:41,1|thread:42,1|move:1377,345|click|move:1377,345|click|move:731,419|thread:41,2|thread:42,2";Require(String.Join("|",lifecycle.ToArray())==expected+"|"+expected,"Revival lifecycle changed");}
     cases.Add(new{first_failed_query=failure,inconsistent_return_value=flip!=0,cycles=2,queries=fixture.Queries,events=host.Snapshot()});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  File.WriteAllText(Path.Combine(Lab,"original-revival-vm-test.json"),new JavaScriptSerializer(){MaxJsonLength=16*1024*1024}.Serialize(new{
   ok=error==null,error=error,completed_cases=cases.Count,cases=cases,original_body_executed=true,
   source_rewrites=new[]{"DM constructor to managed fixture","GetCursorPos to recording cursor fixture"},
   sdk_marker_is_synthetic_test_data=true,original_sdk_marker_recovered=false,
   original_class_entry_mapping_inferred=true,thread_ids_are_unmatched_recording_intents=true,
   native_mouse_emulation_executed=false,original_native_loaded=false,game_input_sent=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
