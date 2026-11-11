using System;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;
using QMacroRebuild;
public static class Settings10SelfTest {
 static void Require(bool value,string message){if(!value)throw new Exception(message);}
 static Dictionary<string,object> Input(int potion,int skill,int speed,int flags,string text){
  return new Dictionary<string,object>{{"Form1.ComboBox1.ListIndex",potion},{"Form1.ComboBox2.ListIndex",skill},{"Form1.ComboBox3.ListIndex",speed},
   {"Form1.CheckBox1.Value",(flags&1)!=0?1:0},{"Form1.CheckBox2.Value",(flags&2)!=0?1:0},
   {"Form1.CheckBox3.Value",(flags&4)!=0?1:0},{"Form1.CheckBox4.Value",(flags&8)!=0?1:0},{"Form1.InputBox1.Text",text}};
 }
 public static int Main(string[] args){
  if(args.Length!=2)return 2;var json=new JavaScriptSerializer(){MaxJsonLength=16*1024*1024};int cases=0;string error=null;
  try{
   var fixture=(Dictionary<string,object>)json.DeserializeObject(File.ReadAllText(args[0]));Require((bool)fixture["ok"],"Guest reconstruction test failed");
   foreach(object value in (object[])fixture["cases"]){
    var c=(Dictionary<string,object>)value;var settings=Settings10.Resolve(Input(Convert.ToInt32(c["potion"]),Convert.ToInt32(c["skill"]),Convert.ToInt32(c["speed"]),Convert.ToInt32(c["flags"]),(string)c["gms"]));
    Require(settings.Flags==Convert.ToInt32(c["flags"])&&settings.PressG==(Convert.ToInt32(c["g_value"])==1),"Settings flags differ from retained-source replay");
    var targets=(object[])c["selected_original_body_entries"];
    Require(settings.SkillEntry==Convert.ToInt32(targets[0])&&settings.PotionEntry==Convert.ToInt32(targets[1]),"Selected bodies differ");
    Require(settings.DeathEntry==(targets.Length==3?Convert.ToInt32(targets[2]):0),"Death selection differs");cases++;
   }
   Require(cases==1280,"Configuration coverage narrowed");
   foreach(string input in new[]{"","abc","0","10","1.0"}){
    bool rejected=false;try{Settings10.Resolve(Input(0,1,1,8,input));}catch(ArgumentException){rejected=true;}Require(rejected,"Unsupported G input accepted: "+input);
    Settings10.Resolve(Input(0,1,1,0,input));
   }
   Require(Settings10.ApplyInputChange("123")=="3"&&Settings10.ApplyInputChange("45")=="5"&&Settings10.ApplyInputChange("")=="","Input change reconstruction differs");
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(args[1],json.Serialize(new{ok=error==null,error=error,matched_guest_configuration_cases=cases,
   additional_policy="When G is checked the new UI validates one ASCII digit 1..9; it rejects invalid inputs before the original type-error path.",
   original_script_executed=false,original_native_loaded=false,game_input_sent=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
