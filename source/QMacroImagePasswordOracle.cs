// Fixed isolated guest only. Tests the previously user-supplied image password.
// No password dictionary, host activation, registration or antivirus changes.
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
using Microsoft.Win32;
public static class ImagePasswordOracle {
 const string Root=@"C:\Users\Public\Documents\QMacroLab";
 const string Plugin="a23fb027db71c668f8bc13399d148c6ed18f8ef242121e58f73a5e4f57eb3bfc";
 const string Input="58792d98ad820ad1d1de1e1dcde4c6144b50694c5854d5029ed9253304bd23f9";
 static string Hash(string path){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(File.ReadAllBytes(path))).Replace("-","").ToLowerInvariant();}
 [STAThread]public static int Main(){
  CallbackGuestTest.Guard();var trials=new List<object>();string error=null;bool converted=false;
  try{
   string dll=Path.Combine(Root,"fz.dll"),input=Path.Combine(Root,"YLDJS1.bmp");
   if(Hash(dll)!=Plugin||Hash(input)!=Input)throw new Exception("Fixed native/input digest mismatch");
   string[] passwords={"","xiaoxun"};
   for(int i=0;i<passwords.Length;i++){
    using(var dm=GuestNativeDual.Open()){
     dm.SetShowErrorMsg(0);
     int pwd=(int)dm.SetPicPwd(passwords[i]);string before=Convert.ToString(dm.GetPicSize(input));int loaded=(int)dm.LoadPic(input);string after=Convert.ToString(dm.GetPicSize(input));
     string output=Path.Combine(Root,"password-image-candidate-"+i+"-"+Guid.NewGuid().ToString("N")+".bmp");int result=(int)dm.ImageToBmp(input,output);
     int display=(int)dm.SetDisplayInput("pic:"+input);string first=Convert.ToString(dm.GetColor(0,0));object image=null;
     bool valid=false;if(File.Exists(output))try{using(var bmp=new Bitmap(output)){valid=bmp.Width>0&&bmp.Height>0;image=new{width=bmp.Width,height=bmp.Height,sha256=Hash(output),file=Path.GetFileName(output)};}}catch(ArgumentException){}
     converted|=valid;trials.Add(new{candidate=i==0?"empty_baseline":"previous_user_candidate",set_password_return=pwd,size_before_load=before,load_return=loaded,size_after_load=after,
      convert_return=result,output_exists=File.Exists(output),valid_bitmap=valid,image=image,display_input_return=display,first_color=first});
     if(Hash(input)!=Input)throw new Exception("Original image was modified");
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(Root,"original-image-password-probe.json"),new JavaScriptSerializer().Serialize(new{ok=error==null,error=error,trials=trials,converted=converted,
   plugin_sha256=Plugin,input_sha256=Input,original_file_modified=false,vmware_guest_guard=true,
   password_dictionary_used=false,com_registration_changed=false,direct_fixed_class_factory=true,typed_dual_interface=true,game_input_sent=false,antivirus_changed=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
