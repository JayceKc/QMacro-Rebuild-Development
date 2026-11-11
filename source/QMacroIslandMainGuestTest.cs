using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using QMacroRebuild;

[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class IslandMainFixture {
 readonly DryRunHost host;readonly RecordVm vm;readonly bool gold,hp,invert;
 [ComVisible(false)]public int MainGold,MainHp,MainElite;
 public IslandMainFixture(DryRunHost h,RecordVm context,bool goldFound,bool hpFound,bool flip){host=h;vm=context;gold=goldFound;hp=hpFound;invert=flip;}
 public int MoveTo(int x,int y){host.Record(vm,"move_to",new[]{x,y});return 1;}
 public int FindColor(int x1,int y1,int x2,int y2,string color,double similarity,int direction,out object x,out object y){
  bool found=vm.Pc<1038?true:gold;if(vm.Pc>=1038)MainGold++;x=found?x1:-1;y=found?y1:-1;int ret=invert?(found?0:1):(found?1:0);
  host.Record(vm,"find_color",new{arguments=new object[]{x1,y1,x2,y2,color,similarity,direction},return_value=ret,x=x,y=y});return ret;
 }
 public int FindPic(int x1,int y1,int x2,int y2,string files,string delta,double similarity,int direction,out object x,out object y){
  bool found;if(vm.Pc<1038)found=x1==316;else if(x1==316){MainHp++;found=hp;}else if(x1==600){found=MainElite++%2==0;}else throw new Exception("Unknown main picture query");
  x=found?x1:-1;y=found?y1:-1;int ret=invert?(found?-1:0):(found?0:-1);
  host.Record(vm,"find_pic",new{arguments=new object[]{x1,y1,x2,y2,files,delta,similarity,direction},return_value=ret,x=x,y=y});return ret;
 }
}
public static class IslandMainGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 const string Derived="babdde055bdbe575354a6a00fb173cd2efc40c1565a940f1011c2627c9e3ca78";
 const string Original="bbca57d0f39890c3c992f209ee00375e7909dd386efff576771a4ecc65cae204";
 static void Require(bool condition,string message){if(!condition)throw new Exception(message);}
 [STAThread]public static int Main(){
  CallbackGuestTest.Guard();string error=null;var cases=new List<object>();
  try{
   var p=ProgramReader.Read(Path.Combine(Lab,"09-semantic-main.json"),Derived);var original=ProgramReader.Read(Path.Combine(Lab,"09.json"),Original);
   Require(p.Code.Length==1143&&p.Missing.SetEquals(original.Missing),"Prefix/missing scope changed");
   for(int i=0;i<1038;i++){var a=p.Code[i];var b=original.Code[i];Require(a.Op==b.Op&&a.Operand==b.Operand&&a.Location==b.Location&&a.Field3==b.Field3,"Original record changed");}
   var allowed=new HashSet<string>(StringComparer.Ordinal);int headerEnd=Array.FindIndex(p.Code,r=>r.Op==29);
   for(int i=0;i<p.Code.Length;i++)if(i<headerEnd||i>=936&&i<=1032||i>=1061){var r=p.Code[i];if(r.Op==2||r.Op==30)allowed.Add(p.Strings[r.Operand]);}
   for(int mode=0;mode<4;mode++)for(int gold=0;gold<2;gold++)for(int hp=0;hp<2;hp++)for(int flip=0;flip<2;flip++)for(int alternative=0;alternative<2;alternative++)for(int hpAlternative=0;hpAlternative<2;hpAlternative++){
    p.Code[1092]=new Instruction(6,alternative==0?48:4,p.Code[1092].Location); // ref66 ->114 or70
    p.Code[1098]=new Instruction(6,hpAlternative==0?42:41,p.Code[1098].Location); // ref72 ->114 or113
    using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,1061)){
     host.SetUiProperty("Form1.ComboBox2.ListIndex",mode);host.SetUiProperty("Form1.InputBox2.Text","");int id=200;host.WorkerStarter=(context,entry)=>++id;
     var fixture=new IslandMainFixture(host,vm,gold!=0,hp!=0,flip!=0);vm.AddOwnedObject("QMacroIslandFixture",fixture);
     for(int n=0;n<100&&vm.Pc!=1061;n++)vm.Step();Require(vm.Pc==1061,"New entry was not reached");vm.ExecuteOwnedSetup("Set DM=QMacroIslandFixture:g_iSimulateModeInVBSBlock=0");
     bool entered=false;int cycles=0;
     for(int n=0;n<3000&&cycles<2;n++){int before=vm.Pc;vm.Step();if(before==1087)entered=true;if(entered&&before!=1087&&vm.Pc==1087)cycles++;}
     Require(cycles==2&&vm.Depth==0,"New main did not complete two bounded outer cycles");
     int kills=hp==1&&(gold==1||alternative==1)?2:0;string text=Convert.ToString(host.ReadUiProperty(vm,"Form1.InputBox2.Text"));Require(text==(kills==0?"":"2"),"Kill counter UI RHS/temp/set ordering differs");
     Require(fixture.MainGold==2&&fixture.MainHp==((gold==1||alternative==1)?2:0)&&fixture.MainElite==kills*2,"Inferred branch candidate query flow differs");
     int starts=0,resumes=0,pauses=0,left=0,right=0;foreach(var e in host.Snapshot()){
      if(e.Kind=="worker_start")starts++;
      if(e.Kind=="thread_control_unmatched"){int[] args=(int[])e.Value;Require(args[0]==201||args[0]==202,"Unexpected root worker ID");if(args[1]==1)pauses++;else if(args[1]==2)resumes++;else throw new Exception("Unexpected root mode");}
      if(e.Kind=="mouse_click"){object[] args=(object[])e.Value;if(Convert.ToInt32(args[0])==0)left++;else if(Convert.ToInt32(args[0])==2)right++;else throw new Exception("Unexpected mouse button");}
      if(e.Kind=="move_to"){int[] xy=(int[])e.Value;Require(xy[0]>=35&&xy[0]<40&&xy[1]>=10&&xy[1]<20,"Original random focus point outside formula");}
     }
     Require(starts==2&&resumes==kills*2&&pauses==2+kills*2&&left==1&&right==kills*3,"Main worker/click lifecycle differs");
     cases.Add(new{skill_mode=mode,gold_found=gold!=0,hp_found=hp!=0,inconsistent_return_value=flip!=0,gold_branch_alternative=alternative,hp_branch_alternative=hpAlternative,
      outer_cycles=cycles,kills=kills,ui_counter=text,events=host.Snapshot()});
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(Lab,"semantic-main09-verification.json"),new JavaScriptSerializer(){MaxJsonLength=32*1024*1024}.Serialize(new{
   ok=error==null,error=error,completed_cases=cases.Count,cases=cases,derived_sha256=Derived,original_sha256=Original,
   original_104_missing_records_unchanged=true,original_branch_operands_recovered=false,
   branch_candidates_tested=true,legacy_native_bootstrap_executed=false,worker_start_intercepted=true,query_results_synthetic=true,
   original_native_loaded=false,game_input_sent=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
