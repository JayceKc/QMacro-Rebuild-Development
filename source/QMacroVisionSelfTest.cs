// Saved native observations are input data, never executable code.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
using QMacroRebuild;

public static class VisionSelfTest {
 static void Require(bool value,string message){if(!value)throw new Exception(message);}
 static int Int(object value){return Convert.ToInt32(value);}
 static string Hash(byte[] data){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(data)).Replace("-","").ToLowerInvariant();}
 static byte[] Hex(string hex){Require(hex.Length%2==0,"Odd hex string");var data=new byte[hex.Length/2];for(int i=0;i<data.Length;i++)data[i]=Convert.ToByte(hex.Substring(i*2,2),16);return data;}
 static VisionFrame Frame(object value){var obj=(Dictionary<string,object>)value;var origin=(object[])obj["origin"];return new VisionFrame(Int(obj["width"]),Int(obj["height"]),Hex((string)obj["rgb_hex"]),Int(origin[0]),Int(origin[1]));}
 static void Reject(Action operation,string message){bool rejected=false;try{operation();}catch(ArgumentException){rejected=true;}Require(rejected,message);}
 static void GeneralChecks(){
  for(int w=1;w<=12;w++)for(int h=1;h<=12;h++){
   int cx=w/2,cy=h/2;var points=new List<VisionPoint>();for(int y=0;y<h;y++)for(int x=0;x<w;x++)points.Add(new VisionPoint(x,y));
   var sorted=points.OrderBy(p=>(p.X-cx)*(p.X-cx)+(p.Y-cy)*(p.Y-cy)).ThenBy(p=>p.Y).ThenBy(p=>p.X).ToArray();
   var actual=VisionMatcher.Scan(0,0,w,h,4).ToArray();Require(actual.Length==sorted.Length,"Center scan omitted pixel");
   for(int i=0;i<actual.Length;i++)Require(actual[i].X==sorted[i].X&&actual[i].Y==sorted[i].Y,"Center rectangle tie/order mismatch");
  }
  var black=new VisionFrame(1,1,new byte[3]);
  Require(GdiFrameSampler.VerifyOffscreenPixelConversion(),"GDI BGRA/topdown/origin conversion changed");
  var deniedCapture=new GdiFrameSampler(window=>false);bool captureDenied=false;
  try{deniedCapture.Capture(652,959,656,972);}catch(CaptureUnavailableException){captureDenied=true;}Require(captureDenied,"Unverified foreground was captured");
  captureDenied=false;try{deniedCapture.Capture(652,959,3000,972);}catch(CaptureUnavailableException){captureDenied=true;}Require(captureDenied,"Invalid original geometry was captured");
  foreach(string invalid in new[]{null,"@FFFFFF","missing-key","FFFFFF-000000|nothex"})Reject(()=>VisionMatcher.FindColor(black,0,0,1,1,invalid,.9,0),"Invalid syntax accepted");
  Reject(()=>VisionMatcher.FindColor(black,0,0,2,2,"000000",1,0),"Capture outside accepted");
  Reject(()=>VisionMatcher.FindColor(black,0,0,1,1,"000000",1,9),"Direction outside accepted");
  Reject(()=>VisionMatcher.FindPic(black,0,0,1,1,new[]{black},"000000",1,4),"Unmeasured picture direction accepted");
  bool stopped=false;try{VisionMatcher.FindPic(black,0,0,1,1,new[]{black},"000000",1,0,()=>true);}catch(OperationCanceledException){stopped=true;}Require(stopped,"Picture cancellation ignored");
  stopped=false;try{VisionMatcher.FindColor(black,0,0,1,1,"000000",1,0,()=>true);}catch(OperationCanceledException){stopped=true;}Require(stopped,"Color cancellation ignored");
  // Independent BMP rows and padding: red/green top, blue/white bottom.
  byte[] expected={255,0,0,0,255,0,0,0,255,255,255,255};
  foreach(int height in new[]{2,-2}){
   using(var buffer=new MemoryStream())using(var writer=new BinaryWriter(buffer)){
    writer.Write((byte)'B');writer.Write((byte)'M');writer.Write(70);writer.Write(0);writer.Write(54);writer.Write(40);writer.Write(2);writer.Write(height);writer.Write((ushort)1);writer.Write((ushort)24);writer.Write(0);writer.Write(16);writer.Write(new byte[16]);
    byte[] top={0,0,255,0,255,0,99,99},bottom={255,0,0,255,255,255,88,88};writer.Write(height>0?bottom:top);writer.Write(height>0?top:bottom);
    Require(VisionFrame.DecodeBmp(buffer.ToArray()).CopyRgb().SequenceEqual(expected),"BMP row/channel/padding changed");
   }
  }
  var library=new OwnedVisionLibrary((a,b,c,d)=>black,name=>black);
  using(var engine=new VbsEngine()){
   engine.AddItem("OwnedVision",library);engine.Execute("Dim x,y,r:Set DM=OwnedVision:r=DM.FindColor(0,0,1,1,\"000000\",1,0,x,y):If r<>1 Or x<>0 Or y<>0 Then Err.Raise 5",1);
   engine.Execute("x=999:y=999:r=DM.FindPic(0,0,1,1,\"fixture.bmp\",\"000000\",1,0,x,y):If r<>0 Or x<>0 Or y<>0 Then Err.Raise 5",2);
   engine.Execute("x=999:y=999:r=DM.FindColor(0,0,1,1,\"FFFFFF\",1,0,x,y):If r<>0 Or x<>-1 Or y<>-1 Then Err.Raise 5",3);
  }
  var unavailable=new OwnedVisionLibrary((a,b,c,d)=>{throw new InvalidOperationException("Fixture capture unavailable");},name=>black);
  object ox=999,oy=999;bool failed=false;try{unavailable.FindColor(0,0,1,1,"000000",1,0,out ox,out oy);}catch(InvalidOperationException){failed=true;}
  Require(failed&&Int(ox)==-1&&Int(oy)==-1,"Capture error became successful not-found or stale coordinates");
 }
 static void PictureListChecks(string root){
  byte[] pixels=new byte[8*8*3];for(int i=0;i<pixels.Length;i+=3){pixels[i]=17;pixels[i+1]=34;pixels[i+2]=51;}
  for(int y=2;y<5;y++)for(int x=3;x<6;x++){int i=(y*8+x)*3;pixels[i]=145;pixels[i+1]=16;pixels[i+2]=10;}
  byte[] red=new byte[27],green=new byte[27];for(int i=0;i<27;i+=3){red[i]=145;red[i+1]=16;red[i+2]=10;green[i]=204;green[i+1]=221;green[i+2]=85;}
  var scene=new VisionFrame(8,8,pixels);var target=new VisionFrame(3,3,red);var other=new VisionFrame(3,3,green);
  var dm=new OwnedVisionLibrary((a,b,c,d)=>scene,name=>{if(name=="target.bmp")return target;if(name=="other.bmp")return other;throw new FileNotFoundException("Owned missing-template fixture",name);});
  var json=new JavaScriptSerializer();var data=(Dictionary<string,object>)json.DeserializeObject(File.ReadAllText(Path.Combine(root,"verification","fixtures","original-picture-list-oracle.json")));
  Require((bool)data["ok"]&&(bool)data["input_validated"],"Invalid native filename-list fixture");var samples=(object[])data["samples"];Require(samples.Length==11,"Filename-list coverage changed");
  foreach(object item in samples){var sample=(Dictionary<string,object>)item;string files=String.Join("|",((object[])sample["tokens"]).Select(t=>(string)t).ToArray());object x=null,y=null;int ret=dm.FindPic(0,0,8,8,files,"000000",1,0,out x,out y);Require(ret==Int(sample["return_value"])&&Int(x)==Int(sample["x"])&&Int(y)==Int(sample["y"]),"Native filename-list behavior differs: "+files);}
  var invalid=new OwnedVisionLibrary((a,b,c,d)=>scene,name=>{throw new InvalidDataException("Unresolved image format fixture");});
  object ox=null,oy=null;bool rejected=false;try{invalid.FindPic(0,0,8,8,"unreadable.bmp","000000",1,0,out ox,out oy);}catch(InvalidDataException){rejected=true;}Require(rejected,"Unsupported image was silently treated as an absent file");
 }
 static void ColorListChecks(string root){
  var data=(Dictionary<string,object>)new JavaScriptSerializer().DeserializeObject(File.ReadAllText(Path.Combine(root,"verification","fixtures","original-color-list-oracle.json")));
  Require((bool)data["ok"]&&(bool)data["validated_synthetic_picture_input"],"Invalid native color-list fixture");
  var rows=(object[])data["cases"];Require(rows.Length==92,"Native color-list coverage changed");
  foreach(object item in rows){
   var row=(Dictionary<string,object>)item;var rect=(object[])row["rect"];
   var frame=new VisionFrame(Int(row["width"]),Int(row["height"]),Hex((string)row["rgb_hex"]));
   var result=VisionMatcher.FindColor(frame,Int(rect[0]),Int(rect[1]),Int(rect[2]),Int(rect[3]),(string)row["color"],Convert.ToDouble(row["similarity"]),Int(row["direction"]));
   Require(result.ReturnValue==Int(row["return_value"])&&result.X==Int(row["x"])&&result.Y==Int(row["y"]),"Native empty color token differs: "+row["color"]);
  }
 }
 static void AssetIndexChecks(string root){
  var data=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=32*1024*1024}.DeserializeObject(File.ReadAllText(Path.Combine(root,"data","asset-catalog.json")));
  Require(((object[])data["images"]).Length==3048,"Full image container inventory changed");
  var unique=new HashSet<string>();var containers=new Dictionary<string,OriginalAssetResolver>();int ordinary=0,encrypted=0;
  foreach(object item in (object[])data["images"]){var row=(Dictionary<string,object>)item;if(!unique.Add((string)row["sha256"]))continue;
   string container=(string)row["container"];OriginalAssetResolver resolver;if(!containers.TryGetValue(container,out resolver)){resolver=new OriginalAssetResolver(root,container);containers.Add(container,resolver);}
   byte[] bytes=File.ReadAllBytes(resolver.ResolveFile((string)row["filename"]));
   if((string)row["kind"]=="ordinary_bmp"){var frame=VisionFrame.DecodeBmp(bytes);Require(frame.CopyRgb().Length==frame.Width*frame.Height*3,"Unique asset size mismatch");ordinary++;}
   else{Require((string)row["kind"]=="proprietary_dmdm","Unknown attachment image format");Reject(()=>VisionFrame.DecodeBmp(bytes),"Protected unique image accepted as ordinary BMP");encrypted++;}
  }Require(unique.Count==378&&ordinary==377&&encrypted==1,"Unique image coverage changed");
  var baseline=new OriginalAssetResolver(root,"account/01");var alias=new OriginalAssetResolver(root,"account/02");Require(alias.CanonicalContainer=="account/01"&&alias.ImageCount==380&&baseline.ImageCount==380,"Canonical script/image association changed");
  var conflicts=(object[])data["name_conflicts"];Require(conflicts.Length==1,"Image conflict coverage changed");var conflict=(Dictionary<string,object>)conflicts[0];Require((string)conflict["name"]=="ta.bmp","Unknown image conflict needs review");
  var seen=new HashSet<string>();foreach(object item in (object[])conflict["occurrences"]){var row=(Dictionary<string,object>)item;string digest=(string)row["sha256"];if(!seen.Add(digest))continue;
   var resolver=new OriginalAssetResolver(root,(string)row["container"]);string file=resolver.ResolveFile(@"C:\users\mymacro\ta.bmp");Require(Hash(File.ReadAllBytes(file))==digest,"Same-name distinct image was overwritten");resolver.ResolveImage("ta.bmp");
  }Require(seen.Count==2,"Distinct image versions were merged");
  Reject(()=>baseline.ResolveFile(@"C:\Windows\ta.bmp"),"Image escaped mapped original root");
  bool missing=false;try{baseline.ResolveFile("not-a-restored-image.bmp");}catch(FileNotFoundException){missing=true;}Require(missing,"Unknown original image resolved silently");
  Reject(()=>baseline.ResolveImage("YLDJS1.bmp"),"Encrypted asset was incorrectly treated as restored pixels");
 }
 [STAThread]public static int Main(string[] args){
  if(args.Length!=2)return 2;string root=Path.GetFullPath(args[0]),error=null;int colors=0,pictures=0,bmp=0,proprietary=0;var matched=new List<object>();string fixtureHash=null;bool checksCompleted=false;
  try{
   string file=Path.Combine(root,"verification","vision-replay-cases.json");byte[] raw=File.ReadAllBytes(file);fixtureHash=Hash(raw);
   var document=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=16*1024*1024}.DeserializeObject(System.Text.Encoding.UTF8.GetString(raw));
   foreach(var source in (Dictionary<string,object>)document["source_sha256"])Require(Hash(File.ReadAllBytes(Path.Combine(root,"verification","fixtures",source.Key)))==(string)source.Value,"Native evidence file digest changed: "+source.Key);
   foreach(object value in (object[])document["cases"]){
    var row=(Dictionary<string,object>)value;VisionFrame scene=Frame(row["scene"]);var rect=(object[])row["rect"];VisionResult result;
    if((string)row["kind"]=="color"){result=VisionMatcher.FindColor(scene,Int(rect[0]),Int(rect[1]),Int(rect[2]),Int(rect[3]),(string)row["color"],Convert.ToDouble(row["similarity"]),Int(row["direction"]));colors++;}
    else{var templates=new List<VisionFrame>();foreach(object t in (object[])row["templates"])templates.Add(Frame(t));result=VisionMatcher.FindPic(scene,Int(rect[0]),Int(rect[1]),Int(rect[2]),Int(rect[3]),templates,(string)row["delta"],Convert.ToDouble(row["similarity"]),Int(row["direction"]));pictures++;}
    var expected=(object[])row["expected"];Require(result.ReturnValue==Int(expected[0])&&result.X==Int(expected[1])&&result.Y==Int(expected[2]),"Observation mismatch: "+row["source"]+" / "+row["sample_index"]+" actual="+result.ReturnValue+","+result.X+","+result.Y);
    matched.Add(new{source=row["source"],sample_index=row["sample_index"],result=new[]{result.ReturnValue,result.X,result.Y}});
   }
   Require(colors==416&&pictures==141,"Native observation coverage changed");GeneralChecks();PictureListChecks(root);ColorListChecks(root);AssetIndexChecks(root);checksCompleted=true;
   foreach(string path in Directory.GetFiles(Path.Combine(root,"assets","account-01","attachments"),"*.bmp")){
    byte[] rawBmp=File.ReadAllBytes(path);if(rawBmp.Length>=4&&System.Text.Encoding.ASCII.GetString(rawBmp,0,4)=="DMDM"){Reject(()=>VisionFrame.DecodeBmp(rawBmp),"DMDM incorrectly decoded");proprietary++;}
    else{var frame=VisionFrame.DecodeBmp(rawBmp);Require(frame.CopyRgb().Length==frame.Width*frame.Height*3,"BMP size mismatch");bmp++;}
   }Require(bmp==379&&proprietary==1,"Original asset inventory changed");
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(args[1],new JavaScriptSerializer(){MaxJsonLength=16*1024*1024}.Serialize(new{
   ok=error==null,error=error,color_observations=colors,picture_observations=pictures,picture_distinct_conditions=77,
   ordinary_bmp_decoded=bmp,proprietary_bmp_rejected=proprietary,fixture_sha256=fixtureHash,matched=matched,
   executable_sha256=Hash(File.ReadAllBytes(System.Reflection.Assembly.GetExecutingAssembly().Location)),
   owned_vbs_coordinate_bridge_verified=checksCompleted,owned_offscreen_gdi_conversion_verified=checksCompleted,
   picture_filename_list_observations=checksCompleted?11:0,picture_filename_list_fixture_sha256=File.Exists(Path.Combine(root,"verification","fixtures","original-picture-list-oracle.json"))?Hash(File.ReadAllBytes(Path.Combine(root,"verification","fixtures","original-picture-list-oracle.json"))):null,
   color_list_observations=checksCompleted?92:0,color_list_fixture_sha256=File.Exists(Path.Combine(root,"verification","fixtures","original-color-list-oracle.json"))?Hash(File.ReadAllBytes(Path.Combine(root,"verification","fixtures","original-color-list-oracle.json"))):null,
   invalid_foreground_rejected=checksCompleted,capture_error_propagation_verified=checksCompleted,
   module_asset_conflicts_and_aliases_verified=checksCompleted,
   unique_asset_image_contents_verified=checksCompleted?378:0,unique_ordinary_images_decoded=checksCompleted?377:0,unique_proprietary_images_unresolved=1,
   original_native_loaded=false,original_script_executed=false,game_input_sent=false,live_capture_verified=false,
   realtime_performance_verified=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
