using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Web.Script.Serialization;

namespace QMacroRebuild {
 public static class ProgramReader {
  public static MacroProgram Read(string filename,string expectedSha256){
   byte[] raw=File.ReadAllBytes(filename);
   using(var hash=SHA256.Create()){
    string actual=BitConverter.ToString(hash.ComputeHash(raw)).Replace("-","").ToLowerInvariant();
    if(expectedSha256==null||actual!=expectedSha256)throw new InvalidDataException("Program digest mismatch");
   }
   var serializer=new JavaScriptSerializer(){MaxJsonLength=64*1024*1024};
   var data=(Dictionary<string,object>)serializer.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
   if(Convert.ToInt32(data["schema"])!=1)throw new InvalidDataException("Unknown macro schema");
   var code=(object[])data["code"];var text=(object[])data["strings"];
   var program=new MacroProgram(){Name=(string)data["name"],Code=new Instruction[code.Length],Strings=new string[text.Length]};
   for(int i=0;i<code.Length;i++){
    var row=(object[])code[i];if(row.Length!=4)throw new InvalidDataException("Invalid instruction tuple");
    program.Code[i]=new Instruction(Convert.ToInt32(row[0]),Convert.ToInt32(row[2]),Convert.ToInt32(row[1]),Convert.ToInt32(row[3]));
   }
   for(int i=0;i<text.Length;i++)program.Strings[i]=(string)text[i];
   foreach(object value in (object[])data["missing_records"]){int index=Convert.ToInt32(value);if(index<0||index>=code.Length)throw new InvalidDataException("Missing-record index outside program");program.Missing.Add(index);}
   Validate(program);return program;
  }
  public static void Validate(MacroProgram program){
   var allowed=new HashSet<int>(new[]{2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18,19,20,22,23,24,27,28,29,30,31,32,33,34,35,36,37,38,255});
   var textOps=new HashSet<int>(new[]{2,4,27,28,30,31,37,38});
   for(int i=0;i<program.Code.Length;i++){
    Instruction instruction=program.Code[i];if(!allowed.Contains(instruction.Op))throw new InvalidDataException("Unknown opcode at "+i);
    if(textOps.Contains(instruction.Op)&&(instruction.Operand<0||instruction.Operand>=program.Strings.Length))throw new InvalidDataException("SL index at "+i);
    if(instruction.Op==5||instruction.Op>=6&&instruction.Op<=12||instruction.Op==16||instruction.Op==24){
     long target=instruction.Op==5||instruction.Op==12?instruction.Operand:(long)i+instruction.Operand;
     if(target<0||target>=program.Code.Length)throw new InvalidDataException("Target outside program at "+i);
    }
   }
  }
 }
}
