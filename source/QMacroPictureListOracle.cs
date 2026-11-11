using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Web.Script.Serialization;
public static class PictureListOracle {
 const string Root=@"C:\Users\Public\Documents\QMacroLab";
 [STAThread]public static int Main(){
  CallbackGuestTest.Guard();string error=null;var samples=new List<object>();bool validated=false;
  try{
   string folder=Path.Combine(Root,"picture-list-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(folder);
   string a=Path.Combine(folder,"target.bmp"),b=Path.Combine(folder,"other.bmp"),missing=Path.Combine(folder,"missing.bmp"),input=Path.Combine(folder,"scene.bmp");
   using(var target=new Bitmap(3,3,PixelFormat.Format24bppRgb))using(var other=new Bitmap(3,3,PixelFormat.Format24bppRgb))using(var scene=new Bitmap(8,8,PixelFormat.Format24bppRgb)){
    using(var g=Graphics.FromImage(target))g.Clear(Color.FromArgb(145,16,10));using(var g=Graphics.FromImage(other))g.Clear(Color.FromArgb(204,221,85));using(var g=Graphics.FromImage(scene))g.Clear(Color.FromArgb(17,34,51));
    for(int y=0;y<3;y++)for(int x=0;x<3;x++)scene.SetPixel(x+3,y+2,target.GetPixel(x,y));target.Save(a,ImageFormat.Bmp);other.Save(b,ImageFormat.Bmp);scene.Save(input,ImageFormat.Bmp);
   }
   using(var dm=GuestNativeDual.Open()){
    dm.SetShowErrorMsg(0);int mode=dm.SetDisplayInput("pic:"+input);validated=mode==1&&dm.GetColor(0,0).ToLowerInvariant()=="112233";if(!validated)throw new Exception("Synthetic picture input failed validation");
    string[][] cases={new[]{a},new[]{a,""},new[]{"",a},new[]{a,"",b},new[]{missing,a},new[]{b,a},new[]{a,missing},new[]{""},new[]{"",""},new[]{missing},new[]{b,"",a}};
    foreach(string[] files in cases){object x=null,y=null;int result=dm.FindPic(0,0,8,8,String.Join("|",files),"000000",1,0,out x,out y);var names=new List<string>();foreach(string path in files)names.Add(Path.GetFileName(path));samples.Add(new{tokens=names,return_value=result,x=x,y=y});}
   }
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(Root,"original-picture-list-oracle.json"),new JavaScriptSerializer().Serialize(new{ok=error==null,error=error,input_validated=validated,samples=samples,vmware_guest_guard=true,com_registration_changed=false,game_input_sent=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
}
