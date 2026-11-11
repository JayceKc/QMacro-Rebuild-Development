// Bounded dry-run orchestration: real STA worker engines, shared values,
// explicit pause/resume gates and UI event queues. Never sends Windows input.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;

namespace QMacroRebuild {
 public sealed class DryEvent {
  public string Module,Kind;
  public int Record;
  public object Value;
 }
 public sealed class DryWorker {
  internal readonly ManualResetEvent Pause=new ManualResetEvent(true);
  internal readonly ManualResetEvent Cancel=new ManualResetEvent(false);
  internal Thread Thread;
  internal RecordVm Context;
  internal int Steps;
  public readonly int Id,Entry;
  public Exception Error {get;internal set;}
  public RunState State {get;internal set;}
  internal DryWorker(int id,int entry){Id=id;Entry=entry;}
 }
 public sealed class DryRunHost:IVmPorts,IDisposable {
  readonly object gate=new object();
  readonly ManualResetEvent stop=new ManualResetEvent(false);
  readonly Dictionary<int,DryWorker> workers=new Dictionary<int,DryWorker>();
  readonly Dictionary<RecordVm,DryWorker> contexts=new Dictionary<RecordVm,DryWorker>();
  readonly Dictionary<RecordVm,int> rootSteps=new Dictionary<RecordVm,int>();
  readonly Dictionary<RecordVm,Queue<int>> uiEvents=new Dictionary<RecordVm,Queue<int>>();
  readonly Dictionary<string,object> uiProperties=new Dictionary<string,object>(StringComparer.OrdinalIgnoreCase);
  readonly List<DryEvent> events=new List<DryEvent>();
  public readonly SharedVariables Globals=new SharedVariables();
  readonly Func<string,bool> sourceAllowed;
  public bool UiOpen=true,MessageAvailable=true;
  public int MaxInstructions=10000;
  public Func<RecordVm,string,object> LibraryProvider;
  public Func<RecordVm,string,string> SourceRewrite;
  public Func<RecordVm,int,int> WorkerStarter;
  public Func<RecordVm,string,object[],object> BuiltinProvider;
  int nextId;
  public DryRunHost(Func<string,bool> reviewedSourcePolicy){
   if(reviewedSourcePolicy==null)throw new ArgumentNullException("reviewedSourcePolicy");sourceAllowed=reviewedSourcePolicy;
  }
  public DryEvent[] Snapshot(){lock(gate)return events.ToArray();}
  public DryWorker Worker(int id){lock(gate)return workers[id];}
  public void Record(RecordVm vm,string kind,object value){lock(gate)events.Add(new DryEvent(){Module=vm.Program.Name,Record=vm.Pc,Kind=kind,Value=value});}
  public void BeforeInstruction(RecordVm context){
   if(stop.WaitOne(0))throw new OperationCanceledException();
   DryWorker worker;
   lock(gate){
    if(contexts.TryGetValue(context,out worker)){if(++worker.Steps>MaxInstructions)throw new InvalidOperationException("Dry-run instruction bound reached");}
    else{int count;rootSteps.TryGetValue(context,out count);rootSteps[context]=count+1;if(count>=MaxInstructions)throw new InvalidOperationException("Dry-run instruction bound reached");}
   }
   if(worker!=null){
    if(worker.Cancel.WaitOne(0))throw new OperationCanceledException();
    if(WaitHandle.WaitAny(new WaitHandle[]{stop,worker.Cancel,worker.Pause})!=2)throw new OperationCanceledException();
   }
  }
  public string PrepareSource(RecordVm context,string source){
   if(!sourceAllowed(source))throw new NotSupportedException("Source has not been approved for this dry-run: "+context.Program.Name+" L"+context.Pc);
   if(SourceRewrite==null)return source;
   string rewritten=SourceRewrite(context,source);
   if(rewritten!=source)Record(context,"source_rewrite",new[]{source,rewritten});
   return rewritten;
  }
  public int StartWorker(RecordVm parent,int entry){
   if(WorkerStarter!=null){int virtualId=WorkerStarter(parent,entry);Record(parent,"worker_start",new[]{virtualId,entry});return virtualId;}
   DryWorker worker;
   lock(gate){if(workers.Count>=64)throw new InvalidOperationException("Dry-run worker bound reached");worker=new DryWorker(++nextId,entry);workers.Add(worker.Id,worker);}
   worker.Thread=new Thread(()=>{
    try{
     using(var context=new RecordVm(parent.Program,Globals,this,entry)){
      lock(gate){worker.Context=context;contexts.Add(context,worker);}
      while(!stop.WaitOne(0)&&!worker.Cancel.WaitOne(0)){
       RunState state=context.Step();worker.State=state;
       if(state==RunState.Finished||state==RunState.Cancelled||state==RunState.Faulted||state==RunState.IterationEnded)break;
       if(state==RunState.WaitingForUi||state==RunState.WaitingForMessage)stop.WaitOne(5);
      }
      if((stop.WaitOne(0)||worker.Cancel.WaitOne(0))&&worker.State!=RunState.Finished&&worker.State!=RunState.IterationEnded)worker.State=RunState.Cancelled;
     }
    }catch(Exception ex){worker.Error=ex;worker.State=RunState.Faulted;}
    finally{lock(gate){if(worker.Context!=null)contexts.Remove(worker.Context);}}
   });
   worker.Thread.IsBackground=true;worker.Thread.Name="QMacro dry worker "+worker.Id;worker.Thread.SetApartmentState(ApartmentState.STA);worker.Thread.Start();
   Record(parent,"worker_start",new[]{worker.Id,entry});return worker.Id;
  }
  public bool JoinWorker(int id,int milliseconds){return Worker(id).Thread.Join(milliseconds);}
  public bool ReceiveRunnerMessage(RecordVm context){return MessageAvailable;}
  public bool UiIsOpen(RecordVm context){return UiOpen;}
  public void QueueUiEvent(RecordVm context,int target){lock(gate){Queue<int> queue;if(!uiEvents.TryGetValue(context,out queue))uiEvents.Add(context,queue=new Queue<int>());queue.Enqueue(target);}}
  public bool TryUiEvent(RecordVm context,out int target){lock(gate){Queue<int> queue;target=0;if(!uiEvents.TryGetValue(context,out queue)||queue.Count==0)return false;target=queue.Dequeue();return true;}}
  public object ReadUiProperty(RecordVm context,string path){lock(gate){object value;if(!uiProperties.TryGetValue(path,out value))throw new KeyNotFoundException("Unknown UI property "+path);return value;}}
  public void SetUiProperty(string path,object value){lock(gate)uiProperties[path]=value;}
  public void WriteUiProperty(RecordVm context,string path,string value){lock(gate)uiProperties[path]=value;Record(context,"ui_write",new[]{path,value});}
  public object LoadOwnedLibrary(RecordVm context,string name){if(LibraryProvider!=null)return LibraryProvider(context,name);throw new NotSupportedException("Dry-run plugin adapter not provided: "+name);}
  public void Delay(RecordVm context,int milliseconds){Record(context,"delay",milliseconds);}
  public void Trace(RecordVm context,string message){Record(context,"trace",message);}
  public void Input(RecordVm context,string kind,object value,int mode,int count){Record(context,kind,new object[]{value,mode,count});}
  public void ThreadControl(RecordVm context,int worker,int operation){
   operation=unchecked((short)operation);
   if(operation<0||operation>2)throw new NotSupportedException("Unverified ThreadControl mode");
   DryWorker control;lock(gate)workers.TryGetValue(worker,out control);
   // Native selector 0x60a120 compares the exact id, and the scan returns zero
   // matches if it is absent. It does not throw merely because the id is stale.
   if(control==null){Record(context,"thread_control_unmatched",new[]{worker,operation});return;}
   // Native 0x65f940 -> 0x623ac0 proves mode 1 sets bit 8 and mode 2 clears it.
   // The dispatcher polls that bit; OS SuspendThread is not used by this path.
   // Stop bit 0x4 is also cooperative. This managed policy stops only the
   // selected worker; native UI notifications/cleanup are not emulated here.
   if(operation==0){control.Cancel.Set();control.Pause.Set();}
   else if(operation==1)control.Pause.Reset();else control.Pause.Set();
   Record(context,"thread_control",new[]{worker,operation});
  }
  public void ExitScriptRequested(RecordVm context,int restart){
   // Native 0x65e490 stops the root family and calls 0x628100 when nonzero.
   // The bounded dry host has no verified root reinitialization lifecycle.
   if(restart!=0)throw new NotSupportedException("ExitScript restart requires a verified root lifecycle adapter");
   Record(context,"exit_script",restart);stop.Set();
  }
  public object Service(RecordVm context,string name,object[] arguments){
   if(name=="builtin_cursor"||name=="builtin_color"||name=="builtin_picture"){
    if(BuiltinProvider==null)throw new NotSupportedException("Builtin provider not supplied: "+name);
    object value=BuiltinProvider(context,name,arguments);Record(context,name,arguments);return value;
   }
   if(name=="call_api2")throw new NotSupportedException("Native API calls require an explicit owned replacement");
   if(name!="open_log"&&name!="extract_attachment"&&name!="message_notify")throw new NotSupportedException("Unknown service "+name);
   Record(context,name,arguments);return null;
  }
  public void Dispose(){
   stop.Set();DryWorker[] pending;
   lock(gate){pending=new List<DryWorker>(workers.Values).ToArray();foreach(var worker in pending)worker.Pause.Set();}
   var deadline=Stopwatch.StartNew();
   foreach(var worker in pending){int remaining=2000-(int)deadline.ElapsedMilliseconds;if(remaining>0)worker.Thread.Join(remaining);}
   foreach(var worker in pending)if(worker.Thread.IsAlive)throw new InvalidOperationException("Dry worker still active; do not assume stopped");
   foreach(var worker in pending){worker.Pause.Dispose();worker.Cancel.Dispose();}stop.Dispose();
  }
 }
}
