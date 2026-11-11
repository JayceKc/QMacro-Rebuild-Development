// Runs only the two intact UI callbacks in the fixed isolated guest.
// FILE.DeleteFolder is a recording-only managed object: no deletion occurs.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using Microsoft.Win32;
using QMacroRebuild;

[ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class FileIntentPreview {
 [ComVisible(false)]public readonly List<string> Requested=new List<string>();
 public int DeleteFolder(string path){Requested.Add(path);return 1;}
}
public static class CallbackGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 internal static void Guard(){
  string vendor=Convert.ToString(Registry.GetValue(@"HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS","SystemManufacturer",""));
  if(vendor.IndexOf("VMware",StringComparison.OrdinalIgnoreCase)<0||Environment.MachineName!="DESKTOP-GAR2QIL"||Environment.UserName!="kc")throw new InvalidOperationException("Fixed VMware guest only");
 }
 static void Require(bool condition,string message){if(!condition)throw new Exception(message);}
 static object Check(int module,string digest,int callback,int last){
  MacroProgram program=ProgramReader.Read(Path.Combine(Lab,module.ToString("D2")+".json"),digest);
  int ui=Array.FindIndex(program.Code,r=>r.Op==35);int headerEnd=Array.FindIndex(program.Code,r=>r.Op==29);
  Require(ui>0&&headerEnd>0,"Missing gate/UI pump");
  var allowed=new HashSet<string>(StringComparer.Ordinal);
  for(int i=0;i<headerEnd;i++){
   Require(program.Code[i].Op==30,"Unexpected bootstrap opcode");
   string declaration=program.Strings[program.Code[i].Operand];
   Require(declaration.StartsWith("Dim ")||declaration.StartsWith("Class "),"Unexpected bootstrap source");
   Require(!Regex.IsMatch(declaration,@"\b(Call|CreateObject|Execute|GetObject|Eval)\b",RegexOptions.IgnoreCase),"Executable bootstrap side effect");
   allowed.Add(declaration);
  }
  for(int i=callback;i<=last;i++){
   Instruction instruction=program.Code[i];
   if(instruction.Op==2||instruction.Op==30)allowed.Add(program.Strings[instruction.Operand]);
   Require(!program.Missing.Contains(i),"Callback original record missing");
  }
  string header=program.Strings[program.Code[0].Operand];
  var names=Regex.Match(header,@":Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+):Set ");Require(names.Success,"Unknown frame header");
  var file=new FileIntentPreview();int loads=0;var observations=new List<object>();
  using(var host=new DryRunHost(s=>allowed.Contains(s))){
   host.LibraryProvider=(context,name)=>{Require(module==6&&name=="FILE","Unexpected native dependency");loads++;return file;};
   using(var vm=new RecordVm(program,host.Globals,host,ui)){
    for(int i=0;i<500&&vm.State!=RunState.WaitingForUi;i++)vm.Step();
    Require(vm.Pc==ui&&vm.State==RunState.WaitingForUi,"Context did not reach UI wait");
    foreach(string value in new[]{"123","45"}){
     if(module==10)host.SetUiProperty("Form1.InputBox1.Text",value);
     host.QueueUiEvent(vm,callback);vm.Step();
     Require(vm.Pc==callback&&vm.Depth==1,"Wrong event entry");
     int steps=0;while(vm.Pc!=ui&&steps++<100)vm.Step();
     Require(vm.Pc==ui&&vm.Depth==0,"Callback failed to return to op35");
     Require(Convert.ToBoolean(vm.Evaluate(names.Groups[1].Value+" Is Nothing")),"Parent frame not restored");
     Require(Convert.ToBoolean(vm.Evaluate(names.Groups[2].Value+" Is Nothing")),"Temporary frame not released");
     if(module==10){string actual=Convert.ToString(host.ReadUiProperty(vm,"Form1.InputBox1.Text"));Require(actual==value.Substring(value.Length-1),"Original RIGHT callback result differs");observations.Add(new{input=value,result=actual,return_pc=vm.Pc,frame_restored=true});}
     else observations.Add(new{delete_intents=file.Requested.Count,return_pc=vm.Pc,frame_restored=true});
     Require(vm.Step()==RunState.WaitingForUi,"Callback did not wait for next event");
    }
    if(module==6){Require(file.Requested.Count==10,"Expected five intents per click");Require(loads==1,"Load-once adapter recreated FILE");}
   }
   return new{module=module,entry=callback,last=last,pump_record=ui,observations=observations,
              delete_intents=file.Requested,owned_library_loads=loads,events=host.Snapshot(),filesystem_deletions=0};
  }
 }
 [STAThread]public static int Main(){
  var results=new List<object>();string error=null;
  try{Guard();results.Add(Check(10,CallbackProgramDigests.Module10,66,73));results.Add(Check(6,CallbackProgramDigests.Module06,73,86));}
  catch(Exception ex){error=ex.ToString();}
  var report=new{ok=error==null,error=error,callbacks=results,original_script_callback_executed=error==null,
    original_native_loaded=false,game_input_sent=false,filesystem_deletions=0,full_program_restored=false};
  // Refuse to create a host-side output path when the guard failed.
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  File.WriteAllText(Path.Combine(Lab,"original-callback-vm-test.json"),new JavaScriptSerializer(){MaxJsonLength=4*1024*1024}.Serialize(report),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
