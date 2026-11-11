// Execute the retained VBScript through the owned dispatcher in the fixed guest.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

[ComVisible(true), ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class CubeMainVisionFixture {
    readonly CubeVisionFixture vision;
    readonly DryRunHost host;
    readonly RecordVm vm;
    public CubeMainVisionFixture(DryRunHost host, RecordVm vm, Dictionary<string,object> spec) {
        this.host = host; this.vm = vm; vision = new CubeVisionFixture(host, vm, spec);
    }
    public int FindColor(int l,int t,int r,int b,string color,double sim,int dir,out object x,out object y) {
        return vision.FindColor(l,t,r,b,color,sim,dir,out x,out y);
    }
    public int FindPic(int l,int t,int r,int b,string path,string delta,double sim,int dir,out object x,out object y) {
        return vision.FindPic(l,t,r,b,path,delta,sim,dir,out x,out y);
    }
    public int MoveTo(int x,int y) { return vision.MoveTo(x,y); }
    public int Capture(int l,int t,int r,int b,string path) {
        host.Record(vm,"capture_intent",new object[]{l,t,r,b,path}); return 1;
    }
    public int SetShowErrorMsg(int value) {
        host.Record(vm,"dm_error_policy_intent",new[]{value}); return 1;
    }
    public int EnableRealMouse(int mode,int delay,int distance) {
        host.Record(vm,"dm_real_mouse_intent",new[]{mode,delay,distance}); return 1;
    }
}

public static class CubeMainGuestTest {
    const string Lab = @"C:\Users\Public\Documents\QMacroLab";
    const string Slots = "F2730835_2229_445E_97C7_l3F761277lDA";
    const string Parent = "F2730835_2229_445E_97C7_13F76l2771DA";
    const string OriginalCreate = "SET DM=CREATEOBJECT(\"dm.dmsoft\")";
    const string OwnedCreate = "Set DM=QMacroCubeMainVision";
    static readonly HashSet<int> RestoreRecords = new HashSet<int>{1492,3362,3485,6441,6688,6813};
    static void Check(bool ok,string why) { if(!ok) throw new InvalidOperationException(why); }
    static string Sha(byte[] raw) {
        using(var hash=SHA256.Create()) return BitConverter.ToString(hash.ComputeHash(raw)).Replace("-", "").ToLowerInvariant();
    }
    static bool Body(int at) {
        return at>=857&&at<=1493 || at>=1677&&at<=3363 || at>=3365&&at<=3486 ||
               at>=5020&&at<=6442 || at>=6657&&at<=6689 || at>=6740&&at<=6814;
    }
    static object Execute(MacroProgram p, int scaffold, HashSet<string> allowed, string frame, string rootClass, Dictionary<string,object> spec) {
        using(var host=new DryRunHost(allowed.Contains))
        using(var vm=new RecordVm(p,host.Globals,host,scaffold)) {
            vm.AddOwnedObject("QMacroCubeMainVision",new CubeMainVisionFixture(host,vm,spec));
            host.SourceRewrite=(context,source)=>{
                if(context.Pc!=1678) return source;
                Check(source==OriginalCreate,"DM creation source changed"); return OwnedCreate;
            };
            host.LibraryProvider=(context,name)=>{
                Check(context==vm&&name=="SYS","Unexpected library");
                host.Record(vm,"load_service_intent",name); return new CubeSysIntent(host,vm);
            };
            for(int n=0;n<100&&vm.Pc!=scaffold;n++) vm.Step();
            Check(vm.Pc==scaffold,"Header scaffold not reached");
            vm.ExecuteOwnedSetup("Set "+frame+"=New "+rootClass+":Set "+frame+"."+Parent+"=Nothing:Set FixtureRoot="+frame);
            var shared=(Dictionary<string,object>)spec["shared"];
            foreach(var entry in shared) host.Globals.Set(entry.Key,entry.Value);
            foreach(var entry in (Dictionary<string,object>)spec["values"]) {
                Check(Regex.IsMatch(entry.Key,@"^[A-Za-z_][A-Za-z0-9_]*$"),"Invalid scalar name");
                vm.ExecuteOwnedSetup(entry.Key+"="+Convert.ToInt32(entry.Value));
            }
            foreach(var entry in (Dictionary<string,object>)spec["frame_slots"]) {
                int slot=Int32.Parse(entry.Key); Check(slot>=0&&slot<=256,"Invalid seed slot");
                vm.ExecuteOwnedSetup(frame+"."+Slots+"("+slot+")="+Convert.ToInt32(entry.Value));
            }
            int limit=Convert.ToInt32(spec["max_body_steps"]), stopAfter=spec["stop_after"]==null?-1:Convert.ToInt32(spec["stop_after"]);
            Check(limit>0&&limit<=3000,"Invalid body limit");
            vm.Step();
            var records=new List<int>(); var restores=new List<object>(); var accesses=new List<object>();
            var parentReferences=new Stack<string>();
            while(vm.State!=RunState.Finished && records.Count<limit) {
                int at=vm.Pc; Check(Body(at),"Escaped reviewed body at L"+at);
                var instruction=p.Code[at];
                string source=instruction.Op==2||instruction.Op==30?p.Strings[instruction.Operand]:null;
                if(source!=null&&source.StartsWith("Set ")&&source.Contains("=New ")) {
                    string reference="FixtureParent"+parentReferences.Count;
                    vm.ExecuteOwnedSetup("Set "+reference+"="+frame); parentReferences.Push(reference);
                }
                records.Add(at); vm.Step();
                if(instruction.Op==27||instruction.Op==28) {
                    accesses.Add(new{record=at,kind=instruction.Op==27?"read_global":"write_global",
                        key=p.Strings[instruction.Operand],value=vm.Evaluate(RecordVm.Temp)});
                }
                if(RestoreRecords.Contains(at)) {
                    Check(parentReferences.Count>0,"Unexpected root restoration");
                    string reference=parentReferences.Pop();
                    Check(Convert.ToBoolean(vm.Evaluate(frame+" Is "+reference)),"Parent object identity changed");
                    restores.Add(new{record=at,depth=parentReferences.Count+1,return_empty=Convert.ToBoolean(vm.Evaluate("IsEmpty("+RecordVm.Temp+")"))});
                    vm.ExecuteOwnedSetup("Set "+reference+"=Nothing");
                }
                if(source!=null) {
                    var random=Regex.Match(source,@"^(X|Y|XXX|YYY)=INT\((\d+)\*RND\+(INTX|INTY|\d+)\)$");
                    if(random.Success) {
                        string name=random.Groups[1].Value;
                        int span=Int32.Parse(random.Groups[2].Value), lower=Convert.ToInt32(vm.Evaluate(random.Groups[3].Value));
                        int actual=Convert.ToInt32(vm.Evaluate(name));
                        Check(actual>=lower&&actual<lower+span,"Original RND result out of bounds");
                        vm.ExecuteOwnedSetup(name+"="+(lower+((bool)spec["random_upper"]?span-1:0)));
                    }
                }
                if(at==stopAfter) break;
            }
            var final=new Dictionary<string,object>();
            foreach(string key in shared.Keys) final[key]=host.Globals.Get(key);
            var rootSlots=new Dictionary<string,object>();
            foreach(int index in new[]{5,47,54,55,255}) {
                string slot="FixtureRoot."+Slots+"("+index+")";
                rootSlots[index.ToString()]=Convert.ToBoolean(vm.Evaluate("IsEmpty("+slot+")"))?null:vm.Evaluate(slot);
            }
            return new{id=spec["id"],records=records,events=host.Snapshot(),reason=vm.State==RunState.Finished?"script_stop":"fixture_stop",
                next_record=vm.Pc,shared_accesses=accesses,final_shared=final,restores=restores,root_slots=rootSlots,frame_depth=parentReferences.Count+1};
        }
    }
    [STAThread] public static int Main() {
        string error=null; var results=new List<object>();
        var serializer=new JavaScriptSerializer(){MaxJsonLength=64000000};
        try {
            CallbackGuestTest.Guard();
            byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"cube-main-cases.json"));
            Check(Sha(raw)==CubeMainDigests.Cases,"Case digest changed");
            var cases=(object[])((Dictionary<string,object>)serializer.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw)))["cases"];
            Check(cases.Length==CubeMainDigests.CaseCount,"Unexpected case count");
            var original=ProgramReader.Read(Path.Combine(Lab,"07.json"),CubeMainDigests.Program);
            string frame=Regex.Match(original.Strings[0],@":Dim ([A-Za-z_0-9]+),[A-Za-z_0-9]+:Set ").Groups[1].Value;
            string rootClass=Regex.Match(original.Strings[1],@"^Class ([A-Za-z_0-9]+):Dim ").Groups[1].Value;
            Check(frame.Length>0&&rootClass.Length>0,"Unknown frame declarations");
            var allowed=new HashSet<string>();
            int header=Array.FindIndex(original.Code,r=>r.Op==29);
            Check(header>0&&header<100,"Unknown header boundary");
            for(int i=0;i<header;i++) {
                string source=original.Strings[original.Code[i].Operand];
                Check(original.Code[i].Op==30&&(source.StartsWith("Dim ")||source.StartsWith("Class "))&&!Regex.IsMatch(source,@"\b(Call|CreateObject|Execute|GetObject|Eval)\b",RegexOptions.IgnoreCase),"Unsafe declaration");
                allowed.Add(source);
            }
            for(int i=0;i<original.Code.Length;i++) {
                if(Body(i)&&(original.Code[i].Op==2||original.Code[i].Op==30)) allowed.Add(original.Strings[original.Code[i].Operand]);
            }
            int scaffold=original.Code.Length;
            var expanded=new Instruction[scaffold+1]; Array.Copy(original.Code,expanded,scaffold); expanded[scaffold]=new Instruction(12,1677);
            var p=new MacroProgram(){Code=expanded,Name=original.Name,Strings=original.Strings};
            foreach(int missing in original.Missing) p.Missing.Add(missing);
            foreach(object spec in cases) results.Add(Execute(p,scaffold,allowed,frame,rootClass,(Dictionary<string,object>)spec));
        } catch(Exception ex) { error=ex.ToString(); }
        if(Environment.MachineName!="DESKTOP-GAR2QIL") return 2;
        File.WriteAllText(Path.Combine(Lab,"original-cube-main.json"),serializer.Serialize(new{ok=error==null,error=error,cases=results,
            case_spec_sha256=CubeMainDigests.Cases,source_program_sha256=CubeMainDigests.Program,
            runtime_sha256=Sha(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),rewritten_records=new[]{1678},
            synthetic_root_frame=true,original_native_loaded=false,game_input_sent=false,full_module_restored=false}));
        return error==null?0:1;
    }
}
