using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using QMacroRebuild;
[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class IslandWorkerDm {
 readonly DryRunHost host;readonly RecordVm vm;readonly bool[] finds;readonly bool invert;int index;
 public IslandWorkerDm(DryRunHost h,RecordVm v,bool[] values,bool flip=false){host=h;vm=v;finds=values;invert=flip;}
 public int SetShowErrorMsg(int value){host.Record(vm,"set_error_display",value);return 1;}
 public int FindPic(int a,int b,int c,int d,string files,string delta,double sim,int dir,out object x,out object y){
  if(index>=finds.Length)throw new Exception("Finder sequence exhausted");bool found=finds[index++];x=found?a+1:-1;y=found?b+2:-1;int ret=invert?(found?-1:0):(found?0:-1);host.Record(vm,"find_pic",new{arguments=new object[]{a,b,c,d,files,delta,sim,dir},x=x,y=y,return_value=ret});return ret;
 }
}
public static class IslandWorkersGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab",Digest="bbca57d0f39890c3c992f209ee00375e7909dd386efff576771a4ecc65cae204";
 static readonly int[] Orders={137,276,415,554},Controllers={693,757,808,872},Loops={699,762,814,878},SjAssignments={708,771,823,887};
 static void Require(bool condition,string message){if(!condition)throw new Exception(message);}
 static int Frame(MacroProgram p,int entry){for(int i=1;i<p.Code.Length;i++)if(p.Code[i].Op==12&&p.Code[i].Operand==entry&&p.Code[i-1].Op==2)return p.Code[i-1].Operand;throw new Exception("Original frame/call pair missing");}
 static MacroProgram Wrapped(MacroProgram original,int entry){var code=new List<Instruction>(original.Code);code.Add(new Instruction(2,Frame(original,entry)));code.Add(new Instruction(12,entry));code.Add(new Instruction(22));var p=new MacroProgram(){Name=original.Name,Strings=original.Strings,Code=code.ToArray()};foreach(int i in original.Missing)p.Missing.Add(i);return p;}
 static string Keys(DryEvent[] events,int offset){var result=new StringBuilder();for(int i=offset;i<events.Length;i++)if(events[i].Kind=="key_press")result.Append(Convert.ToString(((object[])events[i].Value)[0]));return result.ToString();}
 static string ExpectedOrder(MacroProgram p,int entry,int sj){
  int pc=entry;bool flag=false;var keys=new StringBuilder();
  for(int n=0;n<1000;n++){
   var r=p.Code[pc];if(r.Op==13)return keys.ToString();
   if(r.Op==4){string source=p.Strings[r.Operand];Require(Regex.IsMatch(source,@"\ASgn\(SJ=\d(?: or SJ=\d)*\)\z"),"Unreviewed order condition");flag=false;foreach(Match m in Regex.Matches(source,@"SJ=(\d)"))if(Int32.Parse(m.Groups[1].Value)==sj)flag=true;}
   else if(r.Op==6){if(!flag){pc+=r.Operand;continue;}}
   else if(r.Op==16){pc+=r.Operand;continue;}
   else if(r.Op==2||r.Op==30){var match=Regex.Match(p.Strings[r.Operand],"Call QMLibrary.KeyPress\\(\"([QWERASDF])\",g_iSimulateModeInVBSBlock,1\\)");if(match.Success)keys.Append(match.Groups[1].Value);}
   else throw new Exception("Unexpected order opcode");pc++;
  }throw new Exception("Expected order exceeded bound");
 }
 static DryRunHost Host(MacroProgram p){
  var allowed=new HashSet<string>(StringComparer.Ordinal);int header=Array.FindIndex(p.Code,r=>r.Op==29);
  for(int i=0;i<p.Code.Length;i++)if(i<header||i>=117&&i<=934||i>=1038){var r=p.Code[i];if(r.Op==2||r.Op==30)allowed.Add(p.Strings[r.Operand]);}
  var host=new DryRunHost(s=>allowed.Contains(s));host.SourceRewrite=(vm,s)=>s.Trim().Equals("SET DM=CREATEOBJECT(\"dm.dmsoft\")",StringComparison.OrdinalIgnoreCase)?"Set DM=QMacroIslandWorkerDm":s;return host;
 }
 static void Boot(RecordVm vm){for(int n=0;n<100&&vm.Pc!=1038;n++)vm.Step();Require(vm.Pc==1038,"Worker wrapper not reached");vm.ExecuteOwnedSetup("g_iSimulateModeInVBSBlock=0");}
 [STAThread]public static int Main(){
  CallbackGuestTest.Guard();var cases=new List<object>();string error=null;
  try{
   var original=ProgramReader.Read(Path.Combine(Lab,"09.json"),Digest);
   for(int order=0;order<4;order++)for(int sj=0;sj<4;sj++)foreach(int yc in new[]{66,181}){
    var p=Wrapped(original,Orders[order]);using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,1038)){
     Boot(vm);vm.ExecuteOwnedSetup("SJ="+sj+":YC="+yc);for(int n=0;n<1000&&vm.State!=RunState.Finished;n++)vm.Step();Require(vm.State==RunState.Finished&&vm.Depth==0,"Order failed to return");string expected=ExpectedOrder(p,Orders[order],sj);Require(Keys(host.Snapshot(),0)==expected,"Original VBScript key condition differs from closed SJ membership interpretation");
     cases.Add(new{kind="order",entry=Orders[order],sj=sj,yc=yc,keys=expected,events=host.Snapshot()});
    }
   }
   for(int controller=0;controller<4;controller++)for(int sj=0;sj<4;sj++){
    var p=Wrapped(original,Controllers[controller]);using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,1038)){
     vm.AddOwnedObject("QMacroIslandWorkerDm",new IslandWorkerDm(host,vm,new bool[0]));Boot(vm);int loop=Loops[controller];for(int n=0;n<100&&vm.Pc!=loop;n++)vm.Step();Require(vm.Pc==loop,"Controller loop not reached");var cycles=new List<object>();
     for(int cycle=0;cycle<4;cycle++){
      int offset=host.Snapshot().Length;bool set=false;for(int n=0;n<1000;n++){int before=vm.Pc;vm.Step();if(before==SjAssignments[controller]){int actual=Convert.ToInt32(vm.Evaluate("SJ"));Require(actual>=0&&actual<4,"Original RNG branch outside range");host.Record(vm,"owned_sj_override",new[]{actual,sj});vm.ExecuteOwnedSetup("SJ="+sj);set=true;}if(vm.Pc==loop)break;}
      int yc=Convert.ToInt32(vm.Evaluate("YC"));Require(set&&vm.Pc==loop&&yc>=66&&yc<=181,"Controller RNG/loop contract changed");
      bool special=controller==2||controller!=1&&(cycle==0||cycle==3);string prefix=special?(controller==3?"XX":"ZZ"):"";string expected=prefix+ExpectedOrder(p,Orders[sj],sj);Require(Keys(host.Snapshot(),offset)==expected,"Controller period, special key or selected order differs");
      Require(vm.Depth==1,"Nested order failed to restore controller call frame");cycles.Add(new{cycle=cycle,sj=sj,yc=yc,keys=expected});
     }
     cases.Add(new{kind="controller",entry=Controllers[controller],sj=sj,cycles=cycles,events=host.Snapshot()});
    }
   }
   foreach(bool[] sequence in new[]{new[]{false,true,true},new[]{true,false,true},new[]{false,false,false}})for(int repeat=0;repeat<2;repeat++){
    var p=Wrapped(original,117);using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,1038)){
     vm.AddOwnedObject("QMacroIslandWorkerDm",new IslandWorkerDm(host,vm,sequence,repeat!=0));Boot(vm);for(int n=0;n<100&&vm.Pc!=121;n++)vm.Step();Require(vm.Pc==121,"Finder loop not reached");
     for(int cycle=0;cycle<sequence.Length;cycle++){int count=0;do{vm.Step();count++;}while(vm.Pc!=121&&count<100);Require(vm.Pc==121,"Finder failed to loop");}
     int moves=0;foreach(var e in host.Snapshot())if(e.Kind=="mouse_move"){int[] xy=(int[])((object[])e.Value)[0];Require(xy[0]==317&&xy[1]==182,"Original y+70 target adjustment differs");moves++;}
     int expected=0;foreach(bool found in sequence)if(found)expected++;Require(moves==expected,"Finder acted on absent target");cases.Add(new{kind="finder",entry=117,query_results=sequence,inconsistent_return_value=repeat!=0,events=host.Snapshot()});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(Lab,"original-island-workers.json"),new JavaScriptSerializer(){MaxJsonLength=32*1024*1024}.Serialize(new{
   ok=error==null,error=error,completed_cases=cases.Count,cases=cases,program_sha256=Digest,original_bodies_executed=true,
   original_program_unchanged=true,dm_constructor_replaced=true,controller_sj_overridden_after_original_random_assignment=true,
   rng_algorithm_identity_claimed=false,game_input_sent=false,original_native_loaded=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
