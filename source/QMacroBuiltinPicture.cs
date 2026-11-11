// Owned Runner builtin pixel matcher. Supplied RGB rows only; not dm.FindPic.
// Original filename, conversion and screen capture behavior are separate work.
using System;

namespace QMacroRebuild {
 public static class BuiltinPicture {
  static int Rgb(VisionFrame frame,int x,int y){int i=frame.Index(x,y);return frame.Data[i]<<16|frame.Data[i+1]<<8|frame.Data[i+2];}
  static int Difference(int a,int b){return Math.Abs((a>>16&255)-(b>>16&255))+Math.Abs((a>>8&255)-(b>>8&255))+Math.Abs((a&255)-(b&255));}
  public static VisionPoint FindPicture(VisionFrame frame,VisionFrame template,int left,int top,int right,int bottom,double similarity,int? transparentRgb=null,Func<bool> cancelled=null){
   if(frame==null||template==null)throw new ArgumentNullException("frame/template");
   if(Double.IsNaN(similarity)||Double.IsInfinity(similarity)||similarity<.1||similarity>1)throw new ArgumentException("Unverified builtin picture similarity");
   if(left>right||top>bottom||left<frame.OriginX||top<frame.OriginY||(long)right>=frame.OriginX+(long)frame.Width||(long)bottom>=frame.OriginY+(long)frame.Height)throw new ArgumentException("Inclusive rectangle outside frame");
   if(transparentRgb.HasValue&&(transparentRgb.Value<0||transparentRgb.Value>0xffffff))throw new ArgumentException("Expected RGB transparency");
   int tx=template.OriginX,ty=template.OriginY,w=template.Width,h=template.Height;
   // The native default makes a uniform image transparent too.
   if(!transparentRgb.HasValue){
    int corner=Rgb(template,tx,ty);
    if(Rgb(template,tx+w-1,ty)==corner&&Rgb(template,tx,ty+h-1)==corner&&Rgb(template,tx+w-1,ty+h-1)==corner)transparentRgb=corner;
   }
   int allowance=(int)((long)w*h*(1-(double)(float)similarity));
   int[,] stages={{0,0,4,4,Math.Max(1,allowance/16)},
                  {2,2,4,4,Math.Max(1,allowance/8)},
                  {0,1,2,2,Math.Max(1,3*allowance/8)},
                  {1,0,2,2,5*allowance/8},{1,1,2,2,7*allowance/8}};
   // Preserve strict bounds: the last fitting origin is not visited.
   long stopX=(long)right+1-w,stopY=(long)bottom+1-h;
   for(long yl=top;yl<stopY;yl++)for(long xl=left;xl<stopX;xl++){
    int x=(int)xl,y=(int)yl,misses=0;bool reject=false;
    if(cancelled!=null&&cancelled())throw new OperationCanceledException();
    for(int stage=0;stage<5&&!reject;stage++){
     for(int yy=stages[stage,1];yy<h&&!reject;yy+=stages[stage,3]){
      if(cancelled!=null&&cancelled())throw new OperationCanceledException();
      for(int xx=stages[stage,0];xx<w;xx+=stages[stage,2]){
       int target=Rgb(template,checked(tx+xx),checked(ty+yy));
       if((!transparentRgb.HasValue||target!=transparentRgb.Value)&&Difference(Rgb(frame,checked(x+xx),checked(y+yy)),target)>=24)misses++;
       if(misses>stages[stage,4]){reject=true;break;}
      }
     }
    }
    if(!reject)return new VisionPoint(x,y);
   }
   return new VisionPoint(-1,-1);
  }
  public static int FindPic(VisionFrame frame,VisionFrame template,int left,int top,int right,int bottom,double similarity,Func<bool> cancelled=null){
   var point=FindPicture(frame,template,left,top,right,bottom,similarity,null,cancelled);
   return checked(point.X*8192+point.Y);
  }
 }
}
