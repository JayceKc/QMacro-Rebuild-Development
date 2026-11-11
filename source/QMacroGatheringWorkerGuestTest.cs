// Fixed guest only. Original polling body; one disclosed CreateObject rewrite
// binds an owned recorder. No native plugin, keyboard or timed delay is used.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Security.Cryptography;
using QMacroRebuild;
[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]public sealed class GatheringWorkerVisionFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly Dictionary<string,object> spec;
 public GatheringWorkerVisionFixture(DryRunHost h,RecordVm v,Dictionary<string,object> s){host=h;vm=v;spec=s;}
 public int SetShowErrorMsg(int value){host.Record(vm,"set_show_error",value);return 1;}
 int Result(string kind,object[] args,int top,out object x,out object y){
  int at=Convert.ToInt32(spec[kind=="find_color"?"color_result":"picture_result"]);x=at;y=at<0?-1:top+1;
  int ret=kind=="find_color"?(at>=0?1:0):(at>=0?0:-1);if((bool)spec["invert_return"])ret=ret==0?1:0;
  host.Record(vm,kind,new{arguments=args,x=x,y=y,return_value=ret});return ret;
 }
 public int FindColor(int l,int t,int r,int b,string color,double sim,int dir,out object x,out object y){return Result("find_color",new object[]{l,t,r,b,color,sim,dir},t,out x,out y);}
 public int FindPic(int l,int t,int r,int b,string path,string delta,double sim,int dir,out object x,out object y){return Result("find_pic",new object[]{l,t,r,b,path,delta,sim,dir},t,out x,out y);}
}
public static class GatheringWorkerGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Sha(byte[] raw){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(raw)).Replace("-","").ToLowerInvariant();}
 [STAThread]public static int Main(){string error=null;var cases=new List<object>();
  try{
   CallbackGuestTest.Guard();byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"gathering-worker-cases.json"));Check(Sha(raw)==GatheringWorkerDigests.Cases,"Case digest changed");
   var specRoot=(Dictionary<string,object>)new JavaScriptSerializer().DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));var specs=(object[])specRoot["cases"];Check(specs.Length==41,"Case count");
   var original=ProgramReader.Read(Path.Combine(Lab,"08.json"),GatheringWorkerDigests.Program);var frame=Regex.Match(original.Strings[0],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Check(frame.Success,"Frame identifiers");
   var shape=Regex.Match(original.Strings[1],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+),([A-Za-z_0-9]+)\(256\):End Class");Check(shape.Success,"Frame shape");
   int headerEnd=Array.FindIndex(original.Code,r=>r.Op==29);var allowed=new HashSet<string>();for(int i=0;i<headerEnd;i++)allowed.Add(original.Strings[original.Code[i].Operand]);
   for(int i=890;i<=914;i++)if(original.Code[i].Op==2||original.Code[i].Op==30)allowed.Add(original.Strings[original.Code[i].Operand]);
   foreach(object val in specs){var spec=(Dictionary<string,object>)val;var expanded=new Instruction[original.Code.Length+2];Array.Copy(original.Code,expanded,original.Code.Length);expanded[original.Code.Length]=new Instruction(12,890);expanded[original.Code.Length+1]=new Instruction(23);
    var p=new MacroProgram(){Name=original.Name,Strings=original.Strings,Code=expanded};foreach(int missing in original.Missing)p.Missing.Add(missing);
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,original.Code.Length)){
     int bootstrap=0;while(vm.Pc!=original.Code.Length&&bootstrap++<20)vm.Step();Check(vm.Pc==original.Code.Length,"Header scaffold");
     vm.AddOwnedObject("QMacroGatheringVision",new GatheringWorkerVisionFixture(host,vm,spec));
     host.SourceRewrite=(context,source)=>{if(context.Pc==891){Check(source=="SET DM=CREATEOBJECT(\"dm.dmsoft\")","Unexpected DM load");host.Record(context,"load_vision_intent","dm.dmsoft");return "Set DM=QMacroGatheringVision";}return source;};
     // Explicitly owned structural frame; no claim about the missing worker-start class.
     vm.ExecuteOwnedSetup("Class QMacroGatheringWorkerFrame:Dim "+shape.Groups[1].Value+","+shape.Groups[2].Value+","+shape.Groups[3].Value+"(256):End Class");
     vm.ExecuteOwnedSetup("Set "+frame.Groups[1].Value+"=New QMacroGatheringWorkerFrame:Set "+frame.Groups[1].Value+"."+shape.Groups[1].Value+"=Nothing:g_iSimulateModeInVBSBlock="+Convert.ToInt32(spec["simulation_mode"]));
     var visited=new List<int>();int loops=0,steps=0;object stop=spec["stop_before_record"];var markers=(object[])spec["sdk_markers"];
     vm.Step();Check(vm.Pc==890,"Owned call did not reach worker");
     while(steps++<600){int at=vm.Pc;if(stop!=null&&at==Convert.ToInt32(stop)||loops>=Convert.ToInt32(spec["iterations"]))break;
      Check(at>=890&&at<=914,"Worker left body");if(at==897)host.Globals.Set(original.Strings[original.Code[897].Operand],markers[loops%markers.Length]);
      visited.Add(at);vm.Step();if(at==912)loops++;
     }
     Check(steps<600,"Worker bound exceeded");Check(!visited.Contains(913)&&!visited.Contains(914),"Unexpected normal cleanup/return");
     cases.Add(new{id=Convert.ToInt32(spec["id"]),records=visited,events=host.Snapshot(),next_record=vm.Pc,loops=loops,reason="fixture_stop"});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  File.WriteAllText(Path.Combine(Lab,"original-gathering-worker.json"),new JavaScriptSerializer(){MaxJsonLength=16000000}.Serialize(new{
   ok=error==null,error=error,cases=cases,case_count=cases.Count,source_program_sha256=GatheringWorkerDigests.Program,case_spec_sha256=GatheringWorkerDigests.Cases,
   runtime_sha256=Sha(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),original_body_executed=true,original_control_records_changed=false,
   createobject_source_rewritten_to_owned_recorder=true,owned_frame_shape_not_original_worker_identity=true,fixture_stops_before_instruction=true,
   original_native_loaded=false,game_input_sent=false,sdk_marker_is_synthetic_test_data=true,original_timing_verified=false,original_cancellation_protocol_verified=false,full_module_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
