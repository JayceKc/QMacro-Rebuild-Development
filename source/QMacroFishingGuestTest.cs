// Original bodies only in the fixed isolated guest. All effects use owned stubs.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Security.Cryptography;
using QMacroRebuild;

[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class FishingVisionFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly int failure;readonly bool flip;
 readonly Dictionary<int,int> seen=new Dictionary<int,int>();
 [ComVisible(false)]public int Queries;
 public FishingVisionFixture(DryRunHost h,RecordVm context,int fail,bool inverted){host=h;vm=context;failure=fail;flip=inverted;}
 int Result(string kind,object[] args,int left,int top,out object x,out object y){
  int count;seen.TryGetValue(vm.Pc,out count);seen[vm.Pc]=++count;Queries++;
  bool found=vm.Pc!=failure||count!=1;x=found?left+1:-1;y=found?top+2:-1;
  int ret=kind=="find_color"?(found?1:0):(found?0:-1);if(flip)ret=ret==0?1:0;
  host.Record(vm,kind,new{arguments=args,x=x,y=y,return_value=ret});return ret;
 }
 public int FindColor(int l,int t,int r,int b,string color,double sim,int dir,out object x,out object y){return Result("find_color",new object[]{l,t,r,b,color,sim,dir},l,t,out x,out y);}
 public int FindPic(int l,int t,int r,int b,string path,string delta,double sim,int dir,out object x,out object y){return Result("find_pic",new object[]{l,t,r,b,path,delta,sim,dir},l,t,out x,out y);}
 public int MoveTo(int x,int y){host.Record(vm,"move_to",new[]{x,y});return 1;}
}
[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class FishingSystemFixture {
 readonly DryRunHost host;readonly RecordVm vm;
 public FishingSystemFixture(DryRunHost h,RecordVm context){host=h;vm=context;}
 public int ExitOS(int flags){host.Record(vm,"os_exit_intent",flags);return 1;}
}
public static class FishingGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Require(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Sha(byte[] raw){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(raw)).Replace("-","").ToLowerInvariant();}
 static string Quoted(string value){return "\""+value.Replace("\"","\"\"")+"\"";}
 static string Literal(object value){return value is string?Quoted((string)value):Convert.ToInt32(value).ToString(System.Globalization.CultureInfo.InvariantCulture);}
 static void Seed(RecordVm vm,Dictionary<string,object> fields,Dictionary<string,string> names){
  foreach(var item in fields){Require(names.ContainsKey(item.Key),"Unknown context role");vm.ExecuteOwnedSetup(names[item.Key]+"="+Literal(item.Value));}
 }
 [STAThread]public static int Main(){
  var completed=new List<object>();string error=null;
  try{
   CallbackGuestTest.Guard();
   byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"fishing-cases.json"));Require(Sha(raw)==FishingEvidenceDigests.Cases,"Case spec digest changed");
   var data=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=16000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
   var specs=(object[])data["cases"];Require(specs.Length==77,"Wrong case count");
   MacroProgram original=ProgramReader.Read(Path.Combine(Lab,"05.json"),FishingEvidenceDigests.Program);
   var names=new Dictionary<string,string>();
   foreach(var pair in new[]{new object[]{57,"repair_mode"},new object[]{53,"completion_mode"},new object[]{86,"slow_repair"},new object[]{68,"return_home"},new object[]{8,"sdk_marker"}})
    names.Add((string)pair[1],original.Strings[Convert.ToInt32(pair[0])].Split('=')[0]);
   names.Add("saved_cursor_x","MX");names.Add("saved_cursor_y","MY");names.Add("simulation_mode","g_iSimulateModeInVBSBlock");
   var frame=Regex.Match(original.Strings[0],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Require(frame.Success,"Frame variables missing");
   string current=frame.Groups[1].Value;
   var declarations=new string[]{original.Strings[1],original.Strings[2]};
   var allowed=new HashSet<string>(StringComparer.Ordinal);
   for(int i=0;i<3;i++)allowed.Add(original.Strings[i]);
   for(int i=541;i<=923;i++)if((i<=877||i>=879)&&(original.Code[i].Op==2||original.Code[i].Op==30))allowed.Add(original.Strings[original.Code[i].Operand]);
   foreach(object value in specs){
    var spec=(Dictionary<string,object>)value;int entry=Convert.ToInt32(spec["entry"]);
    var expanded=new Instruction[original.Code.Length+2];Array.Copy(original.Code,expanded,original.Code.Length);
    expanded[original.Code.Length]=new Instruction(12,entry);expanded[original.Code.Length+1]=new Instruction(23);
    var program=new MacroProgram(){Name=original.Name,Strings=original.Strings,Code=expanded};foreach(int missing in original.Missing)program.Missing.Add(missing);
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(program,host.Globals,host,original.Code.Length)){
     var fixture=new FishingVisionFixture(host,vm,Convert.ToInt32(spec["first_failed_record"]),(bool)spec["inverted_return"]);
     vm.AddOwnedObject("QMacroFishingVision",fixture);
     host.LibraryProvider=(context,name)=>{Require(name=="SYS","Unexpected original service");host.Record(context,"load_service_intent",name);return new FishingSystemFixture(host,context);};
     int header=0;while(vm.Pc!=original.Code.Length&&header++<10)vm.Step();Require(vm.Pc==original.Code.Length,"Header did not reach owned call scaffold");
     var cls=Regex.Match(declarations[entry==879?0:1],@"^Class ([A-Za-z_0-9]+):Dim ([A-Za-z_0-9]+),");Require(cls.Success,"Routine class missing");
     vm.ExecuteOwnedSetup("Set "+current+"=New "+cls.Groups[1].Value+":Set "+current+"."+cls.Groups[2].Value+"=Nothing:Set DM=QMacroFishingVision");
     Seed(vm,(Dictionary<string,object>)spec["context"],names);
     var updates=(Dictionary<string,object>)spec["updates"];var visited=new List<int>();var draws=new List<object>();
     int steps=0;
     while(vm.State!=RunState.Finished&&vm.State!=RunState.IterationEnded&&steps++<5000){
      int at=vm.Pc;object update;if(updates.TryGetValue(at.ToString(),out update))Seed(vm,(Dictionary<string,object>)update,names);
      if(at>=541&&at<=877||at>=879&&at<=923)visited.Add(at);
      vm.Step();
      if(at==559||at==561){string variable=at==559?"XLX":"XLY";int actual=Convert.ToInt32(vm.Evaluate(variable));int lower=at==559?1233:715,span=at==559?10:5;
       Require(actual>=lower&&actual<lower+span,"Original random result outside source interval");
       int controlled=Convert.ToInt32(spec[at==559?"random_x":"random_y"]);draws.Add(new{record=at,original_value=actual,controlled_value=controlled});
       vm.ExecuteOwnedSetup(variable+"="+controlled.ToString());
      }
     }
     Require(steps<5000,"Original body did not terminate within fixture bound");
     bool returned=vm.State==RunState.IterationEnded;
     if(returned){Require(Convert.ToBoolean(vm.Evaluate(current+" Is Nothing")),"Root frame did not restore Nothing");Require(Convert.ToBoolean(vm.Evaluate("IsEmpty("+RecordVm.Temp+")")),"Unassigned return field was not Empty");}
     completed.Add(new{id=Convert.ToInt32(spec["id"]),records=visited,events=host.Snapshot(),reason=returned?"routine_return":"script_stop",query_count=fixture.Queries,
                        original_rng_draws=draws,root_frame_restored=returned,return_is_empty=returned});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  File.WriteAllText(Path.Combine(Lab,"original-fishing-vm-test.json"),new JavaScriptSerializer(){MaxJsonLength=64000000}.Serialize(new{
   ok=error==null,error=error,completed_cases=completed.Count,cases=completed,source_program_sha256=FishingEvidenceDigests.Program,case_spec_sha256=FishingEvidenceDigests.Cases,
   original_body_executed=true,original_body_source_rewritten=false,original_native_loaded=false,game_input_sent=false,os_exit_called=false,
   owned_call_scaffold_appended=true,owned_dm_and_sys_stubs=true,random_state_overridden_after_original_assignment=true,original_rng_equivalent=false,
   sdk_marker_is_synthetic_test_data=true,original_timing_verified=false,full_module_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
