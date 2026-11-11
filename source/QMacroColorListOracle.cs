// Original packed plugin in fixed guest; all pixels supplied by owned BMPs.
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Web.Script.Serialization;
public static class ColorListOracle {
 const string Lab=@"C:\Users\Public\Documents\QMacroLab";
 [STAThread]public static int Main(){
  CallbackGuestTest.Guard();string error=null;var samples=new List<object>();bool validated=true;
  try{
   string directory=Path.Combine(Lab,"color-list-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(directory);
   using(var dm=GuestNativeDual.Open()){
    dm.SetShowErrorMsg(0);
    Color[] firstColors={Color.FromArgb(17,34,51),Color.Black,Color.FromArgb(25,25,25),Color.FromArgb(26,0,0),Color.FromArgb(0,25,0),Color.FromArgb(0,0,26),Color.FromArgb(1,1,1),Color.Black};
    for(int sceneIndex=0;sceneIndex<firstColors.Length;sceneIndex++){
     Color firstColor=firstColors[sceneIndex];bool black=firstColor.R==0&&firstColor.G==0&&firstColor.B==0;
     string path=Path.Combine(directory,"scene-"+sceneIndex+".bmp");var rgb=new List<byte>();
     using(var scene=new Bitmap(4,4,PixelFormat.Format24bppRgb)){
      using(var g=Graphics.FromImage(scene))g.Clear(Color.FromArgb(17,34,51));
      scene.SetPixel(0,0,firstColor);scene.SetPixel(1,2,Color.FromArgb(147,64,57));
      for(int y=0;y<4;y++)for(int x=0;x<4;x++){Color c=scene.GetPixel(x,y);rgb.Add(c.R);rgb.Add(c.G);rgb.Add(c.B);}scene.Save(path,ImageFormat.Bmp);
     }
     int mode=dm.SetDisplayInput("pic:"+path);string first=dm.GetColor(0,0).ToLowerInvariant();
     string expectedFirst=firstColor.R.ToString("x2")+firstColor.G.ToString("x2")+firstColor.B.ToString("x2");
     if(mode!=1||first!=expectedFirst){validated=false;throw new Exception("Owned picture input was not validated");}
     string[] specs={"934039-050505","934039-050505|","|934039-050505","934039-050505||ffffff-000000","ffffff-000000|","|","||","","|ffffff-000000","934039-050505|793430-050505|70322A-050505|9B453A-050505|"};
     if(sceneIndex>=2)specs=new[]{"","000000","934039-050505|","934039-050505|000000"};
     foreach(double similarity in sceneIndex<2?new[]{.9}:new[]{.1,.9,1.0})foreach(string spec in specs){object x=null,y=null;int ret=dm.FindColor(0,0,4,4,spec,similarity,0,out x,out y);
      samples.Add(new{black_first=black,width=4,height=4,rgb_hex=BitConverter.ToString(rgb.ToArray()).Replace("-","").ToLowerInvariant(),
                      rect=new[]{0,0,4,4},color=spec,similarity=similarity,direction=0,return_value=ret,x=x,y=y});}
    }
   }
  }catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(Lab,"original-color-list-oracle.json"),new JavaScriptSerializer().Serialize(new{
   ok=error==null,error=error,validated_synthetic_picture_input=validated&&error==null,cases=samples,original_native_loaded=true,
   native_findcolor_vtable_offset=176,original_script_executed=false,game_input_sent=false,desktop_pixels_used=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));
  return error==null?0:1;
 }
}
