// Preserved module09 first-battle routine in fixed guest. Workers only recorded.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using QMacroRebuild;

[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class IslandVisionFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly bool[] gold,hp,elite;readonly bool invert;
 [ComVisible(false)]public int Gold,Hp,Elite;
 public IslandVisionFixture(DryRunHost h,RecordVm v,bool[] g,bool[] p,bool[] e,bool flip){host=h;vm=v;gold=g;hp=p;elite=e;invert=flip;}
 public int FindColor(int x1,int y1,int x2,int y2,string color,double similarity,int direction,out object x,out object y){
  if(Gold>=gold.Length)throw new Exception("Gold fixture exhausted");bool found=gold[Gold++];x=found?x1:-1;y=found?y1:-1;int ret=invert?(found?0:1):(found?1:0);
  host.Record(vm,"find_color",new{arguments=new object[]{x1,y1,x2,y2,color,similarity,direction},return_value=ret,x=x,y=y});return ret;
 }
 public int FindPic(int x1,int y1,int x2,int y2,string path,string delta,double similarity,int direction,out object x,out object y){
  bool found;if(x1==316){if(Hp>=hp.Length)throw new Exception("HP fixture exhausted");found=hp[Hp++];}else if(x1==600){if(Elite>=elite.Length)throw new Exception("Elite fixture exhausted");found=elite[Elite++];}else throw new Exception("Unreviewed picture query");
  x=found?x1:-1;y=found?y1:-1;int ret=invert?(found?-1:0):(found?0:-1);
  host.Record(vm,"find_pic",new{arguments=new object[]{x1,y1,x2,y2,path,delta,similarity,direction},return_value=ret,x=x,y=y});return ret;
 }
}
public static class IslandGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 const string ProgramHash="bbca57d0f39890c3c992f209ee00375e7909dd386efff576771a4ecc65cae204";
 static void Require(bool value,string message){if(!value)throw new Exception(message);}
 [STAThread]public static int Main(){
  CallbackGuestTest.Guard();var cases=new List<object>();string error=null;
  try{
   MacroProgram original=ProgramReader.Read(Path.Combine(Lab,"09.json"),ProgramHash);
   Require(original.Code.Length==1038&&original.Missing.Count==104,"Original scope changed");
   var code=new List<Instruction>(original.Code);code.Add(new Instruction(2,52));code.Add(new Instruction(12,936));code.Add(new Instruction(22));
   var p=new MacroProgram(){Name=original.Name,Strings=original.Strings,Code=code.ToArray()};foreach(int i in original.Missing)p.Missing.Add(i);
   var allowed=new HashSet<string>(StringComparer.Ordinal);int headerEnd=Array.FindIndex(p.Code,i=>i.Op==29);
   for(int i=0;i<headerEnd;i++)allowed.Add(p.Strings[p.Code[i].Operand]);allowed.Add(p.Strings[52]);
   for(int i=936;i<=1032;i++){Require(!p.Missing.Contains(i),"First-battle body missing record");if(p.Code[i].Op==2||p.Code[i].Op==30)allowed.Add(p.Strings[p.Code[i].Operand]);}
   bool[][] golds={new[]{true},new[]{false,true,true},new[]{true}};
   bool[][] health={new[]{true},new[]{false,true},new[]{true}};
   bool[][] elites={new[]{false},new[]{true,true,false},new[]{true,false}};
   for(int mode=0;mode<4;mode++)for(int scenario=0;scenario<3;scenario++)for(int flip=0;flip<2;flip++){
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,1038)){
     int nextId=200;host.WorkerStarter=(context,entry)=>++nextId;
     var fixture=new IslandVisionFixture(host,vm,golds[scenario],health[scenario],elites[scenario],flip!=0);vm.AddOwnedObject("QMacroIslandFixture",fixture);
     for(int i=0;i<100&&vm.Pc!=1038;i++)vm.Step();Require(vm.Pc==1038,"Failed to bootstrap owned call wrapper");
     string setting=p.Strings[36].Substring(0,p.Strings[36].IndexOf('='));vm.ExecuteOwnedSetup(setting+"="+mode+":Set DM=QMacroIslandFixture:g_iSimulateModeInVBSBlock=0");
     for(int i=0;i<1000&&vm.State!=RunState.Finished;i++)vm.Step();Require(vm.State==RunState.Finished&&vm.Depth==0,"First-battle routine failed to return");
     Require(fixture.Gold==golds[scenario].Length&&fixture.Hp==health[scenario].Length&&fixture.Elite==elites[scenario].Length,"Query short circuit mismatch");
     int starts=0,pauses=0,moves=0;int[] entries={960,973,986,999};
     foreach(var e in host.Snapshot()){
      if(e.Kind=="worker_start"){int[] args=(int[])e.Value;Require(args[0]==201+starts&&args[1]==(starts==0?entries[mode]:1010),"Wrong worker mapping");starts++;}
      else if(e.Kind=="thread_control_unmatched"){int[] args=(int[])e.Value;Require(args[0]==201+pauses&&args[1]==1,"Wrong worker pause order");pauses++;}
      else if(e.Kind=="mouse_move"){object[] args=(object[])e.Value;int[] xy=(int[])args[0];Require(xy[0]==515&&xy[1]==147&&Convert.ToInt32(args[1])==0&&Convert.ToInt32(args[2])==0,"Wrong target positioning");moves++;}
     }
     Require(starts==2&&pauses==2&&moves==(scenario==1?2:1),"Missing or premature side effects");
     cases.Add(new{skill_mode=mode,scenario=scenario,inconsistent_return_value=flip!=0,gold_results=golds[scenario],hp_results=health[scenario],elite_results=elites[scenario],events=host.Snapshot()});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(Lab,"original-island-first-battle.json"),new JavaScriptSerializer(){MaxJsonLength=16*1024*1024}.Serialize(new{
   ok=error==null,error=error,completed_cases=cases.Count,cases=cases,original_program_sha256=ProgramHash,
   original_record_prefix_unchanged=true,original_body_executed=true,body_entry=936,body_last=1032,
   wrapper_appended=true,frame_class_identity_inferred_by_elimination=true,worker_start_intercepted=true,
   query_results_synthetic=true,original_native_loaded=false,game_input_sent=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
