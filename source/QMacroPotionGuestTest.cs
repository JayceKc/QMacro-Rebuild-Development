using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class DmColorFixture {
 readonly bool[] results;readonly DryRunHost host;readonly RecordVm vm;
 [ComVisible(false)]public int Index;
 [ComVisible(false)]public bool InvertReturn;
 public DmColorFixture(bool[] sequence,DryRunHost runtime,RecordVm context){results=sequence;host=runtime;vm=context;}
 public int SetShowErrorMsg(int value){host.Record(vm,"set_error_display",value);return 1;}
 public int FindColor(int x1,int y1,int x2,int y2,string color,double sim,int direction,out object x,out object y){
  if(Index>=results.Length)throw new Exception("Fixture color results exhausted");bool found=results[Index++];
  x=found?x1:-1;y=found?y1:-1;int ret=found?1:0;if(InvertReturn)ret=1-ret;
  host.Record(vm,"find_color",new{rect=new[]{x1,y1,x2,y2},color=color,similarity=sim,direction=direction,return_value=ret,x=x,y=y});return ret;
 }
}
public static class PotionGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Require(bool value,string message){if(!value)throw new Exception(message);}
 static void Reach(RecordVm vm,int pc){int n=0;while(vm.Pc!=pc&&n++<500)vm.Step();Require(vm.Pc==pc,"Fixture failed to reach entry");}
 [STAThread]public static int Main(){
  var cases=new List<object>();string error=null;
  try{
   CallbackGuestTest.Guard();byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"skill-vm-plan.json"));string digest;
   using(var h=SHA256.Create())digest=BitConverter.ToString(h.ComputeHash(raw)).Replace("-","").ToLowerInvariant();
   Require(digest==SkillPlanDigest.Value,"Class map changed");
   var data=(Dictionary<string,object>)new JavaScriptSerializer().DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
   var classes=(Dictionary<string,object>)data["classes"];
   MacroProgram p=ProgramReader.Read(Path.Combine(Lab,"10.json"),(string)data["program_sha256"]);
   var names=Regex.Match(p.Strings[p.Code[0].Operand],@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Require(names.Success,"Unknown frame names");
   int[] entries={1326,1379,1432,1485};string[] classLabels={"吃药11","吃药40","吃药70","吃药6"};
   bool[][] sequences={new[]{false,false,true,false,false,false},new[]{false,false,false,false,false,false},new[]{true,true,true}};
   for(int function=0;function<4;function++)for(int f1=0;f1<2;f1++)for(int one=0;one<2;one++)foreach(bool[] sequence in sequences){
    int entry=entries[function],last=entry+51,loop=entry+8;var allowed=new HashSet<string>(StringComparer.Ordinal);var globals=new List<string>();
    int headerEnd=Array.FindIndex(p.Code,r=>r.Op==29);
    for(int pc=0;pc<p.Code.Length;pc++){
     var r=p.Code[pc];if(pc>=entry&&pc<=last&&r.Op==27)globals.Add(p.Strings[r.Operand]);
     if((pc<headerEnd||pc>=entry&&pc<=last)&&(r.Op==2||r.Op==30))allowed.Add(p.Strings[r.Operand]);
    }
    Require(globals.Count==2,"Unexpected potion globals");
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,entry)){
     host.Globals.Set(globals[0],f1);host.Globals.Set(globals[1],one);
     var dm=new DmColorFixture(sequence,host,vm);vm.AddOwnedObject("QMacroOwnedDmFixture",dm);
     host.SourceRewrite=(context,s)=>String.Equals(s.Trim(),"SET DM=CREATEOBJECT(\"dm.dmsoft\")",StringComparison.OrdinalIgnoreCase)?"Set DM=QMacroOwnedDmFixture":s;
     Reach(vm,entry);vm.ExecuteOwnedSetup("Set "+names.Groups[1].Value+"=New "+(string)classes[classLabels[function]]+":g_iSimulateModeInVBSBlock=0");
     Reach(vm,loop);
     for(int cycle=0;cycle<sequence.Length;cycle++){int steps=0;do{vm.Step();steps++;}while(vm.Pc!=loop&&steps<500);Require(vm.Pc==loop,"Potion loop did not return");}
     Require(dm.Index==sequence.Length,"Wrong number of source color calls");
     int misses=0,triggers=0;foreach(bool found in sequence){if(found)misses=0;else if(++misses>=3){triggers++;misses=0;}}
     int f1Press=0,onePress=0,downs=0,ups=0;
     foreach(var e in host.Snapshot()){
      if(e.Kind=="key_press"){string key=Convert.ToString(((object[])e.Value)[0]);if(key=="F1")f1Press++;else if(key=="1")onePress++;else throw new Exception("Unexpected potion key");}
      if(e.Kind=="key_down")downs++;if(e.Kind=="key_up")ups++;
     }
     Require(f1Press==triggers*f1&&onePress==triggers*one&&downs==f1Press+onePress&&ups==downs,"Potion output lifecycle mismatch");
     cases.Add(new{entry=entry,use_f1=f1,use_one=one,results=sequence,triggers=triggers,f1_press=f1Press,one_press=onePress,events=host.Snapshot()});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  var report=new{ok=error==null,error=error,completed_cases=cases.Count,cases=cases,
    original_potion_bodies_executed=true,dm_constructor_replaced_with_controlled_fixture=true,
    captures_are_synthetic_results=true,game_input_sent=false,original_native_loaded=false,full_program_restored=false};
  File.WriteAllText(Path.Combine(Lab,"original-potion-vm-test.json"),new JavaScriptSerializer(){MaxJsonLength=16*1024*1024}.Serialize(report),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
