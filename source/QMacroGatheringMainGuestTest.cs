// Fixed guest only: intact suffix plus child bodies; no erased prefix execution.
using System;using System.Collections.Generic;using System.IO;using System.Runtime.InteropServices;using System.Text.RegularExpressions;using System.Web.Script.Serialization;using System.Security.Cryptography;using QMacroRebuild;
[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]public sealed class GatheringMainVisionFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly Dictionary<string,object> spec,budget;readonly Dictionary<int,int> seen=new Dictionary<int,int>();
 [ComVisible(false)]public int Queries;
 public GatheringMainVisionFixture(DryRunHost h,RecordVm v,Dictionary<string,object> s){host=h;vm=v;spec=s;budget=(Dictionary<string,object>)s["miss_budget"];}
 bool Found(){int n;seen.TryGetValue(vm.Pc,out n);seen[vm.Pc]=++n;Queries++;object b;return !budget.TryGetValue(vm.Pc.ToString(),out b)||n>Convert.ToInt32(b);}
 int Result(string kind,object[] args,int l,int t,out object x,out object y){bool found=Found();x=found?l+1:-1;y=found?t+2:-1;if(found&&(vm.Pc==541||vm.Pc==667)){var pt=(object[])spec["target_point"];x=Convert.ToInt32(pt[0]);y=Convert.ToInt32(pt[1]);}int ret=kind=="find_color"?(found?1:0):(found?0:-1);if((bool)spec["inverted_return"])ret=ret==0?1:0;host.Record(vm,kind,new{arguments=args,x=x,y=y,return_value=ret});return ret;}
 public int FindColor(int l,int t,int r,int b,string color,double sim,int dir,out object x,out object y){return Result("find_color",new object[]{l,t,r,b,color,sim,dir},l,t,out x,out y);}
 public int FindPic(int l,int t,int r,int b,string path,string delta,double sim,int dir,out object x,out object y){return Result("find_pic",new object[]{l,t,r,b,path,delta,sim,dir},l,t,out x,out y);}
 public int MoveTo(int x,int y){host.Record(vm,"move_to",new[]{x,y});return 1;}
 public int MoveToEx(int x,int y,int w,int h){host.Record(vm,"move_to_ex",new[]{x,y,w,h});return 1;}
 [ComVisible(false)]public object Builtin(RecordVm context,string name,object[] args){if(context!=vm||name!="builtin_color")throw new Exception("Unexpected builtin");bool found=Found();int x=found?Convert.ToInt32(args[0])+1:-1,y=found?Convert.ToInt32(args[1])+2:-1,ret=found?x*8192+y:-8193;host.Record(vm,"builtin_observation",new{arguments=args,x=x,y=y,return_value=ret});return ret;}
}
public static class GatheringMainGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Check(bool ok,string m){if(!ok)throw new Exception(m);}
 static string Sha(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static string Lhs(MacroProgram p,int record){return p.Strings[p.Code[record].Operand].Split('=')[0];}
 static string Literal(object v){return v==null?"Empty":v is string?"\""+((string)v).Replace("\"","\"\"")+"\"":Convert.ToDouble(v).ToString("R",System.Globalization.CultureInfo.InvariantCulture);}
 static void Seed(RecordVm vm,DryRunHost host,Dictionary<string,object> values,Dictionary<string,string> names){foreach(var x in values){if(x.Key=="sdk_marker")host.Globals.Set("V8186B4D47378756D",x.Value);else if(x.Key=="worker_id")host.Globals.Set("V80B0DA86C3CC32BE83A5D23C3778756D",x.Value);else vm.ExecuteOwnedSetup(names[x.Key]+"="+Literal(x.Value));}}
 [STAThread]public static int Main(){string error=null;var cases=new List<object>();try{
  CallbackGuestTest.Guard();var raw=File.ReadAllBytes(Path.Combine(Lab,"gathering-main-cases.json"));Check(Sha(raw)==GatheringMainDigests.Cases,"Case digest changed");var specs=(object[])((Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=16000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw)))["cases"];Check(specs.Length==74,"Case count");
  var p=ProgramReader.Read(Path.Combine(Lab,"08.json"),GatheringMainDigests.Program);var allowed=new HashSet<string>();int headerEnd=Array.FindIndex(p.Code,r=>r.Op==29);for(int i=0;i<headerEnd;i++)allowed.Add(p.Strings[p.Code[i].Operand]);
  for(int i=507;i<=1620;i++)if(!(i>=890&&i<=914)&&(p.Code[i].Op==2||p.Code[i].Op==30))allowed.Add(p.Strings[p.Code[i].Operand]);
  var frame=Regex.Match(p.Strings[0],@"^Dim ([A-Za-z_0-9]+)\(256\):Dim ([A-Za-z_0-9]+),");Check(frame.Success,"Root frame identifiers");string slots=frame.Groups[1].Value,current=frame.Groups[2].Value;
  var names=new Dictionary<string,string>();foreach(var x in new[]{new object[]{38,"repair_strategy"},new object[]{42,"vitality_finish_mode"},new object[]{51,"home_on_no_vitality"},new object[]{57,"home_on_no_durability"}})names.Add((string)x[1],p.Strings[(int)x[0]].Split('=')[0]);
  names.Add("gather_mode",Regex.Match(p.Strings[p.Code[593].Operand],@"Sgn\(([A-Za-z0-9_]+)=3\)").Groups[1].Value);names.Add("simulation_mode","g_iSimulateModeInVBSBlock");names.Add("minimap_center_x","XX1");names.Add("minimap_center_y","YY1");names.Add("walk_pi",p.Strings[81].Split('=')[0]);names.Add("walk_angle",Lhs(p,708));names.Add("fallback_attempts",Lhs(p,510));names.Add("walk_repeats",Lhs(p,516));names.Add("sdk_miss_count",Lhs(p,1278));
  foreach(string a in new[]{"x","y"})for(int n=1;n<=3;n++)names.Add("history_"+a+n,a.ToUpper()+n+a.ToUpper());
  foreach(object val in specs){var spec=(Dictionary<string,object>)val;int entry=Convert.ToInt32(spec["entry"]);using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,entry)){
   var fixture=new GatheringMainVisionFixture(host,vm,spec);host.BuiltinProvider=fixture.Builtin;vm.AddOwnedObject("QMacroGatheringMainVision",fixture);int header=0;while(vm.Pc!=entry&&header++<20)vm.Step();Check(vm.Pc==entry,"Root scaffold");vm.ExecuteOwnedSetup("Set DM=QMacroGatheringMainVision");Seed(vm,host,(Dictionary<string,object>)spec["context"],names);Seed(vm,host,(Dictionary<string,object>)spec["initial"],names);
   var records=new List<int>();var draws=new List<object>();int cycles=0,steps=0;string reason=null,errorEvidence=null;var random=(Dictionary<string,object>)spec["random_values"];
   try{while(steps++<15000){int at=vm.Pc;if(at==596&&cycles>=Convert.ToInt32(spec["max_main_cycles"])){reason="fixture_stop";break;}if(p.Missing.Contains(at)){records.Add(at);reason="missing_original_record";break;}if(at==p.Code.Length){vm.Step();Check(vm.State==RunState.Finished,"Root did not finish");reason="program_end";break;}
    Check(at>=507&&!(at>=890&&at<=914)&&!(at>=1622&&at<=1624),"Unexpected source entry");records.Add(at);vm.Step();if(at==687)cycles++;
    string variable=null,role=null;int lower=0,span=0;if(at==522||at==564){variable="YC";role="recovery_delay";lower=66;span=116;}else if(at==701||at==704){variable=at==701?"X":"Y";role=at==701?"walk_jitter_x":"walk_jitter_y";lower=-15;span=15;}else if(at==938||at==940){variable=at==938?"XLX":"XLY";role=at==938?"random_x":"random_y";lower=at==938?1233:695;span=at==938?20:15;}
    if(variable!=null){int actual=Convert.ToInt32(vm.Evaluate(variable));Check(actual>=lower&&actual<lower+span,"Original random bounds");int controlled=Convert.ToInt32(random[role]);draws.Add(new{record=at,original_value=actual,controlled_value=controlled});vm.ExecuteOwnedSetup(variable+"="+controlled);}
    if(vm.State==RunState.Finished){reason="script_stop";break;}
   }}catch(InvalidOperationException ex){if(!(bool)spec["expected_overflow"]||vm.Pc!=714||ex.ToString().IndexOf("scode=800a0006",StringComparison.OrdinalIgnoreCase)<0)throw;reason="numeric_overflow";errorEvidence=ex.ToString();}
   Check(reason!=null&&steps<15000,"Root bound exceeded case "+spec["id"]);Check((reason=="numeric_overflow")==((bool)spec["expected_overflow"]),"Expected fault mismatch");
   var rootSlots=new Dictionary<string,object>();for(int n=12;n<=16;n++)rootSlots.Add(n.ToString(),Convert.ToBoolean(vm.Evaluate("IsEmpty("+slots+"("+n+"))"))?null:vm.Evaluate(slots+"("+n+")"));
   var history=new Dictionary<string,object>();foreach(string a in new[]{"x","y"})for(int n=1;n<=3;n++)history.Add(a+n,vm.Evaluate(names["history_"+a+n]));
   cases.Add(new{id=Convert.ToInt32(spec["id"]),records=records,events=host.Snapshot(),reason=reason,next_record=vm.Pc,main_cycles=cycles,query_count=fixture.Queries,root_current_is_nothing=Convert.ToBoolean(vm.Evaluate(current+" Is Nothing")),root_slots=rootSlots,history=history,error_evidence=errorEvidence,original_rng_draws=draws});
  }}
 }catch(Exception ex){error=ex.ToString();}
 if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
 File.WriteAllText(Path.Combine(Lab,"original-gathering-main.json"),new JavaScriptSerializer(){MaxJsonLength=64000000}.Serialize(new{ok=error==null,error=error,cases=cases,case_count=cases.Count,source_program_sha256=GatheringMainDigests.Program,case_spec_sha256=GatheringMainDigests.Cases,runtime_sha256=Sha(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),original_body_executed=true,body_source_rewritten=false,original_native_loaded=false,game_input_sent=false,erased_prefix_executed=false,root_entry_reconstructed=false,prefix_dependent_initial_values_are_synthetic_test_inputs=true,random_overridden_after_original_assignment=true,original_rng_equivalent=false,original_timing_verified=false,field_3_semantics_verified=false,full_module_restored=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
