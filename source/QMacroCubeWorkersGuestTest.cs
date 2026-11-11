// Fixed VMware guest. Worker dispatch returns synthetic IDs and never starts real workers.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class CubeWorkersGuestTest {
    const string Lab = @"C:\Users\Public\Documents\QMacroLab";
    const string ArrayName = "F2730835_2229_445E_97C7_l3F761277lDA";
    const string ParentField = "F2730835_2229_445E_97C7_13F76l2771DA";
    static readonly int[,] Ranges = {{717,856},{1495,1675},{3572,3692},{3694,3773},
        {3775,3914},{3916,4055},{4057,4196},{4198,4337},{4339,4414},{4416,4479},{4481,4556},{4558,4633},
        {4635,5018},{6481,6515},{6517,6551},{6553,6587},{6589,6623},{6625,6636},{6638,6655},{6691,6738}};
    static void Check(bool ok,string message) { if(!ok) throw new InvalidOperationException(message); }
    static string Digest(byte[] bytes) {
        using(var hash=SHA256.Create()) return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
    }
    static bool InBody(int at) {
        for(int i=0;i<Ranges.GetLength(0);i++) if(at>=Ranges[i,0]&&at<=Ranges[i,1]) return true;
        return false;
    }
    static readonly HashSet<int> TailSkips = new HashSet<int>{1494,1676,3364,3693,3774,3915,4056,4197,4338,4415,4480,4557,4634,5019,6443,6480,6516,6552,6588,6624,6637,6656,6690,6739};
    internal static bool InRetainedProbe(int at) {
        return at>=0&&at<=30 || at>=531&&at<=659 || at>=852&&at<=856 || at>=3487&&at<=3571 ||
               at>=6444&&at<=6478 || at>=6815&&at<=6819 || TailSkips.Contains(at);
    }
    internal static object Execute(MacroProgram p, HashSet<string> allowed, string frame, string frameClass, Dictionary<string,object> spec, bool retained=false) {
        int entry=Convert.ToInt32(spec["entry"]);
        Check(retained?InRetainedProbe(entry):InBody(entry),"Unreviewed entry");
        using(var host=new DryRunHost(allowed.Contains))
        using(var vm=new RecordVm(p,host.Globals,host,entry)) {
            vm.AddOwnedObject("QMacroCubeMainVision",new CubeMainVisionFixture(host,vm,spec));
            host.SourceRewrite=(context,source)=>source=="SET DM=CREATEOBJECT(\"dm.dmsoft\")" ? "Set DM=QMacroCubeMainVision" : source;
            host.WorkerStarter=(context,target)=>10000+context.Pc;
            for(int i=0;i<100&&vm.Pc!=entry;i++) vm.Step();
            Check(vm.Pc==entry,"Header did not reach controlled entry");
            if(entry==4635||entry==1495||retained&&(entry==6444||entry==3488||entry==3510||entry==3538))
                vm.ExecuteOwnedSetup("Set "+frame+"=New "+frameClass+":Set "+frame+"."+ParentField+"=Nothing");
            vm.ExecuteOwnedSetup("Set DM=QMacroCubeMainVision");
            var shared=(Dictionary<string,object>)spec["shared"];
            foreach(var pair in shared) host.Globals.Set(pair.Key,pair.Value);
            foreach(var pair in (Dictionary<string,object>)spec["values"]) {
                Check(Regex.IsMatch(pair.Key,@"^[A-Za-z_][A-Za-z_0-9]*$"),"Unexpected scalar name");
                vm.ExecuteOwnedSetup(pair.Key+"="+Convert.ToInt32(pair.Value));
            }
            var rootInput=(Dictionary<string,object>)spec["root_slots"];
            if(retained) {
                foreach(var pair in rootInput) {
                    Check(Int32.Parse(pair.Key)==11&&entry==531,"Unexpected root slot seed");
                    vm.ExecuteOwnedSetup(ArrayName+"(11)="+Convert.ToInt32(pair.Value));
                }
            } else Check(((Dictionary<string,object>)spec["frame_slots"]).Count==0&&rootInput.Count==0,"Unexpected slot inputs");
            int limit=Convert.ToInt32(spec["max_body_steps"]), stop=spec["stop_after"]==null?-1:Convert.ToInt32(spec["stop_after"]);
            Check(limit>0&&limit<=500,"Invalid step bound");
            var records=new List<int>(); var writes=new List<object>(); var waits=new List<object>();
            string reason="fixture_stop";
            while(records.Count<limit) {
                int at=vm.Pc;
                if(retained && p.Missing.Contains(at)) {
                    bool faulted=false;
                    try { vm.Step(); } catch(InvalidOperationException ex) { faulted=ex.InnerException is MissingOriginalRecordException; }
                    Check(faulted,"Expected missing record fault");
                    reason="missing_original_record"; records.Add(at); break;
                }
                if(retained&&at==p.Code.Length) {
                    Check(vm.Step()==RunState.Finished,"Expected program end");
                    reason="program_end"; records.Add(at); break;
                }
                if(!retained&&(at==451||at==1494)) {
                    reason=at==451?"missing_original_record":"untranslated_continuation";
                    records.Add(at); break;
                }
                Check(retained?InRetainedProbe(at):InBody(at),"Unexpected path at L"+at);
                if(retained) {
                    host.MessageAvailable=records.Count>=Convert.ToInt32(spec["message_step"]);
                    host.UiOpen=records.Count<Convert.ToInt32(spec["close_step"]);
                }
                Instruction ins=p.Code[at];
                records.Add(at); vm.Step();
                if(vm.State==RunState.WaitingForMessage) waits.Add(new{record=at,kind="waiting_message"});
                if(vm.State==RunState.WaitingForUi) waits.Add(new{record=at,kind="waiting_ui"});
                if(ins.Op==28) writes.Add(new{record=at,key=p.Strings[ins.Operand],value=vm.Evaluate(RecordVm.Temp)});
                if(ins.Op==2||ins.Op==30) {
                    var random=Regex.Match(p.Strings[ins.Operand],@"^(X|Y|XXX|YYY|YC|SJ|YDX|YDY)=INT\((\d+)\*RND([+-])(\d+|INTX|INTY)\)$");
                    if(random.Success) {
                        string name=random.Groups[1].Value;
                        int span=Int32.Parse(random.Groups[2].Value), lower=Convert.ToInt32(vm.Evaluate(random.Groups[4].Value));
                        if(random.Groups[3].Value=="-") lower=-lower;
                        int result=Convert.ToInt32(vm.Evaluate(name));
                        Check(result>=lower&&result<lower+span,"RND result outside original interval");
                        vm.ExecuteOwnedSetup(name+"="+lower);
                    }
                }
                if(vm.State==RunState.IterationEnded) { reason="iteration_end"; break; }
                if(vm.State==RunState.Finished) { reason="script_stop"; break; }
                if(at==stop) break;
            }
            var final=new Dictionary<string,object>();
            foreach(string key in shared.Keys) final[key]=host.Globals.Get(key);
            var slots=new Dictionary<string,object>();
            for(int index=retained?11:36;index<=37;index++) {
                string slot=ArrayName+"("+index+")";
                if(!Convert.ToBoolean(vm.Evaluate("IsEmpty("+slot+")"))) slots[index.ToString()]=vm.Evaluate(slot);
            }
            return new{id=spec["id"],records=records,events=host.Snapshot(),reason=reason,next_record=vm.Pc,
                       writes=writes,waits=waits,final_shared=final,root_slots=slots,call_depth=vm.Depth};
        }
    }
    [STAThread] public static int Main() {
        var results=new List<object>(); string error=null;
        var serializer=new JavaScriptSerializer(){MaxJsonLength=64000000};
        try {
            CallbackGuestTest.Guard();
            byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"cube-worker-cases.json"));
            Check(Digest(raw)==CubeWorkerDigests.Cases,"Case digest changed");
            var cases=(object[])((Dictionary<string,object>)serializer.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw)))["cases"];
            Check(cases.Length==CubeWorkerDigests.CaseCount,"Case count changed");
            var program=ProgramReader.Read(Path.Combine(Lab,"07.json"),CubeWorkerDigests.Program);
            string frame=Regex.Match(program.Strings[0],@":Dim ([A-Za-z_0-9]+),[A-Za-z_0-9]+:Set ").Groups[1].Value;
            string frameClass=Regex.Match(program.Strings[1],@"^Class ([A-Za-z_0-9]+):Dim ").Groups[1].Value;
            Check(frame.Length>0&&frameClass.Length>0,"Unknown frame names");
            int header=Array.FindIndex(program.Code,r=>r.Op==29);
            Check(header>0&&header<100,"Invalid header boundary");
            var allowed=new HashSet<string>();
            for(int i=0;i<header;i++) {
                string source=program.Strings[program.Code[i].Operand];
                Check(program.Code[i].Op==30&&(source.StartsWith("Dim ")||source.StartsWith("Class "))&&!Regex.IsMatch(source,@"\b(Call|CreateObject|Execute|GetObject|Eval)\b",RegexOptions.IgnoreCase),"Unsafe header");
                allowed.Add(source);
            }
            for(int i=0;i<program.Code.Length;i++) if(InBody(i)&&(program.Code[i].Op==2||program.Code[i].Op==30)) allowed.Add(program.Strings[program.Code[i].Operand]);
            foreach(object spec in cases) results.Add(Execute(program,allowed,frame,frameClass,(Dictionary<string,object>)spec));
        } catch(Exception ex) { error=ex.ToString(); }
        if(Environment.MachineName!="DESKTOP-GAR2QIL") return 2;
        File.WriteAllText(Path.Combine(Lab,"original-cube-workers.json"),serializer.Serialize(new{ok=error==null,error=error,cases=results,
            source_program_sha256=CubeWorkerDigests.Program,case_spec_sha256=CubeWorkerDigests.Cases,
            runtime_sha256=Digest(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),synthetic_worker_ids=true,
            original_native_loaded=false,game_input_sent=false,real_worker_timing_verified=false,full_module_restored=false}));
        return error==null?0:1;
    }
}
