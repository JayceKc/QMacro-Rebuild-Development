// Owned CPU image matcher. Behavior is limited to recorded dm 7.2450 fixtures.
// No original DLL, desktop capture, input or arbitrary native API is used here.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;

namespace QMacroRebuild {
 public struct VisionPoint {public int X,Y;public VisionPoint(int x,int y){X=x;Y=y;}}
 public struct VisionResult {
  public int ReturnValue,X,Y;
  public VisionResult(int value,int x,int y){ReturnValue=value;X=x;Y=y;}
 }
 public sealed class VisionFrame {
  internal readonly byte[] Data;
  public readonly int Width,Height,OriginX,OriginY;
  public VisionFrame(int width,int height,byte[] rgb,int originX=0,int originY=0){
   if(width<=0||height<=0||(long)width*height>16000000||rgb==null||rgb.LongLength!=(long)width*height*3)throw new ArgumentException("Invalid RGB frame");
   Width=width;Height=height;OriginX=originX;OriginY=originY;Data=(byte[])rgb.Clone();
  }
  internal int Index(int x,int y){long dx=(long)x-OriginX,dy=(long)y-OriginY;if(dx<0||dy<0||dx>=Width||dy>=Height)throw new ArgumentException("Pixel outside frame");return (int)((dy*Width+dx)*3);}
  public void ValidateRect(int x1,int y1,int x2,int y2){
   if(x1>x2||y1>y2||x1<OriginX||y1<OriginY||(long)x2>OriginX+(long)Width||(long)y2>OriginY+(long)Height)throw new ArgumentException("Rectangle outside frame");
  }
  public byte[] CopyRgb(){return (byte[])Data.Clone();}
  public static VisionFrame ReadBmp(string file){return DecodeBmp(File.ReadAllBytes(file));}
  public static VisionFrame DecodeBmp(byte[] bytes){
   if(bytes==null||bytes.Length<54||bytes[0]!='B'||bytes[1]!='M')throw new ArgumentException("Expected ordinary BMP; DMDM is unresolved");
   using(var reader=new BinaryReader(new MemoryStream(bytes,false))){
    reader.BaseStream.Position=2;uint declared=reader.ReadUInt32();reader.BaseStream.Position=10;uint offset=reader.ReadUInt32();
    uint header=reader.ReadUInt32();int width=reader.ReadInt32(),signedHeight=reader.ReadInt32();ushort planes=reader.ReadUInt16(),depth=reader.ReadUInt16();uint compression=reader.ReadUInt32();
    long height=Math.Abs((long)signedHeight);
    if(header<40||planes!=1||depth!=24||compression!=0||width<=0||height==0||(long)width*height>16000000)throw new ArgumentException("Only bounded 24-bit BI_RGB is verified");
    long stride=((long)width*3+3)&~3L;
    if(offset<14L+header||offset+stride*height>bytes.LongLength||declared>bytes.LongLength)throw new ArgumentException("Truncated BMP");
    var rgb=new byte[checked(width*(int)height*3)];
    for(int y=0;y<height;y++){
     long row=signedHeight<0?y:height-1-y;int start=checked((int)(offset+row*stride));
     for(int x=0;x<width;x++){int src=start+x*3,dst=(y*width+x)*3;rgb[dst]=bytes[src+2];rgb[dst+1]=bytes[src+1];rgb[dst+2]=bytes[src];}
    }
    return new VisionFrame(width,(int)height,rgb);
   }
  }
 }
 public static class VisionMatcher {
  struct Pattern {public int R,G,B,DR,DG,DB;}
  struct Sample {public int X,Y,Index;}
  sealed class CenterPoint:IComparable<CenterPoint> {
   public int X,Y;public long Distance;
   public int CompareTo(CenterPoint other){int d=Distance.CompareTo(other.Distance);if(d!=0)return d;d=Y.CompareTo(other.Y);return d!=0?d:X.CompareTo(other.X);}
  }
  static int Hex(string value,int start){return Convert.ToInt32(value.Substring(start,2),16);}
  static int Margin(double similarity,double minimum){if(Double.IsNaN(similarity)||Double.IsInfinity(similarity)||similarity<minimum||similarity>1)throw new ArgumentException("Unverified similarity range");return (int)(255*(1-similarity));}
  static Pattern[] Patterns(string expression,double similarity){
   int margin=Margin(similarity,.1);if(expression==null)throw new ArgumentException("Missing color expression");
   var list=new List<Pattern>();foreach(string rawToken in expression.Split('|')){
    string token=rawToken.Length==0?"000000":rawToken;
    var m=Regex.Match(token,@"\A([0-9a-fA-F]{6})(?:-([0-9a-fA-F]{6}))?\z");if(!m.Success)throw new ArgumentException("Unverified color syntax");
    string rgb=m.Groups[1].Value,delta=m.Groups[2].Success?m.Groups[2].Value:"000000";
    list.Add(new Pattern(){R=Hex(rgb,0),G=Hex(rgb,2),B=Hex(rgb,4),DR=Hex(delta,0)+margin,DG=Hex(delta,2)+margin,DB=Hex(delta,4)+margin});
   }return list.ToArray();
  }
  public static IEnumerable<VisionPoint> Scan(int x1,int y1,int x2,int y2,int direction){
   if(direction<0||direction>8)throw new ArgumentException("Unverified scan direction");
   if(x1>=x2||y1>=y2)yield break;
   if(direction==4){
    int w=checked(x2-x1),h=checked(y2-y1);if((long)w*h>16000000)throw new ArgumentException("Excessive center scan");
    int cx=x1+w/2,cy=y1+h/2;var seen=new bool[checked(w*h)];var queue=new SortedSet<CenterPoint>();
    queue.Add(new CenterPoint(){X=cx,Y=cy});seen[(cy-y1)*w+cx-x1]=true;
    int[] dx={0,-1,1,0},dy={-1,0,0,1};
    while(queue.Count>0){var p=queue.Min;queue.Remove(p);yield return new VisionPoint(p.X,p.Y);
     for(int i=0;i<4;i++){int x=p.X+dx[i],y=p.Y+dy[i];if(x<x1||x>=x2||y<y1||y>=y2)continue;int index=(y-y1)*w+x-x1;if(seen[index])continue;seen[index]=true;long xx=(long)x-cx,yy=(long)y-cy;queue.Add(new CenterPoint(){X=x,Y=y,Distance=xx*xx+yy*yy});}
    }yield break;
   }
   bool forwardX=direction==0||direction==1||direction==5||direction==7,forwardY=direction==0||direction==2||direction==5||direction==6;
   int firstX=forwardX?x1:x2-1,firstY=forwardY?y1:y2-1,sx=forwardX?1:-1,sy=forwardY?1:-1;
   if(direction<=3){for(int y=firstY;y>=y1&&y<y2;y+=sy)for(int x=firstX;x>=x1&&x<x2;x+=sx)yield return new VisionPoint(x,y);}
   else{for(int x=firstX;x>=x1&&x<x2;x+=sx)for(int y=firstY;y>=y1&&y<y2;y+=sy)yield return new VisionPoint(x,y);}
  }
  static void CheckCancel(Func<bool> cancelled){if(cancelled!=null&&cancelled())throw new OperationCanceledException("Vision search cancelled");}
  public static VisionResult FindColor(VisionFrame frame,int x1,int y1,int x2,int y2,string colors,double similarity,int direction,Func<bool> cancelled=null){
   frame.ValidateRect(x1,y1,x2,y2);var patterns=Patterns(colors,similarity);CheckCancel(cancelled);
   foreach(var point in Scan(x1,y1,x2,y2,direction)){
    CheckCancel(cancelled);int i=frame.Index(point.X,point.Y);
    foreach(var p in patterns)if(Math.Abs(frame.Data[i]-p.R)<=p.DR&&Math.Abs(frame.Data[i+1]-p.G)<=p.DG&&Math.Abs(frame.Data[i+2]-p.B)<=p.DB)return new VisionResult(1,point.X,point.Y);
   }return new VisionResult(0,-1,-1);
  }
  static bool EqualPixel(byte[] data,int a,int b){return data[a]==data[b]&&data[a+1]==data[b+1]&&data[a+2]==data[b+2];}
  static Sample[] Samples(VisionFrame template){
   byte[] rgb=template.Data;int w=template.Width,h=template.Height;bool corners=EqualPixel(rgb,0,(w-1)*3)&&EqualPixel(rgb,0,(h-1)*w*3)&&EqualPixel(rgb,0,(w*h-1)*3),different=false;
   if(corners)for(int i=0;i<rgb.Length;i+=3)if(!EqualPixel(rgb,0,i)){different=true;break;}
   bool transparent=corners&&different;var samples=new List<Sample>();
   for(int i=0;i<rgb.Length;i+=3)if(!transparent||!EqualPixel(rgb,0,i))samples.Add(new Sample(){X=i/3%w,Y=i/3/w,Index=i});
   return samples.ToArray();
  }
  public static VisionResult FindPic(VisionFrame frame,int x1,int y1,int x2,int y2,IList<VisionFrame> templates,string delta,double similarity,int direction,Func<bool> cancelled=null){
   if(direction<0||direction>3)throw new ArgumentException("Only FindPic directions 0..3 verified");
   if(delta==null||!Regex.IsMatch(delta,@"\A[0-9a-fA-F]{6}\z"))throw new ArgumentException("Unverified delta expression");
   int margin=Margin(similarity,.6),dr=Hex(delta,0)+margin,dg=Hex(delta,2)+margin,db=Hex(delta,4)+margin;
   frame.ValidateRect(x1,y1,x2,y2);if(templates==null||templates.Count==0)throw new ArgumentException("No picture templates");CheckCancel(cancelled);
   for(int n=0;n<templates.Count;n++){
    // A nonempty filename that cannot be loaded retains its native list index.
    var template=templates[n];if(template==null)continue;
    if(template.Width>(long)x2-x1||template.Height>(long)y2-y1)continue;
    var samples=Samples(template);
    int endX=x2-template.Width+1,endY=y2-template.Height+1;
    foreach(var point in Scan(x1,y1,endX,endY,direction)){
     CheckCancel(cancelled);bool match=true;int checkedPixels=0;
     foreach(var s in samples){if((++checkedPixels&1023)==0)CheckCancel(cancelled);int i=frame.Index(point.X+s.X,point.Y+s.Y),j=s.Index;
      if(Math.Abs(frame.Data[i]-template.Data[j])>dr||Math.Abs(frame.Data[i+1]-template.Data[j+1])>dg||Math.Abs(frame.Data[i+2]-template.Data[j+2])>db){match=false;break;}
     }if(match)return new VisionResult(n,point.X,point.Y);
    }
   }return new VisionResult(-1,-1,-1);
  }
 }
 [ComVisible(true),ClassInterface(ClassInterfaceType.AutoDual)]
 public sealed class OwnedVisionLibrary {
  readonly Func<int,int,int,int,VisionFrame> capture;
  readonly Func<string,VisionFrame> resolveTemplate;
  readonly Func<bool> cancelled;
  public OwnedVisionLibrary(Func<int,int,int,int,VisionFrame> capturedFrame,Func<string,VisionFrame> templateResolver,Func<bool> cancellation=null){
   if(capturedFrame==null||templateResolver==null)throw new ArgumentNullException();capture=capturedFrame;resolveTemplate=templateResolver;cancelled=cancellation;
  }
  public int FindColor(int x1,int y1,int x2,int y2,string color,double similarity,int direction,out object x,out object y){
   x=-1;y=-1;var result=VisionMatcher.FindColor(capture(x1,y1,x2,y2),x1,y1,x2,y2,color,similarity,direction,cancelled);x=result.X;y=result.Y;return result.ReturnValue;
  }
  public int FindPic(int x1,int y1,int x2,int y2,string files,string delta,double similarity,int direction,out object x,out object y){
   x=-1;y=-1;if(files==null)throw new ArgumentNullException("files");var templates=new List<VisionFrame>();
   foreach(string file in files.Split(new[]{'|'},StringSplitOptions.RemoveEmptyEntries)){
    try{templates.Add(resolveTemplate(file));}
    catch(FileNotFoundException){templates.Add(null);}
    catch(DirectoryNotFoundException){templates.Add(null);}
   }
   if(templates.Count==0)return -1;
   var result=VisionMatcher.FindPic(capture(x1,y1,x2,y2),x1,y1,x2,y2,templates,delta,similarity,direction,cancelled);x=result.X;y=result.Y;return result.ReturnValue;
  }
 }
}
