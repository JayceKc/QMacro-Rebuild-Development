// Fixed guest probe of the retained cube entry and tail transitions.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class CubeRetainedGuestTest {
    const string Lab = @"C:\Users\Public\Documents\QMacroLab";
    static void Check(bool ok,string message) { if(!ok) throw new InvalidOperationException(message); }
    static string Digest(byte[] data) {
        using(var hash=SHA256.Create()) return BitConverter.ToString(hash.ComputeHash(data)).Replace("-", "").ToLowerInvariant();
    }
    [STAThread] public static int Main() {
        var results=new List<object>();
        var serializer=new JavaScriptSerializer(){MaxJsonLength=64000000};
        string error=null;
        try {
            CallbackGuestTest.Guard();
            byte[] raw=File.ReadAllBytes(Path.Combine(Lab,"cube-retained-cases.json"));
            Check(Digest(raw)==CubeRetainedDigests.Cases,"Case hash differs");
            var cases=(object[])((Dictionary<string,object>)serializer.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw)))["cases"];
            Check(cases.Length==CubeRetainedDigests.CaseCount,"Case count differs");
            var program=ProgramReader.Read(Path.Combine(Lab,"07.json"),CubeRetainedDigests.Program);
            string frame=Regex.Match(program.Strings[0],@":Dim ([A-Za-z_0-9]+),[A-Za-z_0-9]+:Set ").Groups[1].Value;
            string frameClass=Regex.Match(program.Strings[1],@"^Class ([A-Za-z_0-9]+):Dim ").Groups[1].Value;
            Check(frame.Length>0&&frameClass.Length>0,"Unknown frame declarations");
            var allowed=new HashSet<string>();
            for(int at=0;at<program.Code.Length;at++) {
                var ins=program.Code[at];
                if(!CubeWorkersGuestTest.InRetainedProbe(at)||ins.Op!=2&&ins.Op!=30) continue;
                string source=program.Strings[ins.Operand];
                Check(!Regex.IsMatch(source,@"\b(CreateObject|Execute|GetObject|Eval)\b",RegexOptions.IgnoreCase),"Unexpected executable service load");
                allowed.Add(source);
            }
            foreach(object spec in cases) results.Add(CubeWorkersGuestTest.Execute(program,allowed,frame,frameClass,(Dictionary<string,object>)spec,true));
        } catch(Exception ex) { error=ex.ToString(); }
        if(Environment.MachineName!="DESKTOP-GAR2QIL") return 2;
        File.WriteAllText(Path.Combine(Lab,"original-cube-retained.json"),serializer.Serialize(new{ok=error==null,error=error,cases=results,
            source_program_sha256=CubeRetainedDigests.Program,case_spec_sha256=CubeRetainedDigests.Cases,
            runtime_sha256=Digest(File.ReadAllBytes(typeof(RecordVm).Assembly.Location)),synthetic_prefix_values=true,
            original_native_loaded=false,capture_files_written=false,game_input_sent=false,full_module_restored=false}));
        return error==null?0:1;
    }
}
