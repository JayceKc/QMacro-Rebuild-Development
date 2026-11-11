using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class VmSelfTest {
 static void Require(bool condition,string message){if(!condition)throw new Exception(message);}
 static MacroProgram Program(string[] strings,params Instruction[] code){return new MacroProgram(){Name="owned-fixture",Code=code,Strings=strings};}
 static DryRunHost Host(MacroProgram p){var allowed=new HashSet<string>(p.Strings,StringComparer.Ordinal);return new DryRunHost(s=>allowed.Contains(s));}
 static void RunBounded(RecordVm vm){for(int i=0;i<1000;i++){var state=vm.Step();if(state==RunState.Finished||state==RunState.IterationEnded)return;if(state==RunState.WaitingForMessage||state==RunState.WaitingForUi)throw new Exception("Unexpected wait");}throw new Exception("Fixture instruction bound");}
 static void CheckControl(){
  var p=Program(new[]{"x=0","Sgn(x=0)","x=1","x=2"},new Instruction(30,0),new Instruction(4,1),new Instruction(6,3),new Instruction(30,2),new Instruction(16,2),new Instruction(30,3),new Instruction(22));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){
   RunBounded(vm);Require(Convert.ToInt32(vm.Evaluate("x"))==1,"True condition branch changed");Require(vm.Flags==2,"True Sgn should set negative flag");
  }
  p=Program(new[]{"x=7","Sgn(x=0)","x=1","x=2"},new Instruction(2,0),new Instruction(4,1),new Instruction(6,3),new Instruction(30,2),new Instruction(16,2),new Instruction(30,3),new Instruction(22));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){RunBounded(vm);Require(Convert.ToInt32(vm.Evaluate("x"))==2,"Zero condition should take relative branch");Require(vm.Flags==1,"Zero flag lost");}
  p=Program(new[]{"x=x+1"},new Instruction(12,3),new Instruction(5,7),new Instruction(255),new Instruction(12,5),new Instruction(13),new Instruction(30,0),new Instruction(13),new Instruction(22));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){RunBounded(vm);Require(Convert.ToInt32(vm.Evaluate("x"))==1&&vm.Depth==0,"Nested return stack mismatch");}
  p=Program(new string[0],new Instruction(13));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){
   bool failed=false;try{vm.Step();}catch(InvalidOperationException ex){failed=ex.Message.Contains("empty return stack");}Require(failed&&vm.State==RunState.Faulted,"Empty return silently accepted");
  }
 }
 static void CheckSharedVariants(){
  string temp=RecordVm.Temp;
  var p=Program(new[]{temp+"=Null","k",temp+"=Empty"},new Instruction(30,0),new Instruction(28,1),new Instruction(27,1),new Instruction(22));
  using(var host=Host(p)){
   using(var vm=new RecordVm(p,host.Globals,host,0)){RunBounded(vm);Require(Convert.ToBoolean(vm.Evaluate("IsNull("+temp+")")),"Null changed across global store");}
   var q=Program(new[]{"absent"},new Instruction(27,0),new Instruction(22));
   using(var vm=new RecordVm(q,host.Globals,host,0)){RunBounded(vm);Require(Convert.ToBoolean(vm.Evaluate("IsEmpty("+temp+")")),"Absent global should be Variant Empty");}
  }
 }
 static void CheckExtendedBranches(){
  for(int sign=-1;sign<=1;sign++)for(int op=7;op<=11;op++){
   int flags=sign<0?2:sign==0?1:0;bool taken=op==7?(flags&1)==0:op==8?(flags&3)==0:op==9?(flags&2)==0:op==10?(flags&2)!=0:(flags&3)!=0;
   var p=Program(new[]{"Sgn("+sign+")","path=0","path=1"},new Instruction(4,0),new Instruction(op,3),new Instruction(30,1),new Instruction(5,5),new Instruction(30,2),new Instruction(22));
   ProgramReader.Validate(p);
   using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){RunBounded(vm);Require(Convert.ToInt32(vm.Evaluate("path"))==(taken?1:0),"Extended conditional branch differs for opcode "+op+" sign "+sign);}
  }
  var noops=new List<Instruction>();foreach(int op in new[]{3,15,17,18,19,20,32,34,36})noops.Add(new Instruction(op));noops.Add(new Instruction(22));
  var empty=Program(new string[0],noops.ToArray());ProgramReader.Validate(empty);
  using(var host=Host(empty))using(var vm=new RecordVm(empty,host.Globals,host,0)){RunBounded(vm);Require(vm.Pc==empty.Code.Length&&host.Snapshot().Length==0,"Native advance-only opcode caused an effect");}
 }
 static void CheckUiCallbacks(){
  string temp=RecordVm.Temp;
  var p=Program(new[]{"Form1.InputBox1.Text",temp+"=Right("+temp+",1)"},new Instruction(33),new Instruction(35),new Instruction(23),new Instruction(37,0),new Instruction(30,1),new Instruction(38,0),new Instruction(13));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){
   host.MessageAvailable=false;Require(vm.Step()==RunState.WaitingForMessage&&vm.Pc==0,"Message wait advanced");
   host.MessageAvailable=true;vm.Step();Require(vm.Pc==1,"Message resume failed");
   Require(vm.Step()==RunState.WaitingForUi&&vm.Pc==1,"Empty event queue advanced");
   foreach(string value in new[]{"123","45"}){
    host.SetUiProperty("Form1.InputBox1.Text",value);host.QueueUiEvent(vm,3);
    vm.Step();Require(vm.Pc==3&&vm.Depth==1,"Callback dispatch lost caller");
    for(int i=0;i<4;i++)vm.Step();Require(vm.Pc==1&&vm.Depth==0,"Callback must return to op35 itself");
    Require(Convert.ToString(host.ReadUiProperty(vm,"Form1.InputBox1.Text"))==value.Substring(value.Length-1),"UI read/expression/CStr/write mismatch");
   }
   host.UiOpen=false;vm.Step();Require(vm.Pc==2,"Closed UI should advance");Require(vm.Step()==RunState.IterationEnded,"op23 exit missing");
  }
 }
 static void CheckRealStaWorker(){
  var p=Program(new[]{"Dim local","local=700","workerID","local=local+1","Call QMLibrary.SetGlobalVar(\"worker_local\",local,0)"},
   new Instruction(30,0),new Instruction(29),new Instruction(30,1),new Instruction(24,3),new Instruction(28,2),new Instruction(16,4),new Instruction(30,3),new Instruction(30,4),new Instruction(23),new Instruction(22));
  var allowed=new HashSet<string>(p.Strings,StringComparer.Ordinal);
  using(var entered=new ManualResetEvent(false))using(var release=new ManualResetEvent(false))
  using(var host=new DryRunHost(s=>{if(s==p.Strings[3]){entered.Set();if(!release.WaitOne(2000))throw new Exception("Worker fixture barrier timeout");}return allowed.Contains(s);}))
  using(var vm=new RecordVm(p,host.Globals,host,0)){
   RunBounded(vm);int id=Convert.ToInt32(host.Globals.Get("workerID"));Require(id>0,"Worker handle was not saved");
   Require(entered.WaitOne(2000),"STA worker never reached entry");
   host.ThreadControl(vm,id,1);release.Set();Require(!host.JoinWorker(id,50),"Paused worker continued to next instruction");
   host.ThreadControl(vm,id,2);Require(host.JoinWorker(id,2000),"Worker failed to resume");
   Require(host.Worker(id).Error==null,"Worker fault: "+host.Worker(id).Error);
   Require(Convert.ToInt32(host.Globals.Get("worker_local"))==1,"Worker inherited parent script-local value");
   Require(Convert.ToInt32(vm.Evaluate("local"))==700,"Worker clobbered parent-local value");
   Require(host.Worker(id).State==RunState.IterationEnded,"Worker end state missing");
  }
 }
 static void CheckMissingAndEffects(){
  var p=Program(new[]{"Call QMLibrary.KeyDown(\"Q\",0,1)","Call QMLibrary.Delay(50)","Call QMLibrary.KeyUp(\"Q\",0,1)","Call QMLibrary.ExitScript(0)"},new Instruction(30,0),new Instruction(30,1),new Instruction(2,2),new Instruction(30,3),new Instruction(255));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){RunBounded(vm);Require(vm.State==RunState.Finished,"ExitScript became an engine fault");var events=host.Snapshot();Require(events.Length==4&&events[0].Kind=="key_down"&&events[2].Kind=="key_up","Dry-run event ordering differs");}
  p=Program(new[]{"Call QMLibrary.ExitScript()"},new Instruction(30,0),new Instruction(255));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){RunBounded(vm);Require(vm.State==RunState.Finished,"Default ExitScript stop failed");}
  p=Program(new[]{"Call QMLibrary.ExitScript(1)"},new Instruction(30,0));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){
   bool rejected=false;try{vm.Step();}catch(InvalidOperationException){rejected=vm.State==RunState.Faulted;}
   Require(rejected&&host.Snapshot().Length==0,"Unverified restart was silently converted to a successful stop");
  }
  p=Program(new string[0],new Instruction(255));p.Missing.Add(0);
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){
   bool failed=false;try{vm.Step();}catch(InvalidOperationException ex){failed=ex.InnerException is MissingOriginalRecordException&&ex.Message.Contains("L00000");}
   Require(failed,"Missing original record was treated as recovered NOP");
  }
 }
 static void CheckSelectedWorkerStop(){
  var p=Program(new[]{"Call QMLibrary.SetGlobalVar(\"before_stop\",1,0)","Call QMLibrary.SetGlobalVar(\"after_stop\",1,0)"},
   new Instruction(29),new Instruction(24,3),new Instruction(16,5),new Instruction(255),new Instruction(30,0),new Instruction(30,1),new Instruction(23),new Instruction(22));
  using(var entered=new ManualResetEvent(false))using(var release=new ManualResetEvent(false))
  using(var host=new DryRunHost(s=>{if(s==p.Strings[0]){entered.Set();if(!release.WaitOne(2000))throw new Exception("Stop fixture barrier timeout");}return s==p.Strings[0]||s==p.Strings[1];}))
  using(var vm=new RecordVm(p,host.Globals,host,0)){
   RunBounded(vm);Require(entered.WaitOne(2000),"Stop target did not enter");
   host.ThreadControl(vm,1,65537);release.Set();Require(!host.JoinWorker(1,50),"Pause low16 conversion failed");
   host.ThreadControl(vm,1,0);Require(host.JoinWorker(1,2000),"Paused worker failed to cancel");
   Require(host.Worker(1).Error==null&&host.Worker(1).State==RunState.Cancelled,"Stop became worker fault");
   Require(host.Globals.Get("after_stop")==null,"Stopped worker continued past checkpoint");
   int other=host.StartWorker(vm,4);Require(host.JoinWorker(other,2000),"Target stop cancelled unrelated worker");
   Require(host.Worker(other).Error==null&&Convert.ToInt32(host.Globals.Get("after_stop"))==1,"Host-wide stop incorrectly used for selector");
   host.ThreadControl(vm,9999,0);
  }
 }
 static void CheckOwnedServiceBoundary(){
  var p=Program(new[]{"Call QMLibrary.MouseMove(40,20,0,0)","Call QMLibrary.OpenLog(\"fixture.log\")",
   "Call QMLibrary.ExtractAttachment(\"fixture\",\"*.bmp\")","Call QMLibrary.MessageNotify(1,\"preview\")","Call QMLibrary.ThreadControl(9999,1)"},
   new Instruction(30,0),new Instruction(30,1),new Instruction(30,2),new Instruction(30,3),new Instruction(30,4),new Instruction(22));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){
   RunBounded(vm);var events=host.Snapshot();Require(events.Length==5&&events[0].Kind=="mouse_move"&&events[1].Kind=="open_log"&&events[2].Kind=="extract_attachment"&&events[3].Kind=="message_notify"&&events[4].Kind=="thread_control_unmatched","Owned service signatures or unmatched selector behavior differs");
  }
  p=Program(new[]{"Call QMLibrary.CallAPI2(\"fzreg.dll\",\"SetDllPathW\",\"fz.dll\",0)"},new Instruction(30,0));
  using(var host=Host(p))using(var vm=new RecordVm(p,host.Globals,host,0)){
   bool rejected=false;try{vm.Step();}catch(InvalidOperationException){rejected=vm.State==RunState.Faulted;}
   Require(rejected&&host.Snapshot().Length==0,"Native registration was not refused by dry-run boundary");
  }
 }
 [STAThread]public static int Main(string[] args){
  if(args.Length!=1)return 2;var checks=new List<string>();string error=null;
  try{CheckControl();checks.Add("branch_flags_calls_returns");CheckExtendedBranches();checks.Add("extended_native_conditionals_and_advance_only_handlers");CheckSharedVariants();checks.Add("shared_empty_null_variants");CheckUiCallbacks();checks.Add("ui_wait_read_write_repeat_callback");CheckRealStaWorker();checks.Add("real_sta_worker_entry_shared_store_pause_resume");CheckSelectedWorkerStop();checks.Add("selected_paused_worker_cooperative_stop_and_other_worker_survival");CheckMissingAndEffects();checks.Add("bounded_dry_input_exit_missing_provenance");CheckOwnedServiceBoundary();checks.Add("owned_service_signatures_and_native_call_refusal");}
  catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(args[0],new JavaScriptSerializer().Serialize(new{ok=error==null,error=error,checks=checks,
    original_script_executed=false,original_native_loaded=false,game_input_sent=false,
    thread_control_native_equivalence_verified=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
