// Owned x86 host for Windows VBScript. Interface layouts from Microsoft's
// win32metadata ActivScp.h; no original Runner or plugin is loaded here.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using EXCEPINFO = System.Runtime.InteropServices.ComTypes.EXCEPINFO;
using System.Web.Script.Serialization;

namespace QMacroRebuild {
 [ComImport, Guid("BB1A2AE1-A4F9-11CF-8F20-00805F2CD064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 interface IActiveScript {
  void SetScriptSite(IActiveScriptSite site);
  void GetScriptSite(ref Guid iid, out IntPtr site);
  void SetScriptState(int state);
  void GetScriptState(out int state);
  void Close();
  void AddNamedItem([MarshalAs(UnmanagedType.LPWStr)]string name,uint flags);
  void AddTypeLib(ref Guid id,uint major,uint minor,uint flags);
  void GetScriptDispatch([MarshalAs(UnmanagedType.LPWStr)]string item,out IntPtr dispatch);
  void GetCurrentScriptThreadID(out uint id);
  void GetScriptThreadID(uint win32,out uint script);
  void GetScriptThreadState(uint id,out int state);
  void InterruptScriptThread(uint id,ref EXCEPINFO error,uint flags);
  void Clone(out IActiveScript clone);
 }
 [ComImport, Guid("BB1A2AE2-A4F9-11CF-8F20-00805F2CD064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 interface IActiveScriptParse32 {
  void InitNew();
  void AddScriptlet([MarshalAs(UnmanagedType.LPWStr)]string defaultName,[MarshalAs(UnmanagedType.LPWStr)]string code,
   [MarshalAs(UnmanagedType.LPWStr)]string item,[MarshalAs(UnmanagedType.LPWStr)]string subItem,
   [MarshalAs(UnmanagedType.LPWStr)]string eventName,[MarshalAs(UnmanagedType.LPWStr)]string delimiter,
   uint cookie,uint line,uint flags,[MarshalAs(UnmanagedType.BStr)]out string name,out EXCEPINFO error);
  [PreserveSig] int ParseScriptText([MarshalAs(UnmanagedType.LPWStr)]string code,[MarshalAs(UnmanagedType.LPWStr)]string item,
   IntPtr context,[MarshalAs(UnmanagedType.LPWStr)]string delimiter,uint cookie,uint line,uint flags,
   IntPtr result,out EXCEPINFO error);
 }
 [ComVisible(true), Guid("DB01A1E3-A42B-11CF-8F20-00805F2CD064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 public interface IActiveScriptSite {
  [PreserveSig]int GetLCID(out uint lcid);
  [PreserveSig]int GetItemInfo([MarshalAs(UnmanagedType.LPWStr)]string name,uint mask,IntPtr unknown,IntPtr typeInfo);
  [PreserveSig]int GetDocVersionString([MarshalAs(UnmanagedType.BStr)]out string version);
  [PreserveSig]int OnScriptTerminate(IntPtr result,IntPtr error);
  [PreserveSig]int OnStateChange(int state);
  [PreserveSig]int OnScriptError(IActiveScriptError error);
  [PreserveSig]int OnEnterScript();
  [PreserveSig]int OnLeaveScript();
 }
 [ComImport, Guid("EAE1BA61-A4ED-11CF-8F20-00805F2CD064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 public interface IActiveScriptError {
  void GetExceptionInfo(out EXCEPINFO info);
  void GetSourcePosition(out uint cookie,out uint line,out int character);
  void GetSourceLineText([MarshalAs(UnmanagedType.BStr)]out string text);
 }
 [ComVisible(true),ClassInterface(ClassInterfaceType.None)]
 public sealed class ScriptSite : IActiveScriptSite {
  internal readonly Dictionary<string,object> Items=new Dictionary<string,object>(StringComparer.OrdinalIgnoreCase);
  public string LastError;
  public string ItemLookup;
  public int GetLCID(out uint lcid){lcid=0x404;return 0;}
  public int GetItemInfo(string name,uint mask,IntPtr unknown,IntPtr typeInfo){
   ItemLookup=name+":"+mask;
   if(unknown!=IntPtr.Zero)Marshal.WriteIntPtr(unknown,IntPtr.Zero);
   if(typeInfo!=IntPtr.Zero)Marshal.WriteIntPtr(typeInfo,IntPtr.Zero);
   object item;
   if(!Items.TryGetValue(name,out item))return unchecked((int)0x8002802B);
   if((mask&1)!=0){if(unknown==IntPtr.Zero)return unchecked((int)0x80004003);Marshal.WriteIntPtr(unknown,Marshal.GetIUnknownForObject(item));}
   if((mask&2)!=0){if(typeInfo==IntPtr.Zero)return unchecked((int)0x80004003);Marshal.WriteIntPtr(typeInfo,Marshal.GetITypeInfoForType(item.GetType()));}
   return 0;
  }
  public int GetDocVersionString(out string version){version="QMacro-owned-host-v1";return 0;}
  public int OnScriptTerminate(IntPtr result,IntPtr error){return 0;}
  public int OnStateChange(int state){return 0;}
  public int OnScriptError(IActiveScriptError error){
   try{EXCEPINFO info;uint cookie,line;int column;error.GetExceptionInfo(out info);error.GetSourcePosition(out cookie,out line,out column);
    LastError="source="+cookie+",line="+(line+1)+",column="+column+",scode="+info.scode.ToString("x")+": "+info.bstrDescription;
   }catch(Exception ex){LastError=ex.Message;}
   return 0;
  }
  public int OnEnterScript(){return 0;}
  public int OnLeaveScript(){return 0;}
 }
 public sealed class VbsEngine : IDisposable {
  object instance;IActiveScript script;IActiveScriptParse32 parser;readonly bool started;
  readonly ScriptSite site=new ScriptSite();
  [DllImport("oleaut32.dll")]static extern int VariantClear(IntPtr variant);
  public VbsEngine():this(true){}
  public VbsEngine(bool start){
   if(IntPtr.Size!=4)throw new InvalidOperationException("This host requires x86");
   instance=Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("B54F3741-5B07-11CF-A4B0-00AA004A55E8"),true));
   try{script=(IActiveScript)instance;parser=(IActiveScriptParse32)instance;script.SetScriptSite(site);parser.InitNew();script.SetScriptState(5);if(start)script.SetScriptState(1);started=start;}
   catch{Marshal.FinalReleaseComObject(instance);instance=null;throw;}
  }
  public void AddItem(string name,object item){site.Items.Add(name,item);script.AddNamedItem(name,2);}
  public object Parse(string text,bool expression,uint source){
   if(expression&&!started)throw new InvalidOperationException("Expressions cannot run in compile-only mode");
   if(!started){int state;script.GetScriptState(out state);if(state!=5)throw new InvalidOperationException("Compile-only engine left initialized state");}
   site.LastError=null;EXCEPINFO error;IntPtr value=expression?Marshal.AllocCoTaskMem(16):IntPtr.Zero;
   try{
    if(value!=IntPtr.Zero){Marshal.WriteInt64(value,0);Marshal.WriteInt64(value,8,0);}
    int hr=parser.ParseScriptText(text,null,IntPtr.Zero,null,source,0,expression?32u:0u,value,out error);
    if(hr<0||site.LastError!=null)throw new InvalidOperationException((site.LastError??error.bstrDescription)+"; hr="+hr.ToString("x")+"; item="+site.ItemLookup);
    return value==IntPtr.Zero?null:Marshal.GetObjectForNativeVariant(value);
   }finally{if(value!=IntPtr.Zero){VariantClear(value);Marshal.FreeCoTaskMem(value);}}
  }
  public void Execute(string text,uint source){Parse(text,false,source);}
  public object Evaluate(string text,uint source){return Parse(text,true,source);}
  public void Dispose(){
   if(instance==null)return;
   try{script.Close();}finally{Marshal.FinalReleaseComObject(instance);instance=null;script=null;parser=null;site.Items.Clear();}
  }
 }
 [ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
 public sealed class ProbeLibrary {
  public string Recorded {get;private set;}
  public void TracePrint(string value){Recorded=value;}
  public void FindColor(int x1,int y1,int x2,int y2,string color,double similarity,int direction,out object x,out object y){x=12;y=34;}
 }
 public static class EngineSelfTest {
  static void Require(bool condition,string message){if(!condition)throw new Exception(message);}
  [STAThread]public static int Main(string[] args){
   if(args.Length==3&&args[0]=="--compile-audit")return CompileAudit(args[1],args[2]);
   if(args.Length!=2||args[0]!="--self-test-report")return 2;
   var checks=new List<string>();bool ok=false;string failure=null;
   try{
    using(var cold=new VbsEngine(false)){
     var observer=new ProbeLibrary();cold.AddItem("QMLibrary",observer);
     cold.Execute("Call QMLibrary.TracePrint(\"must not execute\")",0);
     Require(observer.Recorded==null,"Compile-only executed code");checks.Add("compile_only_no_side_effect");
    }
    using(var e=new VbsEngine()){
     Require(Convert.ToInt32(e.Evaluate("Sgn(4>2)",1))==-1,"VB boolean sign");checks.Add("boolean_sgn_minus_one");
     Require(Convert.ToString(e.Evaluate("TypeName(Empty) & Chr(124) & CStr(Empty) & Chr(124) & CStr(Empty+1)",2))=="Empty||1","Empty coercion");checks.Add("variant_empty_preserved");
     Require(e.Evaluate("Null",3)==DBNull.Value,"Null distinct from Empty");checks.Add("variant_null_preserved");
     e.Execute("Dim slots(256), current: Set current=Nothing: current=slots(17)",4);
     Require(Convert.ToBoolean(e.Evaluate("IsEmpty(current)",5)),"Nothing assignment to Empty");checks.Add("object_to_empty_assignment");
     e.Execute("Class LocalFrame\n Public slots(4)\n Public parent\nEnd Class\nDim frame: Set frame=New LocalFrame\nframe.slots(2)=123\nSet frame.parent=Nothing",6);
     Require(Convert.ToInt32(e.Evaluate("frame.slots(2)",7))==123,"Class array member");checks.Add("class_member_array");
     var library=new ProbeLibrary();e.AddItem("QMLibrary",library);
     e.Execute("Call QMLibrary.TracePrint(ChrW(32321) & ChrW(39636))",8);
     Require(library.Recorded=="繁體","Named COM item Unicode call");checks.Add("named_com_unicode_call");
     e.Execute("Dim xx, yy: Call QMLibrary.FindColor(0,0,10,10,\"ff0000\",0.9,0,xx,yy)",9);
     Require(Convert.ToString(e.Evaluate("CStr(xx) & Chr(124) & CStr(yy)",10))=="12|34","ByRef VARIANT outputs");checks.Add("com_byref_variant_outputs");
     e.Execute("Function NoReturn()\nEnd Function\nDim result: result=NoReturn()",11);
     Require(Convert.ToBoolean(e.Evaluate("IsEmpty(result)",12)),"Empty function return");checks.Add("empty_function_return");
     bool rejected=false;try{e.Execute("If Then",777);}catch(InvalidOperationException ex){rejected=ex.Message.Contains("source=777");}
     Require(rejected,"Script error provenance");checks.Add("script_error_source_cookie");
    }
    using(var fresh=new VbsEngine()){Require(Convert.ToBoolean(fresh.Evaluate("IsEmpty(result)",1)),"Engine state leaked");checks.Add("fresh_worker_globals_isolated");}
    ok=true;
   }catch(Exception ex){failure=ex.GetType().Name+": "+ex.Message;}
   var report=new{ok=ok,error=failure,checks=checks,x86=IntPtr.Size==4,original_native_loaded=false,original_script_executed=false,game_input_sent=false};
   File.WriteAllText(args[1],new JavaScriptSerializer().Serialize(report),new System.Text.UTF8Encoding(false));
   return ok?0:1;
  }
  static int CompileAudit(string input,string output){
   var serializer=new JavaScriptSerializer(){MaxJsonLength=32*1024*1024};
   var modules=serializer.DeserializeObject(File.ReadAllText(input)) as object[];
   var reports=new List<object>();int total=0,failed=0;
   foreach(object value in modules){
    var module=(Dictionary<string,object>)value;
    var errors=new List<object>();int count=0;
    using(var cold=new VbsEngine(false)){
     foreach(object fragment in (object[])module["fragments"]){
      var f=(Dictionary<string,object>)fragment;uint record=Convert.ToUInt32(f["record"]);
      try{cold.Execute((string)f["text"],record);}
      catch(InvalidOperationException ex){errors.Add(new{record=record,sl=f["sl"],error=ex.Message});failed++;}
      count++;total++;
     }
    }
    reports.Add(new{module=module["module"],fragments=count,errors=errors});
   }
   File.WriteAllText(output,serializer.Serialize(new{ok=failed==0,total_fragments=total,failed=failed,modules=reports,
    compile_only=true,original_script_executed=false,original_native_loaded=false,game_input_sent=false}),new System.Text.UTF8Encoding(false));
   return failed==0?0:1;
  }
 }
}
