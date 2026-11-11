// Data-only native CPU observations plus owned VBScript/COM bridge fixtures.
using System;
using System.IO;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using System.Security.Cryptography;
using QMacroRebuild;

public static class BuiltinSelfTest {
 static int I(object x){return Convert.ToInt32(x);}
 static void Check(bool ok,string message){if(!ok)throw new Exception(message);}
 static string Hash(byte[] data){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(data)).Replace("-","").ToLowerInvariant();}
 static VisionFrame Frame(object size,object pixels,int x=0,int y=0){
  var dimensions=(object[])size;var colors=(object[])pixels;var rgb=new byte[colors.Length*3];
  for(int i=0;i<colors.Length;i++)for(int ch=0;ch<3;ch++)rgb[i*3+ch]=Convert.ToByte(((string)colors[i]).Substring(ch*2,2),16);
  return new VisionFrame(I(dimensions[0]),I(dimensions[1]),rgb,x,y);
 }
 static void Bridge(){
  var p=new MacroProgram(){Name="owned builtin fixture",Strings=new string[0],Code=new[]{new Instruction(255)}};
  using(var host=new DryRunHost(s=>false))using(var vm=new RecordVm(p,host.Globals,host,0)){
   host.BuiltinProvider=(ctx,name,args)=>{
    if(name=="builtin_cursor"){Check(args.Length==0,"Cursor arguments");return 3*8192+4096;}
    if(name=="builtin_color"){
     Check(args.Length==7&&I(args[0])==1&&I(args[3])==4&&(string)args[4]=="40752b"&&I(args[5])==0,"Color argument forwarding");
     return BuiltinColor.FindColor(new VisionFrame(1,1,new byte[]{0,0,0}),0,0,0,0,"ffffff",0,1);
    }
    if(name=="builtin_picture"){
     Check(args.Length==6&&(string)args[4]=="owned.bmp"&&Convert.ToDouble(args[5])==.5,"Picture argument forwarding");
     return BuiltinPicture.FindPic(new VisionFrame(3,3,new byte[27],1,2),new VisionFrame(1,1,new byte[]{255,255,255}),I(args[0]),I(args[1]),I(args[2]),I(args[3]),Convert.ToDouble(args[5]));
    }
    throw new Exception("Unknown builtin");
   };
   vm.ExecuteOwnedSetup("Dim x,y,r:r=GetCursorPos(x,y):If Not IsEmpty(r) Then Err.Raise 5\nIf x<>4 Or y<>4096 Then Err.Raise 5");
   vm.ExecuteOwnedSetup("r=FindColorEx(1,2,3,4,\"40752b\",0,0.9,x,y):If r<>-8193 Or x<>-1 Or y<>-1 Then Err.Raise 5");
   vm.ExecuteOwnedSetup("r=FindPic(1,2,3,4,\"owned.bmp\",0.5,x,y):If r<>8194 Or x<>1 Or y<>2 Then Err.Raise 5");
   host.BuiltinProvider=null;bool rejected=false;
   try{vm.Evaluate("GetCursorPos(x,y)");}catch(InvalidOperationException){rejected=true;}
   Check(rejected,"Missing provider fabricated cursor");
   host.BuiltinProvider=(ctx,name,args)=>null;rejected=false;
   try{vm.Evaluate("GetCursorPos(x,y)");}catch(InvalidOperationException){rejected=true;}
   Check(rejected,"Null packed value coerced to zero");
   host.BuiltinProvider=(ctx,name,args)=>{throw new IOException("Owned capture failure");};rejected=false;
   try{vm.Evaluate("FindColorEx(1,2,3,4,\"40752b\",0,0.9,x,y)");}catch(InvalidOperationException){rejected=true;}
   Check(rejected,"Capture failure became not found");
  }
 }
 static void ServiceChecks(){
  int captures=0,resolves=0;
  var service=new BuiltinVisionService((l,t,r,b)=>{
   Check(l==1&&t==2&&r==4&&b==5,"Inclusive builtin ROI was not converted to exclusive capture");captures++;
   var rgb=new byte[27];rgb[24]=43;rgb[25]=117;rgb[26]=64;return new VisionFrame(3,3,rgb,1,2);
  },name=>{
   resolves++;if(name!="owned.bmp")throw new FileNotFoundException("Owned missing asset");
   return new VisionFrame(1,1,new byte[]{255,255,255});
  },()=>new VisionPoint(100,200));
  var p=new MacroProgram(){Name="owned builtin service",Strings=new string[0],Code=new[]{new Instruction(255)}};
  using(var host=new DryRunHost(s=>false))using(var vm=new RecordVm(p,host.Globals,host,0)){
   host.BuiltinProvider=(ctx,name,args)=>service.Invoke(name,args);
   vm.ExecuteOwnedSetup("Dim x,y,r:r=FindColorEx(1,2,3,4,\"40752b\",0,0.9,x,y):If x<>3 Or y<>4 Or r<>24580 Then Err.Raise 5");
   vm.ExecuteOwnedSetup("r=FindPic(1,2,3,4,\"owned.bmp\",0.5,x,y):If x<>1 Or y<>2 Or r<>8194 Then Err.Raise 5");
   vm.ExecuteOwnedSetup("r=GetCursorPos(x,y):If x<>100 Or y<>200 Or Not IsEmpty(r) Then Err.Raise 5");
  }
  Check(captures==2&&resolves==1,"Builtin read-only service routing changed");
  bool rejected=false;
  try{service.Invoke("builtin_picture",new object[]{1,2,3,4,"missing.bmp",.9});}catch(FileNotFoundException){rejected=true;}
  Check(rejected&&captures==2,"Missing asset was captured/masked as absence");
  var unavailable=new BuiltinVisionService((l,t,r,b)=>{throw new IOException("Owned capture failed");},name=>new VisionFrame(1,1,new byte[3]));
  rejected=false;try{unavailable.Invoke("builtin_cursor",new object[0]);}catch(NotSupportedException){rejected=true;}
  Check(rejected,"No cursor provider fabricated position zero");
  rejected=false;try{unavailable.Invoke("builtin_color",new object[]{1,2,3,4,"40752b",0,.9});}catch(IOException){rejected=true;}
  Check(rejected,"Capture failure became builtin miss");
  rejected=false;try{BuiltinColor.FindColor(new VisionFrame(1,1,new byte[3]),0,0,0,0,"000000",0,1,()=>true);}catch(OperationCanceledException){rejected=true;}
  Check(rejected,"Builtin color cancellation ignored");
 }
 [STAThread]public static int Main(string[] args){
  if(args.Length!=2)return 2;string error=null,sha=null,pictureSha=null,bitmapSha=null;int cases=0,orders=0,pictures=0,bitmaps=0;bool bridge=false;
  try{
   byte[] raw=File.ReadAllBytes(Path.Combine(args[0],"verification","builtin-color-contract.json"));sha=Hash(raw);
   var doc=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=8000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
   foreach(object value in (object[])doc["owned_replay_cases"]){
    var c=(Dictionary<string,object>)value;var pixels=(object[])c["pixels_rgb"];var origin=(object[])c["origin"];var rgb=new byte[pixels.Length*3];
    for(int i=0;i<pixels.Length;i++)for(int ch=0;ch<3;ch++)rgb[i*3+ch]=Convert.ToByte(((string)pixels[i]).Substring(ch*2,2),16);
    int w=I(c["width"]),h=I(c["height"]),x=I(origin[0]),y=I(origin[1]);
    int result=BuiltinColor.FindColor(new VisionFrame(w,h,rgb,x,y),x,y,x+w-1,y+h-1,(string)c["target_bgr"],I(c["scan_type"]),Convert.ToDouble(c["similarity"]));
    Check(result==I(c["packed"]),"Native builtin pixel mismatch "+cases);cases++;
   }
   foreach(object value in (object[])doc["center_removal_cases"]){
    var c=(Dictionary<string,object>)value;var origin=(object[])c["origin"];var expected=(object[])c["order"];int x=I(origin[0]),y=I(origin[1]),index=0;
    foreach(var point in BuiltinColor.Points(x,y,x+I(c["width"])-1,y+I(c["height"])-1,1)){
     var pair=(object[])expected[index++];Check(point.X==I(pair[0])&&point.Y==I(pair[1]),"Builtin center shell order mismatch");
    }Check(index==expected.Length,"Builtin center coverage");orders++;
   }
   Check(cases==80&&orders==9,"Builtin fixture inventory");
   raw=File.ReadAllBytes(Path.Combine(args[0],"verification","builtin-picture-observations.json"));pictureSha=Hash(raw);
   doc=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=8000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
   foreach(object value in (object[])doc["cases"]){
    var c=(Dictionary<string,object>)value;var origin=(object[])c["origin"];int x=I(origin[0]),y=I(origin[1]);
    var frame=Frame(c["frame_size"],c["frame_rgb"],x,y);var template=Frame(c["template_size"],c["template_rgb"]);
    int key=I(c["explicit_transparency"]);var expected=(object[])c["found_xy"];
    var result=BuiltinPicture.FindPicture(frame,template,x,y,x+frame.Width-1,y+frame.Height-1,Convert.ToDouble(c["similarity"]),key==-1?(int?)null:key);
    Check(result.X==I(expected[0])&&result.Y==I(expected[1]),"Builtin picture mismatch: "+c["label"]);pictures++;
   }
   Check(pictures==220,"Builtin picture fixture inventory");
   var black=new VisionFrame(3,3,new byte[27]);var dot=new VisionFrame(1,1,new byte[3]);bool cancelled=false;
   try{BuiltinPicture.FindPicture(black,dot,0,0,2,2,1,null,()=>true);}catch(OperationCanceledException){cancelled=true;}
   Check(cancelled,"Builtin picture cancellation ignored");
   bool rejected=false;try{BuiltinPicture.FindPicture(black,dot,0,0,3,3,1);}catch(ArgumentException){rejected=true;}
   Check(rejected,"Builtin picture out of capture accepted");
   raw=File.ReadAllBytes(Path.Combine(args[0],"verification","builtin-bitmap-conversion.json"));bitmapSha=Hash(raw);
   doc=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=8000000}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
   foreach(object value in (object[])doc["cases"]){
    var c=(Dictionary<string,object>)value;byte[] bmp;
    if((string)c["kind"]=="recovered_asset"){
     bmp=File.ReadAllBytes(Path.Combine(args[0],(string)c["bundle_path"]));Check(Hash(bmp)==(string)c["bmp_sha256"],"Asset BMP changed");
    }else{
     string hex=(string)c["bmp_hex"];bmp=new byte[hex.Length/2];for(int i=0;i<bmp.Length;i++)bmp[i]=Convert.ToByte(hex.Substring(i*2,2),16);
    }
    Check(Hash(VisionFrame.DecodeBmp(bmp).CopyRgb())==(string)c["native_rgb_sha256"],"Native row/conversion mismatch");bitmaps++;
   }
   Check(bitmaps==387,"Native bitmap conversion inventory");
   Bridge();ServiceChecks();bridge=true;
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(args[1],new JavaScriptSerializer().Serialize(new{ok=error==null,error=error,native_pixel_cases=cases,native_center_orders=orders,
   owned_vbs_bridge_verified=bridge,fixture_sha256=sha,original_native_loaded=false,original_script_executed=false,
   native_picture_pixel_cases=pictures,picture_fixture_sha256=pictureSha,builtin_picture_pixel_port_implemented=true,
   native_bitmap_conversion_cases=bitmaps,bitmap_fixture_sha256=bitmapSha,
   owned_readonly_builtin_service_verified=bridge,
   executable_sha256=Hash(File.ReadAllBytes(System.Reflection.Assembly.GetExecutingAssembly().Location)),
   game_input_sent=false,live_capture_verified=false,full_builtin_findpic_api_verified=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
