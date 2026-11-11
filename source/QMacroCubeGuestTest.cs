// Fixed isolated guest only. Original preserved VBScript; all effects owned.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Security.Cryptography;
using QMacroRebuild;

[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]public sealed class CubeVisionFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly Dictionary<string,object> spec,budget;
 readonly Dictionary<int,int> seen=new Dictionary<int,int>();
 [ComVisible(false)]public int Queries;
 public CubeVisionFixture(DryRunHost h,RecordVm v,Dictionary<string,object> s){host=h;vm=v;spec=s;budget=(Dictionary<string,object>)s["miss_budget"];}
 int Result(string kind,object[] args,int l,int t,out object x,out object y){
  int count;seen.TryGetValue(vm.Pc,out count);seen[vm.Pc]=++count;Queries++;object n;
  bool found=budget.TryGetValue(vm.Pc.ToString(),out n)?Convert.ToInt32(n)>=0&&count>Convert.ToInt32(n):(bool)spec["default_found"];
  x=found?l+1:-1;y=found?t+2:-1;int ret=kind=="find_color"?(found?1:0):(found?0:-1);
  if((bool)spec["inverted_return"])ret=ret==0?1:0;
  host.Record(vm,kind,new{arguments=args,x=x,y=y,return_value=ret});return ret;
 }
 public int FindColor(int l,int t,int r,int b,string color,double sim,int dir,out object x,out object y){return Result("find_color",new object[]{l,t,r,b,color,sim,dir},l,t,out x,out y);}
 public int FindPic(int l,int t,int r,int b,string path,string delta,double sim,int dir,out object x,out object y){return Result("find_pic",new object[]{l,t,r,b,path,delta,sim,dir},l,t,out x,out y);}
 public int MoveTo(int x,int y){host.Record(vm,"move_to",new[]{x,y});return 1;}
}
[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]public sealed class CubeSysIntent {
 readonly DryRunHost host;readonly RecordVm vm;
 public CubeSysIntent(DryRunHost h,RecordVm v){host=h;vm=v;}
 public int ExitOS(int flags){host.Record(vm,"os_exit_intent",new[]{flags});return 1;}
}
public static class CubeGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Sha(byte[] raw){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(raw)).Replace("-","").ToLowerInvariant();}
 static string Literal(object value){return value is string?"\""+((string)value).Replace("\"","\"\"")+"\"":Convert.ToInt32(value).ToString();}
 static bool Body(int at){return at>=857&&at<=1493||at>=5020&&at<=6442||at>=6740&&at<=6814;}
 static void Seed(DryRunHost host,Dictionary<string,object> values){foreach(var item in values)host.Globals.Set(item.Key,item.Value);}
 [STAThread]public static int Main(){string error=null;var cases=new List<object>();
  try{
   CallbackGuestTest.Guard();byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"cube-cases.json"));Check(Sha(raw)==CubeDigests.Cases,"Case digest changed");
   var specs=(object[])((Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=16000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw)))["cases"];Check(specs.Length==CubeDigests.CaseCount,"Case count");
   var original=ProgramReader.Read(Path.Combine(Lab,"07.json"),CubeDigests.Program);
   var frame=Regex.Match(original.Strings[0],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Check(frame.Success,"Frame names");
   int headerEnd=Array.FindIndex(original.Code,r=>r.Op==29);Check(headerEnd>0&&headerEnd<100,"Header boundary");
   var allowed=new HashSet<string>();for(int i=0;i<headerEnd;i++){
    string text=original.Strings[original.Code[i].Operand];Check(original.Code[i].Op==30&&(text.StartsWith("Dim ")||text.StartsWith("Class ")),"Header not declarations");
    Check(!Regex.IsMatch(text,@"\b(Call|CreateObject|Execute|GetObject|Eval)\b",RegexOptions.IgnoreCase),"Executable header");allowed.Add(text);
   }
   for(int i=0;i<original.Code.Length;i++)if(Body(i)&&(original.Code[i].Op==2||original.Code[i].Op==30))allowed.Add(original.Strings[original.Code[i].Operand]);
   foreach(object val in specs){var spec=(Dictionary<string,object>)val;int entry=Convert.ToInt32(spec["entry"]);
    Check(entry==857||entry==5020||entry==6740,"Unreviewed entry");int limit=Convert.ToInt32(spec["max_body_steps"]);Check(limit>0&&limit<=6000,"Case bound");
    var expanded=new Instruction[original.Code.Length+2];Array.Copy(original.Code,expanded,original.Code.Length);expanded[original.Code.Length]=new Instruction(12,entry);expanded[original.Code.Length+1]=new Instruction(23);
    var p=new MacroProgram(){Name=original.Name,Strings=original.Strings,Code=expanded};foreach(int missing in original.Missing)p.Missing.Add(missing);
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,original.Code.Length)){
     var fixture=new CubeVisionFixture(host,vm,spec);vm.AddOwnedObject("QMacroCubeVision",fixture);
     host.LibraryProvider=(context,name)=>{Check(context==vm&&name=="SYS","Unexpected native library");host.Record(vm,"load_service_intent",name);return new CubeSysIntent(host,vm);};
     int n=0;while(vm.Pc!=original.Code.Length&&n++<100)vm.Step();Check(vm.Pc==original.Code.Length,"Header scaffold");
     int caller=Array.FindIndex(original.Code,r=>r.Op==12&&r.Operand==entry);Check(caller>0,"Retained caller");
     var cls=Regex.Match(original.Strings[original.Code[caller-1].Operand],@"=New ([A-Za-z_0-9]+):Set [A-Za-z_0-9]+\.([A-Za-z_0-9]+)=");Check(cls.Success,"Retained call frame");
     vm.ExecuteOwnedSetup("Set "+frame.Groups[1].Value+"=New "+cls.Groups[1].Value+":Set "+frame.Groups[1].Value+"."+cls.Groups[2].Value+"=Nothing:Set DM=QMacroCubeVision");
     var shared=(Dictionary<string,object>)spec["shared"];Seed(host,shared);
     foreach(var item in (Dictionary<string,object>)spec["values"]){Check(Regex.IsMatch(item.Key,@"^[A-Za-z_][A-Za-z_0-9]*$"),"Invalid owned value name");vm.ExecuteOwnedSetup(item.Key+"="+Literal(item.Value));}
     Check(((Dictionary<string,object>)spec["frame_slots"]).Count==0,"Only explicit new-frame fixtures reviewed");
     var updates=(Dictionary<string,object>)spec["updates"];var visited=new List<int>();var draws=new List<object>();var access=new List<object>();int steps=0,lastBody=-1;
     while(vm.State!=RunState.Finished&&vm.State!=RunState.IterationEnded){int at=vm.Pc;if(Body(at)&&visited.Count>=limit)break;Check(++steps<6200,"Step bound");
      object update;if(updates.TryGetValue(at.ToString(),out update))Seed(host,(Dictionary<string,object>)update);
      Instruction instruction=original.Code[Math.Min(at,original.Code.Length-1)];if(Body(at)){visited.Add(at);lastBody=at;}
      vm.Step();
      if(Body(at)&&(instruction.Op==27||instruction.Op==28))access.Add(new{record=at,kind=instruction.Op==27?"read_global":"write_global",key=original.Strings[instruction.Operand],value=vm.Evaluate(RecordVm.Temp)});
      if(Body(at)&&(instruction.Op==2||instruction.Op==30)){
       var random=Regex.Match(original.Strings[instruction.Operand],@"^(XXX|YYY)=INT\((30|20)\*RND\+(INTX|INTY)\)$");
       if(random.Success){string name=random.Groups[1].Value;int span=Convert.ToInt32(random.Groups[2].Value),lower=Convert.ToInt32(vm.Evaluate(random.Groups[3].Value)),actual=Convert.ToInt32(vm.Evaluate(name));
        Check(actual>=lower&&actual<lower+span,"Original RNG bounds");int controlled=lower+((bool)spec["random_upper"]?span-1:0);draws.Add(new{record=at,original_value=actual,controlled_value=controlled});vm.ExecuteOwnedSetup(name+"="+controlled);
       }
      }
     }
     bool returned=vm.State==RunState.IterationEnded,stopped=vm.State==RunState.Finished;
     if(returned){Check(Convert.ToBoolean(vm.Evaluate(frame.Groups[1].Value+" Is Nothing")),"Root frame not restored");Check(Convert.ToBoolean(vm.Evaluate("IsEmpty("+RecordVm.Temp+")")),"Return not Empty");}
     var final=new Dictionary<string,object>();foreach(string key in shared.Keys)final[key]=host.Globals.Get(key);
     cases.Add(new{id=Convert.ToInt32(spec["id"]),records=visited,events=host.Snapshot(),reason=returned?"routine_return":stopped?"script_stop":"fixture_stop",
      next_record=returned?lastBody+1:vm.Pc,query_count=fixture.Queries,shared_accesses=access,final_shared=final,root_frame_restored=returned,return_is_empty=returned,original_rng_draws=draws});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  File.WriteAllText(Path.Combine(Lab,"original-cube-routines.json"),new JavaScriptSerializer(){MaxJsonLength=64000000}.Serialize(new{
   ok=error==null,error=error,cases=cases,case_count=cases.Count,source_program_sha256=CubeDigests.Program,case_spec_sha256=CubeDigests.Cases,
   runtime_sha256=Sha(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),original_body_executed=true,body_source_rewritten=false,
   original_native_loaded=false,game_input_sent=false,system_exit_executed=false,sdk_marker_is_synthetic_test_data=true,
   random_overridden_after_original_assignment=true,original_rng_equivalent=false,original_timing_verified=false,full_module_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
