// Owned implementation of Runner builtin image arithmetic, not dm.FindColor.
// Input is an immutable supplied RGB frame. No capture, native DLL or input here.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;

namespace QMacroRebuild {
 public static class BuiltinColor {
  public static IEnumerable<VisionPoint> Points(int left,int top,int right,int bottom,int mode){
   if(left>right||top>bottom||mode<0||mode>1)throw new ArgumentException("Unverified builtin rectangle or scan mode");
   if(mode==0){for(int y=top;y<=bottom;y++)for(int x=left;x<=right;x++)yield return new VisionPoint(x,y);yield break;}
   int cx=left+(right-left+1)/2,cy=top+(bottom-top+1)/2;yield return new VisionPoint(cx,cy);
   int radius=Math.Max(Math.Max(cx-left,right-cx),Math.Max(cy-top,bottom-cy));
   for(int r=1;r<=radius;r++){
    for(int x=Math.Max(left,cx-r);x<=Math.Min(right,cx+r);x++){
     if(cy-r>=top&&cy-r<=bottom)yield return new VisionPoint(x,cy-r);
     if(cy+r>=top&&cy+r<=bottom)yield return new VisionPoint(x,cy+r);
    }
    for(int y=Math.Max(top,cy-r+1);y<=Math.Min(bottom,cy+r-1);y++){
     if(cx-r>=left&&cx-r<=right)yield return new VisionPoint(cx-r,y);
     if(cx+r>=left&&cx+r<=right)yield return new VisionPoint(cx+r,y);
    }
   }
  }
  public static int FindColor(VisionFrame frame,int left,int top,int right,int bottom,string bgr,int mode,double similarity,Func<bool> cancelled=null){
   if(frame==null)throw new ArgumentNullException("frame");
   if(bgr==null||!Regex.IsMatch(bgr,"\\A[0-9a-fA-F]{6}\\z"))throw new ArgumentException("Only six-digit BGR strings verified");
   if(Double.IsNaN(similarity)||Double.IsInfinity(similarity)||similarity<.1||similarity>1)throw new ArgumentException("Unverified builtin similarity");
   if(left>right||top>bottom||left<frame.OriginX||top<frame.OriginY||(long)right>=frame.OriginX+(long)frame.Width||(long)bottom>=frame.OriginY+(long)frame.Height)throw new ArgumentException("Inclusive rectangle outside frame");
   frame.ValidateRect(left,top,right,bottom);
   float single=(float)similarity;int threshold=(int)((1-(double)single)*100);bool exact=(double)single>.99;
   int red=Int32.Parse(bgr.Substring(4,2),NumberStyles.HexNumber),green=Int32.Parse(bgr.Substring(2,2),NumberStyles.HexNumber),blue=Int32.Parse(bgr.Substring(0,2),NumberStyles.HexNumber);
   foreach(var p in Points(left,top,right,bottom,mode)){
    if(cancelled!=null&&cancelled())throw new OperationCanceledException();
    int i=frame.Index(p.X,p.Y),dr=Math.Abs(frame.Data[i]-red),dg=Math.Abs(frame.Data[i+1]-green),db=Math.Abs(frame.Data[i+2]-blue);
    if(exact?dr+dg+db==0:dr+dg+db<threshold)return checked(p.X*8192+p.Y);
   }
   return -8193;
  }
 }
 public static class OwnedBuiltinPrelude {
  // Reviewed definitions only. Deliberately excludes original COM initialization.
  public const string Text=@"Function GetCursorPos(ByRef outX, ByRef outY)
Dim packedCursor
packedCursor=QMLibrary.GetCursorPos()
outY=packedCursor Mod 8192
outX=CInt(packedCursor / 8192)
End Function
Function FindColorEx(left,top,right,bottom,color,kind,similarity,ByRef outX,ByRef outY)
Dim packedColor
packedColor=QMLibrary.FindColor(left,top,right,bottom,color,kind,similarity)
outX=CInt(packedColor / 8192)
outY=packedColor Mod 8192
FindColorEx=packedColor
End Function
Function FindPic(left,top,right,bottom,file,similarity,ByRef outX,ByRef outY)
Dim packedPicture
packedPicture=QMLibrary.FindPic(left,top,right,bottom,file,similarity)
outX=CInt(packedPicture / 8192)
outY=packedPicture Mod 8192
FindPic=packedPicture
End Function";
 }
}
