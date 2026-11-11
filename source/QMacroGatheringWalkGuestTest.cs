// Fixed VM only: original intact walk body, recording DM and controlled jitter.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Security.Cryptography;
using QMacroRebuild;
[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]public sealed class WalkVisionFixture {
 readonly DryRunHost host;readonly RecordVm vm;
 public WalkVisionFixture(DryRunHost h,RecordVm v){host=h;vm=v;}
 public int MoveTo(int x,int y){host.Record(vm,"move_to",new[]{x,y});return 1;}
}
public static class GatheringWalkGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Check(bool x,string message){if(!x)throw new Exception(message);}
 static string Sha(byte[] bytes){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
 [STAThread]public static int Main(){
  string error=null;var cases=new List<object>();
  try{
   CallbackGuestTest.Guard();byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"gathering-walk-cases.json"));Check(Sha(raw)==GatheringWalkDigests.Cases,"Case digest changed");
   var data=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=16000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));var specs=(object[])data["cases"];Check(specs.Length==146,"Walk case count");
   var original=ProgramReader.Read(Path.Combine(Lab,"08.json"),GatheringWalkDigests.Program);
   var frame=Regex.Match(original.Strings[0],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Check(frame.Success,"Walk frame names");
   var cls=Regex.Match(original.Strings[original.Code[546].Operand],@"=New ([A-Za-z_0-9]+):Set [A-Za-z_0-9]+\.([A-Za-z_0-9]+)=");Check(cls.Success,"Retained walk caller did not identify class");
   string angleName=original.Strings[original.Code[708].Operand].Split('=')[0];int headerEnd=Array.FindIndex(original.Code,r=>r.Op==29);
   var allowed=new HashSet<string>();for(int i=0;i<headerEnd;i++)allowed.Add(original.Strings[original.Code[i].Operand]);
   for(int i=689;i<=888;i++)if(original.Code[i].Op==2||original.Code[i].Op==30)allowed.Add(original.Strings[original.Code[i].Operand]);
   foreach(object value in specs){
    var spec=(Dictionary<string,object>)value;var expanded=new Instruction[original.Code.Length+2];Array.Copy(original.Code,expanded,original.Code.Length);expanded[original.Code.Length]=new Instruction(12,689);expanded[original.Code.Length+1]=new Instruction(23);
    var p=new MacroProgram(){Name=original.Name,Strings=original.Strings,Code=expanded};foreach(int missing in original.Missing)p.Missing.Add(missing);
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,original.Code.Length)){
     int start=0;while(vm.Pc!=original.Code.Length&&start++<20)vm.Step();Check(vm.Pc==original.Code.Length,"Walk header/scaffold");
     vm.AddOwnedObject("QMacroWalkVision",new WalkVisionFixture(host,vm));vm.ExecuteOwnedSetup("Set "+frame.Groups[1].Value+"=New "+cls.Groups[1].Value+":Set "+frame.Groups[1].Value+"."+cls.Groups[2].Value+"=Nothing:Set DM=QMacroWalkVision");
     foreach(var item in (Dictionary<string,object>)spec["context"])vm.ExecuteOwnedSetup(item.Key+"="+Convert.ToDouble(item.Value).ToString("R",System.Globalization.CultureInfo.InvariantCulture));
     var visited=new List<int>();var draws=new List<object>();string reason=null,errorEvidence=null;int steps=0;
     try{
      while(vm.State!=RunState.IterationEnded&&steps++<600){
       int at=vm.Pc;if(at>=689&&at<=888)visited.Add(at);vm.Step();
       if(at==701||at==704){string variable=at==701?"X":"Y";int originalDraw=Convert.ToInt32(vm.Evaluate(variable));Check(originalDraw>=-15&&originalDraw<0,"Original jitter outside source bounds");int controlled=Convert.ToInt32(spec[at==701?"random_x":"random_y"]);draws.Add(new{record=at,original_value=originalDraw,controlled_value=controlled});vm.ExecuteOwnedSetup(variable+"="+controlled);}
      }
      Check(steps<600,"Walk exceeded step bound");reason="routine_return";Check(!(bool)spec["expected_error"],"Expected coincident-target fault was not raised");
      Check(Convert.ToBoolean(vm.Evaluate(frame.Groups[1].Value+" Is Nothing")),"Walk frame not restored");
     }catch(InvalidOperationException ex){if(!(bool)spec["expected_error"]||vm.Pc!=714||ex.ToString().IndexOf("scode=800a0006",StringComparison.OrdinalIgnoreCase)<0)throw;reason="numeric_overflow";errorEvidence=ex.ToString();}
     bool empty=Convert.ToBoolean(vm.Evaluate("IsEmpty("+angleName+")"));object angle=empty?null:vm.Evaluate(angleName);
     cases.Add(new{id=Convert.ToInt32(spec["id"]),records=visited,events=host.Snapshot(),angle=angle,angle_is_empty=empty,reason=reason,error_evidence=errorEvidence,original_rng_draws=draws});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  File.WriteAllText(Path.Combine(Lab,"original-gathering-walk.json"),new JavaScriptSerializer(){MaxJsonLength=64000000}.Serialize(new{
   ok=error==null,error=error,cases=cases,case_count=cases.Count,source_program_sha256=GatheringWalkDigests.Program,case_spec_sha256=GatheringWalkDigests.Cases,
   runtime_sha256=Sha(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),original_body_executed=true,body_source_rewritten=false,
   owned_call_scaffold_appended=true,jitter_overridden_after_original_assignment=true,original_rng_equivalent=false,original_native_loaded=false,game_input_sent=false,full_module_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
