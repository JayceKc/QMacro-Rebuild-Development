// Fixed VMware guest only. Compare the module08 default dispatch and Form1 tail.
using System;
using System.IO;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class GatheringHostGuestTest {
    const string Lab=@"C:\Users\Public\Documents\QMacroLab";

    [STAThread] public static int Main() {
        object defaultEntry=null;
        object[] form=null;
        string error=null;
        try {
            CallbackGuestTest.Guard();
            var p=ProgramReader.Read(Path.Combine(Lab,"08.json"),GatheringMainDigests.Program);
            var header=BattleFormGuestTest.Header(p,6);
            defaultEntry=BattleFormGuestTest.DefaultEntry(p,header,6);
            form=new[]{
                BattleFormGuestTest.Run(p,header,6,1622,1622,1623,1624,false,true),
                BattleFormGuestTest.Run(p,header,6,1622,1622,1623,1624,true,true),
                BattleFormGuestTest.Run(p,header,6,1621,1622,1623,1624,true,false)};
        } catch(Exception ex) { error=ex.ToString(); }
        if(Environment.MachineName!="DESKTOP-GAR2QIL") return 2;
        string runtime;
        using(var h=SHA256.Create())
            runtime=BitConverter.ToString(h.ComputeHash(File.ReadAllBytes(typeof(RecordVm).Assembly.Location))).Replace("-", "").ToLowerInvariant();
        var report=new{ok=error==null,error=error,default_entry=defaultEntry,form=form,
            source_program_sha256=GatheringMainDigests.Program,runtime_sha256=runtime,
            original_native_loaded=false,game_input_sent=false,real_ui_created=false};
        File.WriteAllText(Path.Combine(Lab,"original-gathering-host.json"),new JavaScriptSerializer().Serialize(report));
        return error==null?0:1;
    }
}
