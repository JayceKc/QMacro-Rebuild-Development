using System;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class ProgramReaderSelfTest {
 static string Hash(string path){using(var h=System.Security.Cryptography.SHA256.Create())return BitConverter.ToString(h.ComputeHash(File.ReadAllBytes(path))).Replace("-","").ToLowerInvariant();}
 public static int Main(string[] args){
  if(args.Length!=2)return 2;
  var json=new JavaScriptSerializer(){MaxJsonLength=64*1024*1024};var results=new List<object>();string error=null;
  int records=0,missing=0,conditions=0,workers=0;
  try{
   var manifest=(Dictionary<string,object>)json.DeserializeObject(File.ReadAllText(Path.Combine(args[0],"manifest.json")));
   foreach(object value in (object[])manifest["modules"]){
    var item=(Dictionary<string,object>)value;string file=Path.Combine(args[0],(string)item["file"]);
    var program=ProgramReader.Read(file,(string)item["sha256"]);
    if(program.Code.Length!=Convert.ToInt32(item["records"])||program.Missing.Count!=Convert.ToInt32(item["missing_records"]))throw new Exception("Program counts differ");
    records+=program.Code.Length;missing+=program.Missing.Count;
    foreach(var instruction in program.Code){
     if(instruction.Op==24)workers++;
     if(instruction.Op==4){string text=program.Strings[instruction.Operand];if(!text.StartsWith("Sgn(",StringComparison.OrdinalIgnoreCase)||!text.EndsWith(")"))throw new Exception("Non-Sgn condition needs separate VARIANT handling");conditions++;}
    }
    bool digestRejected=false;try{ProgramReader.Read(file,new string('0',64));}catch(InvalidDataException){digestRejected=true;}
    if(!digestRejected)throw new Exception("Digest mismatch accepted");
    results.Add(new{module=item["module"],records=program.Code.Length,missing=program.Missing.Count,source_digest_verified=true});
   }
   if(results.Count!=8||records!=42426||missing!=3261)throw new Exception("Full scope changed");
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(args[1],json.Serialize(new{ok=error==null,error=error,modules=results,total_records=records,missing_records=missing,
   condition_sites=conditions,worker_start_sites=workers,executable_sha256=Hash(System.Reflection.Assembly.GetExecutingAssembly().Location),runtime_sha256=Hash(typeof(ProgramReader).Assembly.Location),original_script_executed=false,original_native_loaded=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
