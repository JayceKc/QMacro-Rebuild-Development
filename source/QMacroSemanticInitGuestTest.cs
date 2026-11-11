using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class SemanticInitGuestTest {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 static void Require(bool value,string message){if(!value)throw new Exception(message);}
 static string Lhs(string code){return code.Substring(0,code.IndexOf('='));}
 static object Run(MacroProgram p,int potion,int skill,int speed,int flags,string gms,bool assertCanonical){
  var allowed=new HashSet<string>(StringComparer.Ordinal);
  for(int i=0;i<p.Code.Length;i++){
   var r=p.Code[i];if(r.Op!=2&&r.Op!=30)continue;if(i<16||i>=1644){
    string source=p.Strings[r.Operand];Require(!Regex.IsMatch(source,@"\b(CreateObject|GetObject|Execute|CallAPI2|Shell)\b",RegexOptions.IgnoreCase),"Unexpected initialization side effect");allowed.Add(source);
   }
  }
  var targets=new List<int>();var ids=new List<int>();int id=1000;
  using(var host=new DryRunHost(s=>allowed.Contains(s)))using(var vm=new RecordVm(p,host.Globals,host,1644)){
   host.SetUiProperty("Form1.ComboBox1.ListIndex",potion);host.SetUiProperty("Form1.ComboBox2.ListIndex",skill);host.SetUiProperty("Form1.ComboBox3.ListIndex",speed);
   host.SetUiProperty("Form1.InputBox1.Text",gms);
   host.SetUiProperty("Form1.CheckBox1.Value",(flags&1)!=0?1:0);host.SetUiProperty("Form1.CheckBox2.Value",(flags&2)!=0?1:0);
   host.SetUiProperty("Form1.CheckBox3.Value",(flags&4)!=0?1:0);host.SetUiProperty("Form1.CheckBox4.Value",(flags&8)!=0?1:0);
   host.WorkerStarter=(parent,entry)=>{
    Require(p.Code[entry].Op==2&&p.Code[entry+1].Op==12&&p.Code[entry+2].Op==23,"Unexpected reconstructed worker wrapper");
    targets.Add(p.Code[entry+1].Operand);ids.Add(++id);return id;
   };
   int steps=0;while(vm.Pc!=1920&&steps++<1000)vm.Step();Require(vm.Pc==1920,"Main failed to reach idle entry");
   Require(Convert.ToInt32(vm.Evaluate(Lhs(p.Strings[46])) )==potion,"Potion index lost");
   Require(Convert.ToInt32(vm.Evaluate(Lhs(p.Strings[50])) )==skill,"Skill index lost");
   Require(Convert.ToInt32(host.Globals.Get(p.Strings[55]))==speed,"Global speed lost");
   Require(Convert.ToString(host.Globals.Get(p.Strings[72]))==gms,"GMS text coerced unexpectedly");
   Require(Convert.ToInt32(host.Globals.Get(p.Strings[140]))==((flags&1)!=0?1:0),"F1 flag mismatch");
   Require(Convert.ToInt32(host.Globals.Get(p.Strings[150]))==((flags&2)!=0?1:0),"1-key flag mismatch");
   Require(Convert.ToInt32(vm.Evaluate(Lhs(p.Strings[159])) )==((flags&4)!=0?1:0),"Revive flag mismatch");
   int g=Convert.ToInt32(host.Globals.Get(p.Strings[82]));
   if(assertCanonical)Require(g==((flags&8)!=0?1:0),"G enabled flag mismatch for canonical input "+gms+" flags="+flags+" actual="+g);
   int[] skillTargets={959,1054,1136,1231},potionTargets={1538,1326,1379,1432,1485};
   Require(targets.Count==((flags&4)!=0?3:2)&&targets[0]==skillTargets[skill]&&targets[1]==potionTargets[potion],"Reconstructed worker selection mismatch");
   if((flags&4)!=0)Require(targets[2]==1551,"Wrong death monitor selection");
   Require(Convert.ToInt32(host.Globals.Get(p.Strings[171]))==ids[0]&&Convert.ToInt32(host.Globals.Get(p.Strings[208]))==ids[1],"Worker IDs not stored in original globals");
   if((flags&4)!=0)Require(Convert.ToInt32(host.Globals.Get(p.Strings[254]))==ids[2],"Death monitor ID lost");
   object gValue=host.Globals.Get(p.Strings[82]);
   return new{potion=potion,skill=skill,speed=speed,flags=flags,gms=gms,g_value=g,g_variant_type=gValue==null?"Empty":gValue.GetType().Name,
      selected_original_body_entries=targets,worker_ids=ids,steps=steps,idle_entry=vm.Pc};
  }
 }
 [STAThread]public static int Main(){
  string error=null;var cases=new List<object>();var extra=new List<object>();
  try{
   CallbackGuestTest.Guard();MacroProgram p=ProgramReader.Read(Path.Combine(Lab,"10-semantic-main.json"),SemanticMainDigest.Value);
   Require(p.Missing.Count==329,"Original missing records were concealed");
   for(int potion=0;potion<5;potion++)for(int skill=0;skill<4;skill++)for(int speed=0;speed<4;speed++)for(int flags=0;flags<16;flags++)
    cases.Add(Run(p,potion,skill,speed,flags,"5",true));
   foreach(string value in new[]{"0","1","2","3","4","5","6","7","8","9","","abc","01","1.0"})
    for(int g=0;g<2;g++){
     bool expectedError=g==1&&(value==""||value=="abc");
     try{object result=Run(p,0,1,1,g==1?8:0,value,false);Require(!expectedError,"Expected original Sgn type mismatch was suppressed");extra.Add(result);}
     catch(InvalidOperationException ex){if(!expectedError||!ex.Message.Contains("800a000d"))throw;extra.Add(new{gms=value,flags=8,expected_original_type_mismatch=true,error=ex.Message});}
    }
  }catch(Exception ex){error=ex.ToString();}
  if(Environment.MachineName!="DESKTOP-GAR2QIL")return 2;
  var report=new{ok=error==null,error=error,completed_cases=cases.Count,cases=cases,g_text_cases=extra,
    semantic_main_reconstruction_test=true,original_erased_branch_operands_recovered=false,
    original_missing_records_preserved=329,workers_are_recording_stubs=true,
    native_legacy_bootstrap_executed=false,game_input_sent=false,original_native_loaded=false,full_program_restored=false};
  File.WriteAllText(Path.Combine(Lab,"semantic-main10-verification.json"),new JavaScriptSerializer(){MaxJsonLength=16*1024*1024}.Serialize(report),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
