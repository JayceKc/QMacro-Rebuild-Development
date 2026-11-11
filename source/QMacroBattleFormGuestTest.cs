// Fixed VMware guest only. Exercise the retained Form1 wait and end sequence.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class BattleFormGuestTest {
    const string Lab=@"C:\Users\Public\Documents\QMacroLab";

    static void Check(bool ok,string detail) {
        if(!ok) throw new InvalidOperationException(detail);
    }

    static string Digest(byte[] raw) {
        using(var h=SHA256.Create())
            return BitConverter.ToString(h.ComputeHash(raw)).Replace("-", "").ToLowerInvariant();
    }

    internal static HashSet<string> Header(MacroProgram program,int dispatch) {
        var header=new HashSet<string>(StringComparer.Ordinal);
        Check(dispatch>0&&dispatch<100,"Unexpected original declaration count");
        for(int at=0;at<dispatch;at++) {
            Instruction ins=program.Code[at];
            string source=program.Strings[ins.Operand];
            Check(ins.Op==30&&(source.StartsWith("Dim ")||source.StartsWith("Class "))&&
                  !System.Text.RegularExpressions.Regex.IsMatch(source,@"\b(Call|CreateObject|Execute|GetObject|Eval)\b",
                      System.Text.RegularExpressions.RegexOptions.IgnoreCase),"Unsafe declaration");
            header.Add(source);
        }
        return header;
    }

    internal static object DefaultEntry(MacroProgram program,HashSet<string> header,int dispatch) {
        var records=new List<int>();
        using(var host=new DryRunHost(header.Contains))
        using(var vm=new RecordVm(program,host.Globals,host,0)) {
            for(int at=0;at<=dispatch;at++) {
                Check(vm.Pc==at,"Default entry skipped an original declaration");
                records.Add(at);vm.Step();
            }
            Check(program.Missing.Contains(vm.Pc),"Unexpected first record after default dispatch");
            int boundary=vm.Pc;
            records.Add(boundary);
            try { vm.Step(); }
            catch(InvalidOperationException ex) {
                Check(ex.InnerException is MissingOriginalRecordException&&vm.Pc==boundary&&
                      vm.State==RunState.Faulted&&vm.Depth==0,"Wrong default entry fault");
                Check(host.Snapshot().Length==0,"Default entry had an external effect");
                return new{records=records,missing_record=boundary,call_depth=vm.Depth};
            }
            throw new InvalidOperationException("Default entry did not stop at missing data");
        }
    }

    internal static object Run(MacroProgram program,HashSet<string> header,int dispatch,int entry,int formWait,int pump,int stop,
                      bool continueIteration,bool waitThenClose) {
        var observations=new List<object>();
        using(var host=new DryRunHost(header.Contains))
        using(var vm=new RecordVm(program,host.Globals,host,entry)) {
            vm.ContinueIteration=continueIteration;
            host.MessageAvailable=!waitThenClose;
            host.UiOpen=waitThenClose;
            for(int i=0;i<=dispatch&&vm.Pc!=entry;i++) vm.Step();
            Check(vm.Pc==entry&&vm.Depth==0,"Header did not reach retained entry");
            for(int i=0;i<12&&vm.State!=RunState.IterationEnded&&vm.State!=RunState.Finished;i++) {
                int at=vm.Pc;
                int op=at==program.Code.Length?-1:program.Code[at].Op;
                Check(op==-1||op==16||op==22||op==23||op==33||op==35,"Unsafe flow left Form1 tail");
                var state=vm.Step();
                observations.Add(new{record=at,next=vm.Pc,state=state.ToString(),depth=vm.Depth});
                if(state==RunState.WaitingForMessage) {
                    Check(waitThenClose&&at==formWait&&vm.Pc==at,"Wrong retained message wait");
                    host.MessageAvailable=true;
                }
                if(state==RunState.WaitingForUi) {
                    Check(waitThenClose&&at==pump&&vm.Pc==at,"Wrong retained event wait");
                    host.UiOpen=false;
                }
            }
            Check(continueIteration ? vm.State==RunState.Finished&&vm.Pc==program.Code.Length
                                    : vm.State==RunState.IterationEnded&&vm.Pc==stop,
                  "Wrong retained tail terminal state");
            Check(vm.Depth==0&&host.Snapshot().Length==0,"Unexpected retained Form1 effect");
        }
        return new{entry=entry,continue_iteration=continueIteration,wait_then_close=waitThenClose,observations=observations};
    }

    [STAThread] public static int Main() {
        var results=new List<object>();
        string error=null;
        bool small=SharedBattleDigests.Programs.ContainsKey("09");
        try {
            CallbackGuestTest.Guard();
            foreach(string module in small?new[]{"09","10"}:new[]{"01","03","06"}) {
                string digest=SharedBattleDigests.Programs[module];
                var program=ProgramReader.Read(Path.Combine(Lab,module+".json"),digest);
                int dispatch=Array.FindIndex(program.Code,r=>r.Op==29);
                var header=Header(program,dispatch);
                int gate=Array.FindIndex(program.Code,r=>r.Op==33),pump=gate+1;
                Check(gate>0&&program.Code[pump].Op==35&&program.Code[pump+1].Op==23,"Form tail differs");
                results.Add(new{module=module,source_program_sha256=digest,default_entry=DefaultEntry(program,header,dispatch),cases=new[]{
                    Run(program,header,dispatch,gate,gate,pump,pump+1,false,true),
                    Run(program,header,dispatch,gate,gate,pump,pump+1,true,true),
                    Run(program,header,dispatch,gate-1,gate,pump,pump+2,true,false)}});
            }
        } catch(Exception ex) { error=ex.ToString(); }
        if(Environment.MachineName!="DESKTOP-GAR2QIL") return 2;
        var report=new{ok=error==null,error=error,modules=results,
            runtime_sha256=Digest(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),
            original_native_loaded=false,game_input_sent=false};
        string reportName=small?"original-skill-island-host.json":"original-battle-form.json";
        File.WriteAllText(Path.Combine(Lab,reportName),new JavaScriptSerializer().Serialize(report));
        return error==null?0:1;
    }
}
