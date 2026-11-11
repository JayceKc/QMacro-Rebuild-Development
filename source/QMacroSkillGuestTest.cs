using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class SkillGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Require(bool condition,string message){if(!condition)throw new Exception(message);}
 static string Digest(byte[] b){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static void Boot(RecordVm vm,int entry){for(int i=0;i<500&&vm.Pc!=entry;i++)vm.Step();Require(vm.Pc==entry,"Bootstrap failed to reach fixture entry");}
 static string Keys(DryEvent[] events){var text=new StringBuilder();foreach(var item in events)if(item.Kind=="key_press")text.Append(Convert.ToString(((object[])item.Value)[0]));return text.ToString();}
 static int Count(string text,char key){int n=0;foreach(char c in text)if(c==key)n++;return n;}
 static DryRunHost Host(MacroProgram p,Dictionary<string,object> plan,int g,int speed){
  var allowed=new HashSet<string>(StringComparer.Ordinal);
  for(int i=0;i<p.Code.Length;i++){
   var r=p.Code[i];if(r.Op!=2&&r.Op!=30)continue;
   if(i>=355&&i<=1324||i<Array.FindIndex(p.Code,x=>x.Op==29)){
    string text=p.Strings[r.Operand];Require(!Regex.IsMatch(text,@"\b(CreateObject|GetObject|Execute|CallAPI2|Shell)\b",RegexOptions.IgnoreCase),"Unexpected effect in skill source");allowed.Add(text);
   }
  }
  var host=new DryRunHost(s=>allowed.Contains(s));
  host.Globals.Set((string)plan["g_key"],g);host.Globals.Set((string)plan["g_delay_key"],2);host.Globals.Set((string)plan["speed_key"],speed);return host;
 }
 [STAThread]public static int Main(){
  string error=null;var cases=new List<object>();
  try{
   CallbackGuestTest.Guard();byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"skill-vm-plan.json"));
   Require(Digest(raw)==SkillPlanDigest.Value,"Fixture plan identity mismatch");
   var serializer=new JavaScriptSerializer();var plan=(Dictionary<string,object>)serializer.DeserializeObject(Encoding.UTF8.GetString(raw));
   var program=ProgramReader.Read(Path.Combine(Lab,"10.json"),(string)plan["program_sha256"]);
   foreach(object value in (object[])plan["orders"]){
    var order=(Dictionary<string,object>)value;int entry=Convert.ToInt32(order["entry"]),call=Convert.ToInt32(order["call_record"]);
    Require(program.Code[call-1].Op==2&&program.Code[call].Op==12&&program.Code[call].Operand==entry,"Unknown original call setup");
    for(int sj=0;sj<4;sj++)for(int g=0;g<2;g++)using(var host=Host(program,plan,g,0))using(var vm=new RecordVm(program,host.Globals,host,call-1)){
     Boot(vm,call-1);vm.ExecuteOwnedSetup("SJ="+sj+":YC=100:g_iSimulateModeInVBSBlock=0");
     int steps=0;while(vm.Pc!=call+1&&steps++<1000)vm.Step();
     Require(vm.Pc==call+1&&vm.Depth==0,"Original skill routine did not return");
     string keys=Keys(host.Snapshot());string actual=keys.Replace("G","");var expected=new StringBuilder();
     foreach(char c in (string)order["expected_order"])expected.Append(c,sj<2?3:2);
     Require(actual==expected.ToString()&&Count(keys,'G')==(g==1?2:0),"Original skill order/G mismatch at "+entry+" SJ="+sj+" G="+g);
     cases.Add(new{kind="order",entry=entry,sj=sj,g=g,keys=keys,return_pc=vm.Pc,depth=vm.Depth,events=host.Snapshot()});
    }
   }
   string header=program.Strings[program.Code[0].Operand];var names=Regex.Match(header,@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Require(names.Success,"Frame header unrecognized");
   foreach(object value in (object[])plan["controllers"]){
    var controller=(Dictionary<string,object>)value;int entry=Convert.ToInt32(controller["entry"]),loop=Convert.ToInt32(controller["loop"]);
    for(int speed=0;speed<4;speed++)for(int g=0;g<2;g++)using(var host=Host(program,plan,g,speed))using(var vm=new RecordVm(program,host.Globals,host,entry)){
     Boot(vm,entry);string frame=(string)controller["class_name"];Require(Regex.IsMatch(frame,@"^[A-Za-z_0-9]+$"),"Unsafe frame identifier");
     vm.ExecuteOwnedSetup("Set "+names.Groups[1].Value+"=New "+frame+":g_iSimulateModeInVBSBlock=0");
     int steps=0;while(vm.Pc!=loop&&steps++<100)vm.Step();Require(vm.Pc==loop,"Controller initialization did not reach loop");
     int counter=9,previousKeyCount=0,threshold=Convert.ToInt32(controller["counter_threshold"]);string special=(string)controller["special_key"];
     var cycles=new List<object>();
     for(int cycle=0;cycle<4;cycle++){
      steps=0;do{vm.Step();steps++;}while(vm.Pc!=loop&&steps<2000);
      Require(vm.Pc==loop&&vm.Depth==0,"Controller failed to complete original loop");
      int sj=Convert.ToInt32(vm.Evaluate("SJ")),yc=Convert.ToInt32(vm.Evaluate("YC"));Require(sj>=0&&sj<4,"Original random branch out of range");
      string allKeys=Keys(host.Snapshot()),keys=allKeys.Substring(previousKeyCount);previousKeyCount=allKeys.Length;
      string skills=keys.Replace("G","").Replace("Z","").Replace("X","");var expected=new StringBuilder();
      string order=new[]{"QASWEDRF","SFQDAERW","WFRADQES","RWFSADEQ"}[sj];foreach(char key in order)expected.Append(key,sj<2?3:2);
      Require(skills==expected.ToString(),"Controller chose wrong original skill order");
      bool fire=threshold>0&&counter>=threshold;if(fire)counter=0;counter++;
      Require(Count(keys,'G')==(g==1?2:0)&&Count(keys,'Z')==(fire&&special=="Z"?2:0)&&Count(keys,'X')==(fire&&special=="X"?2:0),"Controller special key schedule mismatch: "+entry+" cycle="+cycle+" keys="+keys);
      int[] bases={66,270,600,1300};int[] widths={116,220,entry==959?600:400,1000};
      Require(yc>=bases[speed]&&yc<bases[speed]+widths[speed],"Original speed distribution out of range");
      cycles.Add(new{cycle=cycle,sj=sj,yc=yc,keys=keys,expected_counter=counter,loop_pc=vm.Pc,depth=vm.Depth});
     }
     cases.Add(new{kind="controller",entry=entry,speed=speed,g=g,cycles=cycles,events=host.Snapshot()});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  var report=new{ok=error==null,error=error,cases=cases,completed_cases=cases.Count,
   original_preserved_skill_bodies_executed=true,fixture_globals_and_controller_root_frame_supplied=true,
   original_native_loaded=false,game_input_sent=false,delays_are_virtual=true,full_program_restored=false};
  File.WriteAllText(Path.Combine(Lab,"original-skill-vm-test.json"),new JavaScriptSerializer(){MaxJsonLength=16*1024*1024}.Serialize(report),new UTF8Encoding(false));return error==null?0:1;
 }
}
