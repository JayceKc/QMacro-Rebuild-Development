// Fixed guest only. Three intact original module08 bodies with owned effects.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Security.Cryptography;
using QMacroRebuild;
[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]public sealed class GatheringRoutineVisionFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly Dictionary<string,object> spec,budget;
 readonly Dictionary<int,int> seen=new Dictionary<int,int>();
 [ComVisible(false)]public int Queries;
 public GatheringRoutineVisionFixture(DryRunHost h,RecordVm v,Dictionary<string,object> s){host=h;vm=v;spec=s;budget=(Dictionary<string,object>)s["miss_budget"];}
 bool Found(){int count;seen.TryGetValue(vm.Pc,out count);seen[vm.Pc]=++count;Queries++;object n;return !budget.TryGetValue(vm.Pc.ToString(),out n)||count>Convert.ToInt32(n);}
 int Result(string kind,object[] args,int l,int t,out object x,out object y){bool found=Found();x=found?l+1:-1;y=found?t+2:-1;int ret=kind=="find_color"?(found?1:0):(found?0:-1);if((bool)spec["inverted_return"])ret=ret==0?1:0;
  host.Record(vm,kind,new{arguments=args,x=x,y=y,return_value=ret});return ret;}
 public int FindColor(int l,int t,int r,int b,string color,double sim,int dir,out object x,out object y){return Result("find_color",new object[]{l,t,r,b,color,sim,dir},l,t,out x,out y);}
 public int FindPic(int l,int t,int r,int b,string path,string delta,double sim,int dir,out object x,out object y){return Result("find_pic",new object[]{l,t,r,b,path,delta,sim,dir},l,t,out x,out y);}
 public int MoveTo(int x,int y){host.Record(vm,"move_to",new[]{x,y});return 1;}
 [ComVisible(false)]public object Builtin(RecordVm context,string name,object[] args){
  if(context!=vm||name!="builtin_color")throw new Exception("Unexpected builtin");bool found=Found();int x=found?Convert.ToInt32(args[0])+1:-1,y=found?Convert.ToInt32(args[1])+2:-1;int ret=found?x*8192+y:-8193;
  host.Record(vm,"builtin_observation",new{arguments=args,x=x,y=y,return_value=ret});return ret;
 }
}
public static class GatheringRoutinesGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Sha(byte[] raw){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(raw)).Replace("-","").ToLowerInvariant();}
 static string Literal(object value){return value is string?"\""+((string)value).Replace("\"","\"\"")+"\"":Convert.ToInt32(value).ToString();}
 static void Seed(RecordVm vm,DryRunHost host,Dictionary<string,object> values,Dictionary<string,string> names){
  foreach(var item in values){if(item.Key=="sdk_marker")host.Globals.Set("V8186B4D47378756D",item.Value);else if(item.Key=="worker_id")host.Globals.Set("V80B0DA86C3CC32BE83A5D23C3778756D",item.Value);else vm.ExecuteOwnedSetup(names[item.Key]+"="+Literal(item.Value));}
 }
 [STAThread]public static int Main(){string error=null;var cases=new List<object>();
  try{
   CallbackGuestTest.Guard();byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"gathering-cases.json"));Check(Sha(raw)==GatheringRoutinesDigests.Cases,"Case digest changed");
   var specs=(object[])((Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=16000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw)))["cases"];Check(specs.Length==129,"Case count");
   var original=ProgramReader.Read(Path.Combine(Lab,"08.json"),GatheringRoutinesDigests.Program);
   var frame=Regex.Match(original.Strings[0],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Check(frame.Success,"Frame names");
   var names=new Dictionary<string,string>();foreach(var item in new[]{new object[]{38,"repair_strategy"},new object[]{42,"vitality_finish_mode"},new object[]{51,"home_on_no_vitality"},new object[]{57,"home_on_no_durability"}})names.Add((string)item[1],original.Strings[(int)item[0]].Split('=')[0]);names.Add("simulation_mode","g_iSimulateModeInVBSBlock");
   int headerEnd=Array.FindIndex(original.Code,r=>r.Op==29);var allowed=new HashSet<string>();for(int i=0;i<headerEnd;i++)allowed.Add(original.Strings[original.Code[i].Operand]);
   for(int i=916;i<=1620;i++)if(i!=1276&&i!=1343&&(original.Code[i].Op==2||original.Code[i].Op==30))allowed.Add(original.Strings[original.Code[i].Operand]);
   foreach(object val in specs){var spec=(Dictionary<string,object>)val;int entry=Convert.ToInt32(spec["entry"]);var expanded=new Instruction[original.Code.Length+2];Array.Copy(original.Code,expanded,original.Code.Length);expanded[original.Code.Length]=new Instruction(12,entry);expanded[original.Code.Length+1]=new Instruction(23);
    var p=new MacroProgram(){Name=original.Name,Strings=original.Strings,Code=expanded};foreach(int missing in original.Missing)p.Missing.Add(missing);
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,original.Code.Length)){
     var fixture=new GatheringRoutineVisionFixture(host,vm,spec);host.BuiltinProvider=fixture.Builtin;vm.AddOwnedObject("QMacroGatheringRoutineVision",fixture);
     int n=0;while(vm.Pc!=original.Code.Length&&n++<20)vm.Step();Check(vm.Pc==original.Code.Length,"Header scaffold");
     int caller=entry==916?613:entry==1344?605:1155;var cls=Regex.Match(original.Strings[original.Code[caller].Operand],@"=New ([A-Za-z_0-9]+):Set [A-Za-z_0-9]+\.([A-Za-z_0-9]+)=");Check(cls.Success,"Retained call frame");
     vm.ExecuteOwnedSetup("Set "+frame.Groups[1].Value+"=New "+cls.Groups[1].Value+":Set "+frame.Groups[1].Value+"."+cls.Groups[2].Value+"=Nothing:Set DM=QMacroGatheringRoutineVision");
     Seed(vm,host,(Dictionary<string,object>)spec["context"],names);var updates=(Dictionary<string,object>)spec["updates"];var visited=new List<int>();var draws=new List<object>();int steps=0;
     while(vm.State!=RunState.Finished&&vm.State!=RunState.IterationEnded&&steps++<8000){int at=vm.Pc;object update;if(updates.TryGetValue(at.ToString(),out update))Seed(vm,host,(Dictionary<string,object>)update,names);
      if(at>=916&&at<=1620&&at!=1276&&at!=1343)visited.Add(at);vm.Step();
      if(at==938||at==940){string name=at==938?"XLX":"XLY";int lower=at==938?1233:695,span=at==938?20:15;int actual=Convert.ToInt32(vm.Evaluate(name));Check(actual>=lower&&actual<lower+span,"Original random bounds");int controlled=Convert.ToInt32(spec[at==938?"random_x":"random_y"]);draws.Add(new{record=at,original_value=actual,controlled_value=controlled});vm.ExecuteOwnedSetup(name+"="+controlled);}
     }
     Check(steps<8000,"Original body bound exceeded in case "+spec["id"]);bool returned=vm.State==RunState.IterationEnded;
     if(returned){Check(Convert.ToBoolean(vm.Evaluate(frame.Groups[1].Value+" Is Nothing")),"Root frame not restored");Check(Convert.ToBoolean(vm.Evaluate("IsEmpty("+RecordVm.Temp+")")),"Return not Empty");}
     cases.Add(new{id=Convert.ToInt32(spec["id"]),records=visited,events=host.Snapshot(),reason=returned?"routine_return":"script_stop",root_frame_restored=returned,return_is_empty=returned,query_count=fixture.Queries,original_rng_draws=draws});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  File.WriteAllText(Path.Combine(Lab,"original-gathering-routines.json"),new JavaScriptSerializer(){MaxJsonLength=64000000}.Serialize(new{
   ok=error==null,error=error,cases=cases,case_count=cases.Count,source_program_sha256=GatheringRoutinesDigests.Program,case_spec_sha256=GatheringRoutinesDigests.Cases,
   runtime_sha256=Sha(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),original_body_executed=true,body_source_rewritten=false,
   original_native_loaded=false,game_input_sent=false,sdk_marker_is_synthetic_test_data=true,worker_ids_are_unmatched_test_ids=true,real_worker_pause_resume_verified=false,
   random_overridden_after_original_assignment=true,original_rng_equivalent=false,original_timing_verified=false,full_module_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
