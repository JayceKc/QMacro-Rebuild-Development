// Controlled original VBScript in the fixed VMware guest, with recording-only effects.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

[ComVisible(true), ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class SharedBattleVision {
    readonly RecordVm vm;
    readonly DryRunHost host;
    readonly Dictionary<string,object> overrides;
    readonly Dictionary<string,object> misses;
    readonly bool found;
    readonly Queue<object[]> builtinPoints;
    readonly int? cursorPacked;
    public SharedBattleVision(RecordVm vm,DryRunHost host,Dictionary<string,object> spec) {
        this.vm=vm; this.host=host; found=(bool)spec["default_found"];
        overrides=(Dictionary<string,object>)spec["return_overrides"];
        misses=(Dictionary<string,object>)spec["miss_budget"];
        object points;
        if(spec.TryGetValue("builtin_points",out points))
            builtinPoints=new Queue<object[]>(Array.ConvertAll((object[])points,x=>(object[])x));
        object cursor;
        if(spec.TryGetValue("cursor_packed",out cursor)) cursorPacked=Convert.ToInt32(cursor);
    }
    int Query(string kind,object[] arguments,int l,int t,int r,int b,out object x,out object y) {
        bool hit=found&&!misses.ContainsKey(vm.Pc.ToString())&&l<r&&t<b;
        x=hit?Math.Min(l+1,r-1):-1; y=hit?Math.Min(t+2,b-1):-1;
        int result=kind=="find_color"?(hit?1:0):(hit?0:-1);
        object forced; if(overrides.TryGetValue(vm.Pc.ToString(),out forced)) result=Convert.ToInt32(forced);
        host.Record(vm,kind,new{arguments=arguments,x=x,y=y,return_value=result}); return result;
    }
    public int FindColor(int l,int t,int r,int b,string color,double sim,int dir,out object x,out object y) {
        return Query("find_color",new object[]{l,t,r,b,color,sim,dir},l,t,r,b,out x,out y);
    }
    public int FindPic(int l,int t,int r,int b,string path,string delta,double sim,int dir,out object x,out object y) {
        return Query("find_pic",new object[]{l,t,r,b,path,delta,sim,dir},l,t,r,b,out x,out y);
    }
    public int MoveTo(int x,int y) { host.Record(vm,"move_to",new[]{x,y}); return 1; }
    public int Capture(int left,int top,int right,int bottom,string path) {
        host.Record(vm,"capture_intent",new object[]{left,top,right,bottom,path});return found?1:0;
    }
    public int SetShowErrorMsg(int value) { host.Record(vm,"dm_error_policy_intent",new[]{value}); return 1; }
    public int EnableRealMouse(int mode,int delay,int distance) {
        host.Record(vm,"dm_real_mouse_intent",new[]{mode,delay,distance}); return 1;
    }
    [ComVisible(false)]
    public object Builtin(RecordVm context,string name,object[] args) {
        if(context==vm&&name=="builtin_cursor"&&args.Length==0&&cursorPacked.HasValue) return cursorPacked.Value;
        if(context!=vm||(name!="builtin_color"&&name!="builtin_picture"))
            throw new InvalidOperationException("Unexpected Runner builtin");
        bool hit=found&&!misses.ContainsKey(vm.Pc.ToString());
        int x=hit?Math.Min(Convert.ToInt32(args[0])+1,Convert.ToInt32(args[2])):-1;
        int y=hit?Math.Min(Convert.ToInt32(args[1])+2,Convert.ToInt32(args[3])):-1;
        if(builtinPoints!=null) {
            object[] point=builtinPoints.Dequeue();
            x=Convert.ToInt32(point[0]);y=Convert.ToInt32(point[1]);
            if((x!=-1||y!=-1)&&(x<Convert.ToInt32(args[0])||x>Convert.ToInt32(args[2])||
                                y<Convert.ToInt32(args[1])||y>Convert.ToInt32(args[3])))
                throw new InvalidOperationException("Fixture point outside dynamic rectangle");
        }
        return x*8192+y;
    }
}

[ComVisible(true), ClassInterface(ClassInterfaceType.AutoDual)]
public sealed class SharedBattleRecorder {
    readonly RecordVm vm;
    readonly DryRunHost host;
    public SharedBattleRecorder(RecordVm vm,DryRunHost host) { this.vm=vm;this.host=host; }
    public void PrintScreen(int left,int top,int right,int bottom,string path) {
        host.Record(vm,"screenshot_intent",new object[]{left,top,right,bottom,path});
    }
    public void RequestRestart(int mode) {
        if(mode!=1) throw new InvalidOperationException("Unexpected restart mode");
        host.Record(vm,"exit_script",mode);
    }
}

public static class SharedBattleGuestTest {
    const string Lab=@"C:\Users\Public\Documents\QMacroLab";
    const string Parent="F2730835_2229_445E_97C7_13F76l2771DA";
    const string Temporary="F2730835_2229_445E_97C7_l3F76l2771DA";
    const string RootSlots="F2730835_2229_445E_97C7_l3F761277lDA";
    const string CaptureClockSuffix=".V87DBD9917378756D=YEAR(NOW) & MONTH(NOW) & DAY(NOW) & HOUR(NOW) & MINUTE(NOW) & SECOND(NOW)";
    const string ExitRestart="Call QMLibrary.ExitScript(1)";
    static void Check(bool ok,string message) { if(!ok) throw new InvalidOperationException(message); }
    static string Digest(byte[] raw) {
        using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(raw)).Replace("-", "").ToLowerInvariant();
    }
    static object Execute(MacroProgram original,HashSet<int> domain,HashSet<string> allowed,string frame,string frameClass,
                          Dictionary<string,object> spec,Dictionary<string,object> boundaries,bool control) {
        int entry=Convert.ToInt32(spec["entry"]), end=Convert.ToInt32(spec["last"]), scaffold=original.Code.Length;
        bool wrapper=control&&(bool)spec["worker_wrapper"];
        object rootSlots;
        bool root=spec.TryGetValue("root_slots",out rootSlots);
        Check(domain.Contains(entry)&&domain.Contains(end)&&original.Code[end].Op==(root?16:wrapper?23:13),"Unexpected direct entry");
        var p=original;
        int dispatch=entry;
        if(!root) {
            var expanded=new Instruction[scaffold+1];Array.Copy(original.Code,expanded,scaffold);
            expanded[scaffold]=new Instruction(12,entry);
            p=new MacroProgram(){Code=expanded,Strings=original.Strings,Name=original.Name};
            foreach(int missing in original.Missing) p.Missing.Add(missing);
            dispatch=scaffold;
        }
        using(var host=new DryRunHost(allowed.Contains))
        using(var vm=new RecordVm(p,host.Globals,host,dispatch)) {
            var vision=new SharedBattleVision(vm,host,spec);
            vm.AddOwnedObject("QMacroCubeMainVision",vision);
            host.BuiltinProvider=vision.Builtin;
            string clock=null;
            object clockParts;
            if(spec.TryGetValue("clock",out clockParts)) {
                var values=Array.ConvertAll((object[])clockParts,x=>Convert.ToInt32(x));
                Check(values.Length==6,"Invalid clock fixture");
                var date=new DateTime(values[0],values[1],values[2],values[3],values[4],values[5]);
                clock=String.Format(CultureInfo.InvariantCulture,"(DateSerial({0},{1},{2}) + TimeSerial({3},{4},{5}))",
                                    date.Year,date.Month,date.Day,date.Hour,date.Minute,date.Second);
                var recorder=new SharedBattleRecorder(vm,host);
                vm.AddOwnedObject("QMacroRestartRecorder",recorder);
                host.LibraryProvider=(context,name)=>{
                    Check(name=="PIC","Unexpected fixture library");
                    host.Record(context,"load_service_intent",name);return recorder;
                };
            }
            host.SourceRewrite=(context,source)=>{
                if(source=="SET DM=CREATEOBJECT(\"dm.dmsoft\")") return "Set DM=QMacroCubeMainVision";
                if(clock!=null&&source==frame+CaptureClockSuffix) return source.Replace("NOW",clock);
                if(clock!=null&&source==ExitRestart) return "Call QMacroRestartRecorder.RequestRestart(1)";
                return source;
            };
            if(control) host.WorkerStarter=(context,target)=>10000+context.Pc;
            for(int i=0;i<130&&vm.Pc!=dispatch;i++) vm.Step();
            Check(vm.Pc==dispatch,"Header failed to dispatch");
            object fields;
            if(spec.TryGetValue("frame_fields",out fields)) {
                var declarations=Array.FindAll(original.Strings,s=>s.StartsWith("Class ")&&s.Contains(":Dim A1:")&&s.Contains(":Dim N:"));
                Check(!wrapper&&declarations.Length==1,"Unknown scan frame class");
                frameClass=Regex.Match(declarations[0],@"^Class ([A-Za-z_0-9]+):Dim ").Groups[1].Value;
                Check(frameClass.Length>0,"Unknown scan frame declaration");
            }
            if(!wrapper&&!root) vm.ExecuteOwnedSetup("Set "+frame+"=New "+frameClass+":Set "+frame+"."+Parent+"=Nothing");
            if(root) {
                foreach(var pair in (Dictionary<string,object>)rootSlots) {
                    int slot=Int32.Parse(pair.Key,CultureInfo.InvariantCulture);
                    Check(slot>=0&&slot<=256&&pair.Value is int,"Unexpected root slot fixture");
                    vm.ExecuteOwnedSetup(RootSlots+"("+slot+")="+pair.Value);
                }
            }
            if(fields!=null) {
                foreach(var pair in (Dictionary<string,object>)fields) {
                    Check(Regex.IsMatch(pair.Key,@"^V[A-F0-9]+$"),"Unexpected named frame input");
                    string literal=pair.Value is string
                        ? "\""+((string)pair.Value).Replace("\"","\"\"")+"\""
                        : Convert.ToString(pair.Value,CultureInfo.InvariantCulture);
                    vm.ExecuteOwnedSetup(frame+"."+pair.Key+"="+literal);
                }
            }
            vm.ExecuteOwnedSetup("Set DM=QMacroCubeMainVision");
            var shared=(Dictionary<string,object>)spec["shared"];
            foreach(var pair in shared) host.Globals.Set(pair.Key,pair.Value);
            foreach(var pair in (Dictionary<string,object>)spec["values"]) {
                Check(Regex.IsMatch(pair.Key,@"^[A-Za-z_][A-Za-z_0-9]*$"),"Invalid scalar fixture");
                string literal=Convert.ToString(pair.Value,CultureInfo.InvariantCulture);
                Check(Regex.IsMatch(literal,@"^-?\d+(\.\d+)?$"),"Invalid numeric fixture value");
                if((pair.Value is double||pair.Value is decimal)&&!literal.Contains(".")) literal+=".0";
                vm.ExecuteOwnedSetup(pair.Key+"="+literal);
            }
            int limit=Convert.ToInt32(spec["max_body_steps"]);
            Check(limit>0&&limit<=(root?2400:600),"Invalid record limit");
            if(!root) vm.Step();
            var records=new List<int>(); var comparisons=new List<object>(); var alternateOutputs=new List<object>();
            var builtinReplies=new List<object>();
            var captureReplies=new List<object>();
            var randomReplies=new List<object>();
            var cursorReplies=new List<object>();
            string reason="fixture_stop";
            int? restartRecord=null;
            while(records.Count<limit) {
                int at=vm.Pc;
                object boundary;
                if(boundaries.TryGetValue(at.ToString(),out boundary)) {
                    reason=(string)boundary;
                    if(root) Check(reason=="missing_original_record"&&p.Missing.Contains(at),"Invalid root boundary");
                    records.Add(at);break;
                }
                Check(domain.Contains(at),"Body left reviewed domain at L"+at);
                Instruction ins=p.Code[at]; records.Add(at); vm.Step();
                if(ins.Op==2||ins.Op==30) {
                    string source=p.Strings[ins.Operand];
                    if(clock!=null&&source==ExitRestart) {
                        Check(vm.Pc==at+1,"Restart observation did not finish");
                        restartRecord=at;reason="restart_requested";break;
                    }
                    var compare=Regex.Match(source,@"^(V[A-F0-9_]+)=DM_RET=DM\.(FINDPIC|FINDCOLOR)\(");
                    if(compare.Success) comparisons.Add(new{record=at,value=vm.Evaluate(compare.Groups[1].Value),dm_ret=vm.Evaluate("DM_RET")});
                    if(control&&source.StartsWith("DM_RET=DM.FIND")&&source.EndsWith(",INTXX,INTYY)")) {
                        alternateOutputs.Add(new{record=at,values=new[]{vm.Evaluate("INTX"),vm.Evaluate("INTY"),vm.Evaluate("INTXX"),vm.Evaluate("INTYY")}});
                    }
                    if(source.StartsWith("Call FindPic(")||source.StartsWith("Call FindColorEx(")) {
                        var outputs=Regex.Match(source,@",(INTX(?:X|12|16|122)?),(INTY(?:Y|12|16|122)?)\)$");
                        if(!outputs.Success&&fields!=null)
                            outputs=Regex.Match(source,@",(F278O335_2229_445E_97C7_l3F76l2771DA__6),(F278O335_2229_445E_97C7_l3F76l2771DA__7)\)$");
                        Check(outputs.Success,"Unreviewed Runner builtin output pair");
                        builtinReplies.Add(new{
                            record=at,x=vm.Evaluate(outputs.Groups[1].Value),y=vm.Evaluate(outputs.Groups[2].Value),
                            dm_ret=vm.Evaluate("DM_RET")});
                    }
                    if(source.StartsWith("DM_RET=DM.CAPTURE("))
                        captureReplies.Add(new{record=at,dm_ret=vm.Evaluate("DM_RET")});
                    if(source=="Call GetCursorPos(MX,MY)")
                        cursorReplies.Add(new{record=at,x=vm.Evaluate("MX"),y=vm.Evaluate("MY")});
                    var random=Regex.Match(source,@"^([A-Z]+)=INT\((\d+)\*RND([+-])(\d+|INTX|INTY)\)$");
                    if(random.Success) {
                        string name=random.Groups[1].Value;
                        int span=Int32.Parse(random.Groups[2].Value), lower=Convert.ToInt32(vm.Evaluate(random.Groups[4].Value));
                        if(random.Groups[3].Value=="-") lower=-lower;
                        int value=Convert.ToInt32(vm.Evaluate(name));
                        Check(lower<=value&&value<lower+span,"Original random bounds differed");
                        int supplied=lower+((bool)spec["random_upper"]?span-1:0);
                        vm.ExecuteOwnedSetup(name+"="+supplied);
                        randomReplies.Add(new{record=at,lower=lower,span=span,supplied=supplied});
                    }
                }
                if(!root&&vm.Pc==scaffold+1) {
                    Check(at==end&&vm.Depth==0&&Convert.ToBoolean(vm.Evaluate(frame+" Is Nothing")),"Incorrect root return");
                    reason="routine_return"; break;
                }
                if(vm.State==RunState.Finished) { reason="script_stop"; break; }
                if(vm.State==RunState.IterationEnded) { reason="iteration_end"; break; }
            }
            var final=new Dictionary<string,object>();
            foreach(string key in shared.Keys) final[key]=host.Globals.Get(key);
            var rootValues=new List<object>();
            if(root) foreach(object slot in (object[])spec["root_observe_slots"])
                rootValues.Add(vm.Evaluate(RootSlots+"("+Convert.ToInt32(slot)+")"));
            var scalarValues=new List<object>();
            object names;
            if(spec.TryGetValue("observe_scalars",out names)) foreach(string name in (object[])names) {
                Check(Regex.IsMatch(name,@"^[A-Za-z_][A-Za-z_0-9]*$"),"Invalid observation name");
                scalarValues.Add(vm.Evaluate(name));
            }
            return new{id=spec["id"],records=records,events=host.Snapshot(),comparisons=comparisons,alternate_outputs=alternateOutputs,
                builtin_replies=builtinReplies,capture_replies=captureReplies,random_replies=randomReplies,cursor_replies=cursorReplies,
                return_value=fields!=null&&reason=="routine_return"?vm.Evaluate(Temporary):null,
                final_shared=final,reason=reason,next_record=restartRecord??(reason=="routine_return"?end+1:vm.Pc),
                call_depth=reason=="routine_return"?0:vm.Depth-(root?0:1),root_values=rootValues,scalar_values=scalarValues};
        }
    }
    [STAThread] public static int Main(string[] args) {
        if(args.Length<1||args.Length>2||!SharedBattleDigests.Programs.ContainsKey(args[0])||
           (args.Length==2&&args[1]!="control"&&args[1]!="recovery"&&args[1]!="restart"&&args[1]!="routes"&&args[1]!="tail"&&args[1]!="scan"&&args[1]!="root"&&args[1]!="small")) return 2;
        bool control=args.Length==2;
        string family=control?"battle-"+args[1]+"-":"battle-";
        string module=args[0], error=null;
        var serializer=new JavaScriptSerializer(){MaxJsonLength=64000000}; var results=new List<object>();
        try {
            CallbackGuestTest.Guard();
            byte[] raw=File.ReadAllBytes(Path.Combine(Lab,family+module+"-cases.json"));
            Check(Digest(raw)==SharedBattleDigests.Cases[module],"Case hash changed");
            var fixture=(Dictionary<string,object>)serializer.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
            var original=ProgramReader.Read(Path.Combine(Lab,module+".json"),SharedBattleDigests.Programs[module]);
            string frame=Regex.Match(original.Strings[0],@":Dim ([A-Za-z_0-9]+),[A-Za-z_0-9]+:Set ").Groups[1].Value;
            string frameClass=Regex.Match(original.Strings[1],@"^Class ([A-Za-z_0-9]+):Dim ").Groups[1].Value;
            Check(frame.Length>0&&frameClass.Length>0,"Unknown frame declarations");
            var domain=new HashSet<int>(); var allowed=new HashSet<string>();
            int header=Array.FindIndex(original.Code,r=>r.Op==29);
            Check(header>0&&header<130,"Invalid header boundary");
            for(int at=0;at<header;at++) {
                string source=original.Strings[original.Code[at].Operand];
                Check(original.Code[at].Op==30&&(source.StartsWith("Dim ")||source.StartsWith("Class "))&&!Regex.IsMatch(source,@"\b(Call|CreateObject|Execute|GetObject|Eval)\b",RegexOptions.IgnoreCase),"Unsafe header");
                allowed.Add(source);
            }
            foreach(object range in (object[])fixture["ranges"]) {
                var bounds=(object[])range;
                for(int at=Convert.ToInt32(bounds[0]);at<=Convert.ToInt32(bounds[1]);at++) {
                    Check(at>=header&&at<original.Code.Length&&!original.Missing.Contains(at),"Unreviewed retained record");
                    domain.Add(at);
                    Instruction ins=original.Code[at];
                    if(ins.Op==2||ins.Op==30) {
                        string source=original.Strings[ins.Operand];
                        Check(source=="SET DM=CREATEOBJECT(\"dm.dmsoft\")"||!Regex.IsMatch(source,@"\b(CreateObject|Execute|GetObject|Eval)\b",RegexOptions.IgnoreCase),"Unexpected service load");
                        allowed.Add(source);
                    }
                }
            }
            var boundaries=control?(Dictionary<string,object>)fixture["boundaries"]:new Dictionary<string,object>();
            foreach(object spec in (object[])fixture["cases"]) results.Add(Execute(original,domain,allowed,frame,frameClass,(Dictionary<string,object>)spec,boundaries,control));
        } catch(Exception ex) { error=ex.ToString(); }
        if(Environment.MachineName!="DESKTOP-GAR2QIL") return 2;
        File.WriteAllText(Path.Combine(Lab,"original-"+family+module+".json"),serializer.Serialize(new{ok=error==null,error=error,cases=results,module=module,
            source_program_sha256=SharedBattleDigests.Programs[module],case_spec_sha256=SharedBattleDigests.Cases[module],
            runtime_sha256=Digest(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),synthetic_context=true,
            original_native_loaded=false,game_input_sent=false,full_module_restored=false}));
        return error==null?0:1;
    }
}
