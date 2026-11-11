// Fixed guest only. Module05 root suffix; input and shutdown are recorded intents.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class FishingSuffixGuestTest {
    const string Lab=@"C:\Users\Public\Documents\QMacroLab";
    const string FailureCount="V8B92AAD77378756D";
    const string Rebait="V859CB696C584756D";

    static void Check(bool ok,string detail) {
        if(!ok) throw new InvalidOperationException(detail);
    }

    static object Execute(MacroProgram p,HashSet<string> allowed,int id,int count,int rebait,bool found,bool inverted) {
        var records=new List<int>();
        using(var host=new DryRunHost(allowed.Contains))
        using(var vm=new RecordVm(p,host.Globals,host,504)) {
            var fixture=new FishingVisionFixture(host,vm,found?-1:504,inverted);
            vm.AddOwnedObject("QMacroFishingVision",fixture);
            host.LibraryProvider=(context,name)=>{
                Check(name=="SYS","Unexpected original service");
                host.Record(context,"load_service_intent",name);
                return new FishingSystemFixture(host,context);
            };
            for(int i=0;i<8&&vm.Pc!=504;i++) vm.Step();
            Check(vm.Pc==504&&vm.Depth==0,"Fishing root did not dispatch");
            vm.ExecuteOwnedSetup("Set DM=QMacroFishingVision:"+FailureCount+"="+count+":"+Rebait+"="+rebait+
                                 ":MX=314:MY=256:CS=13:g_iSimulateModeInVBSBlock=0");
            string reason=null;
            for(int i=0;i<40;i++) {
                int at=vm.Pc;
                records.Add(at);
                if(p.Missing.Contains(at)) {
                    Check(at==115||at==501,"Unexpected missing boundary");
                    reason="missing_original_record";break;
                }
                Check(at>=504&&at<=539,"Fishing fixture left reviewed root suffix");
                if(vm.Step()==RunState.Finished) {reason="script_stop";break;}
            }
            Check(reason!=null&&vm.Depth==0,"Unbounded fishing suffix");
            return new{id=id,failure_count=count,rebait=rebait,found=found,inverted=inverted,records=records,reason=reason,
                       next_record=vm.Pc,final_failure_count=vm.Evaluate(FailureCount),final_cycle_count=vm.Evaluate("CS"),
                       events=host.Snapshot(),query_count=fixture.Queries};
        }
    }

    [STAThread] public static int Main() {
        var cases=new List<object>();
        object defaultEntry=null;
        object[] form=null;
        string error=null;
        try {
            CallbackGuestTest.Guard();
            var p=ProgramReader.Read(Path.Combine(Lab,"05.json"),FishingEvidenceDigests.Program);
            var header=BattleFormGuestTest.Header(p,3);
            defaultEntry=BattleFormGuestTest.DefaultEntry(p,header,3);
            form=new[]{
                BattleFormGuestTest.Run(p,header,3,925,925,926,927,false,true),
                BattleFormGuestTest.Run(p,header,3,925,925,926,927,true,true),
                BattleFormGuestTest.Run(p,header,3,924,925,926,927,true,false)};
            for(int at=504;at<=539;at++) {
                var ins=p.Code[at];
                Check(!p.Missing.Contains(at),"Retained suffix record unavailable");
                if(ins.Op==2||ins.Op==30) {
                    string source=p.Strings[ins.Operand];
                    Check(source.IndexOf("CreateObject",StringComparison.OrdinalIgnoreCase)<0,"Unexpected direct service load");
                    header.Add(source);
                }
            }
            cases.Add(Execute(p,header,1,2,0,true,false));
            cases.Add(Execute(p,header,2,4,1,true,true));
            cases.Add(Execute(p,header,3,0,1,false,true));
            cases.Add(Execute(p,header,4,4,0,false,false));
        } catch(Exception ex) { error=ex.ToString(); }
        if(Environment.MachineName!="DESKTOP-GAR2QIL") return 2;
        string runtimeHash;
        using(var h=SHA256.Create())
            runtimeHash=BitConverter.ToString(h.ComputeHash(File.ReadAllBytes(typeof(RecordVm).Assembly.Location))).Replace("-", "").ToLowerInvariant();
        var report=new{ok=error==null,error=error,cases=cases,default_entry=defaultEntry,form=form,
            source_program_sha256=FishingEvidenceDigests.Program,runtime_sha256=runtimeHash,
            original_native_loaded=false,game_input_sent=false,os_exit_called=false};
        File.WriteAllText(Path.Combine(Lab,"original-fishing-suffix.json"),new JavaScriptSerializer().Serialize(report));
        return error==null?0:1;
    }
}
