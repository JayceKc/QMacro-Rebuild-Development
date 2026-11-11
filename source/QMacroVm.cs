// Owned record dispatcher. Native control contracts are replayed separately.
// All external effects belong to injected ports; missing original records stop.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Runtime.InteropServices;

namespace QMacroRebuild {
 public sealed class Instruction {
  public readonly int Op,Operand,Location,Field3;
  public Instruction(int op,int operand=0,int location=0,int field3=0){Op=op;Operand=operand;Location=location;Field3=field3;}
 }
 public sealed class MacroProgram {
  public string Name;
  public Instruction[] Code;
  public string[] Strings;
  public readonly HashSet<int> Missing=new HashSet<int>();
 }
 public enum RunState { Ready, WaitingForMessage, WaitingForUi, IterationEnded, Finished, Cancelled, Faulted }
 public interface IVmPorts {
  void BeforeInstruction(RecordVm context);
  string PrepareSource(RecordVm context,string source);
  int StartWorker(RecordVm parent,int entry);
  bool ReceiveRunnerMessage(RecordVm context);
  bool TryUiEvent(RecordVm context,out int target);
  bool UiIsOpen(RecordVm context);
  object ReadUiProperty(RecordVm context,string path);
  void WriteUiProperty(RecordVm context,string path,string value);
  object LoadOwnedLibrary(RecordVm context,string name);
  void Delay(RecordVm context,int milliseconds);
  void Trace(RecordVm context,string message);
  void Input(RecordVm context,string kind,object value,int mode,int count);
  void ThreadControl(RecordVm context,int worker,int operation);
  void ExitScriptRequested(RecordVm context,int restart);
  object Service(RecordVm context,string name,object[] arguments);
 }
 public sealed class SharedVariables {
  readonly object gate=new object();
  readonly Dictionary<string,object> values=new Dictionary<string,object>(StringComparer.Ordinal);
  public object Get(string name){lock(gate){object value;return values.TryGetValue(name,out value)?value:null;}}
  public void Set(string name,object value){lock(gate)values[name]=value;}
 }
 [ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
 public sealed class OwnedLibrary {
  readonly RecordVm owner;readonly SharedVariables shared;readonly IVmPorts ports;
  public OwnedLibrary(RecordVm vm,SharedVariables globals,IVmPorts runtime){owner=vm;shared=globals;ports=runtime;}
  public object GetGlobalVar(string name,int scope){if(scope!=0)throw new NotSupportedException("Global scope not observed");return shared.Get(name);}
  public void SetGlobalVar(string name,object value,int scope){if(scope!=0)throw new NotSupportedException("Global scope not observed");shared.Set(name,value);}
  public void Delay(int milliseconds){if(milliseconds<0)throw new ArgumentOutOfRangeException("milliseconds");ports.Delay(owner,milliseconds);}
  public void TracePrint(object message){ports.Trace(owner,Convert.ToString(message,CultureInfo.InvariantCulture));}
  public void KeyPress(string key,int mode,int count){ports.Input(owner,"key_press",key,mode,count);}
  public void KeyDown(string key,int mode,int count){ports.Input(owner,"key_down",key,mode,count);}
  public void KeyUp(string key,int mode,int count){ports.Input(owner,"key_up",key,mode,count);}
  public void MouseClick(int button,int mode,int count){ports.Input(owner,"mouse_click",button,mode,count);}
  public void MouseMove(int x,int y,int mode,int relative){ports.Input(owner,"mouse_move",new[]{x,y},mode,relative);}
  public void OpenLog(string path){ports.Service(owner,"open_log",new object[]{path});}
  public void ExtractAttachment(string folder,string pattern){ports.Service(owner,"extract_attachment",new object[]{folder,pattern});}
  public object CallAPI2(string library,string export,object argument,object flags){return ports.Service(owner,"call_api2",new[]{(object)library,export,argument,flags});}
  public void MessageNotify(int kind,string message){ports.Service(owner,"message_notify",new object[]{kind,message});}
  public void ThreadControl(int worker,int operation){ports.ThreadControl(owner,worker,operation);}
  int Packed(string service,object[] arguments){
   object result=ports.Service(owner,service,arguments);
   if(!(result is int))throw new InvalidOperationException("Builtin provider must return a signed Int32 packed coordinate: "+service);
   return (int)result;
  }
  public int GetCursorPos(){return Packed("builtin_cursor",new object[0]);}
  public int FindColor(int left,int top,int right,int bottom,string bgr,int mode,double similarity){return Packed("builtin_color",new object[]{left,top,right,bottom,bgr,mode,similarity});}
  public int FindPic(int left,int top,int right,int bottom,string file,double similarity){return Packed("builtin_picture",new object[]{left,top,right,bottom,file,similarity});}
  public void ExitScript([Optional,DefaultParameterValue(0)] int restart){
   // The observed source uses ExitScript(0) and ExitScript(1). The port must
   // accept a restart before the context is considered successfully exited.
   ports.ExitScriptRequested(owner,restart);owner.ExitRequested=true;throw new MacroExitException();
  }
 }
 public sealed class MacroExitException:Exception{}
 public sealed class MissingOriginalRecordException:Exception {
  public MissingOriginalRecordException(string module,int pc):base(module+" L"+pc.ToString("D5")+": original instruction missing"){}
 }
 public sealed class RecordVm:IDisposable {
  public const string Temp="F2730835_2229_445E_97C7_l3F76l2771DA";
  public readonly MacroProgram Program;
  readonly IVmPorts ports;readonly VbsEngine engine;
  readonly HashSet<int> loaded=new HashSet<int>();
  readonly HashSet<string> boundLibraries=new HashSet<string>(StringComparer.Ordinal);
  readonly List<int> returns=new List<int>();
  public int Pc {get;private set;}
  public int Flags {get;private set;}
  public int Entry {get;private set;}
  public RunState State {get;private set;}
  public bool ContinueIteration;
  internal bool ExitRequested;
  public int Depth {get{return returns.Count;}}
  public object Evaluate(string text){return engine.Evaluate(text,(uint)Pc);}
  public void ExecuteOwnedSetup(string source){engine.Execute(source,(uint)Pc);}
  public void AddOwnedObject(string name,object instance){engine.AddItem(name,instance);}
  public RecordVm(MacroProgram program,SharedVariables globals,IVmPorts runtime,int entry){
   if(program.Code==null||program.Code.Length==0||program.Strings==null)throw new ArgumentException("Empty macro program");
   Program=program;ports=runtime;Entry=entry;State=RunState.Ready;
   engine=new VbsEngine();
   try{engine.AddItem("QMLibrary",new OwnedLibrary(this,globals,runtime));engine.AddItem("QMacroUiValue",uiSlot);engine.Execute(OwnedBuiltinPrelude.Text,0);}catch{engine.Dispose();throw;}
  }
  static string Quoted(string text){return "\""+text.Replace("\"","\"\"")+"\"";}
  string Text(Instruction instruction){if(instruction.Operand<0||instruction.Operand>=Program.Strings.Length)throw new IndexOutOfRangeException("Bad SL index");return Program.Strings[instruction.Operand];}
  void Jump(int target){if(target<0||target>=Program.Code.Length)throw new IndexOutOfRangeException("Invalid record target "+target);Pc=target;}
  void Push(int pc){if(returns.Count>=8192)throw new InvalidOperationException("Native call-depth limit 8192");returns.Add(pc);}
  void LoadOnce(Instruction instruction){
   if(loaded.Contains(instruction.Operand)){Pc++;return;}
   string text=Text(instruction);int split=text.IndexOf('\n');
   if(split<1)throw new NotSupportedException("Unresolved load-once form");
   string name=text.Substring(0,split);
   if(name!="FILE"&&name!="SYS"&&name!="PIC")throw new NotSupportedException("Unknown owned library "+name);
   string alias="QMacroOwned_"+name;
   if(!boundLibraries.Contains(name)){
    object library=ports.LoadOwnedLibrary(this,name);
    if(library==null)throw new NotSupportedException("Owned library unavailable: "+name);
    engine.AddItem(alias,library);boundLibraries.Add(name);
   }
   engine.Execute("Set "+name+"="+alias,(uint)Pc);loaded.Add(instruction.Operand);Pc++;
  }
  public RunState Step(){
   if(State==RunState.Finished||State==RunState.Cancelled||State==RunState.Faulted||State==RunState.IterationEnded)return State;
   if(Pc==Program.Code.Length){State=RunState.Finished;return State;}
   if(Pc<0||Pc>Program.Code.Length)throw new IndexOutOfRangeException("PC outside program");
   int before=Pc;
   try{
    ports.BeforeInstruction(this);
    if(Program.Missing.Contains(Pc))throw new MissingOriginalRecordException(Program.Name,Pc);
    Instruction instruction=Program.Code[Pc];State=RunState.Ready;
    switch(instruction.Op){
     case 2:case 30:
      engine.Execute(ports.PrepareSource(this,Text(instruction)),(uint)Pc);Pc++;break;
     case 4:
      object result=engine.Evaluate(Text(instruction),(uint)Pc);
      // Every preserved condition is Sgn(...), whose VBScript type is Integer.
      if(!(result is short))throw new NotSupportedException("Condition result is not native VT_I2");
      short value=(short)result;Flags=(Flags&~3)|(value==0?1:0)|(value<0?2:0);Pc++;break;
     case 5:Jump(instruction.Operand);break;
     case 6:if((Flags&1)!=0)Jump(unchecked(Pc+instruction.Operand));else Pc++;break;
     case 7:if((Flags&1)==0)Jump(unchecked(Pc+instruction.Operand));else Pc++;break;
     case 8:if((Flags&3)==0)Jump(unchecked(Pc+instruction.Operand));else Pc++;break;
     case 9:if((Flags&2)==0)Jump(unchecked(Pc+instruction.Operand));else Pc++;break;
     case 10:if((Flags&2)!=0)Jump(unchecked(Pc+instruction.Operand));else Pc++;break;
     case 11:if((Flags&3)!=0)Jump(unchecked(Pc+instruction.Operand));else Pc++;break;
     case 12:Push(Pc+1);Jump(instruction.Operand);break;
     case 13:
      if(returns.Count==0)throw new InvalidOperationException("Native empty return stack");
      int last=returns.Count-1;int target=returns[last];returns.RemoveAt(last);Pc=target;break;
     case 16:Jump(unchecked(Pc+instruction.Operand));break;
     case 3:case 15:case 17:case 18:case 19:case 20:case 22:case 32:case 34:case 36:case 255:Pc++;break;
     case 23:if(ContinueIteration)Pc++;else State=RunState.IterationEnded;break;
     case 24:
      int entry=checked(Pc+instruction.Operand);
      if(entry<0||entry>=Program.Code.Length)throw new IndexOutOfRangeException("Invalid worker entry");
      int worker=ports.StartWorker(this,entry);
      engine.Execute(Temp+"="+worker.ToString(CultureInfo.InvariantCulture),(uint)Pc);Pc++;break;
     case 27:engine.Execute(Temp+"=QMLibrary.GetGlobalVar("+Quoted(Text(instruction))+",0)",(uint)Pc);Pc++;break;
     case 28:engine.Execute("Call QMLibrary.SetGlobalVar("+Quoted(Text(instruction))+","+Temp+",0)",(uint)Pc);Pc++;break;
     case 29:if(Entry!=0)Jump(Entry);else Pc++;break;
     case 31:LoadOnce(instruction);break;
     case 33:if(ports.ReceiveRunnerMessage(this))Pc++;else State=RunState.WaitingForMessage;break;
     case 35:
      int callback;
      if(!ports.UiIsOpen(this))Pc++;
      else if(ports.TryUiEvent(this,out callback)){Push(Pc);Jump(callback);}else State=RunState.WaitingForUi;
      break;
     case 37:
      object property=ports.ReadUiProperty(this,Text(instruction));
      // A named bridge keeps Variant Empty/Null/numeric types intact.
      uiSlot.Value=property;
      engine.Execute(Temp+"=QMacroUiValue.Value",(uint)Pc);Pc++;break;
     case 38:
      string display=(string)engine.Evaluate("CStr("+Temp+")",(uint)Pc);
      ports.WriteUiProperty(this,Text(instruction),display);Pc++;break;
     default:throw new NotSupportedException("Unresolved opcode "+instruction.Op);
    }
    return State;
   }catch(Exception ex){
    if(ExitRequested){State=RunState.Finished;return State;}
    if(ex is OperationCanceledException){State=RunState.Cancelled;return State;}
    State=RunState.Faulted;throw new InvalidOperationException(Program.Name+" L"+before.ToString("D5")+": "+ex.Message,ex);
   }
  }
  readonly VariantSlot uiSlot=new VariantSlot();
  public void Dispose(){engine.Dispose();}
 }
 [ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
 public sealed class VariantSlot {public object Value {get;set;}}
}
