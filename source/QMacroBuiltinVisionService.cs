// Explicit read-only adapters for reviewed builtin calls. No default desktop,
// arbitrary path loader, cursor fallback or native vendor DLL is created here.
using System;
using System.Text.RegularExpressions;

namespace QMacroRebuild {
 public sealed class BuiltinVisionService {
  readonly Func<int,int,int,int,VisionFrame> capture;
  readonly Func<string,VisionFrame> resolve;
  readonly Func<VisionPoint> cursor;
  readonly Func<bool> cancelled;
  public BuiltinVisionService(Func<int,int,int,int,VisionFrame> captureExclusive,Func<string,VisionFrame> resolveReviewedAsset,Func<VisionPoint> readCursor=null,Func<bool> isCancelled=null){
   if(captureExclusive==null||resolveReviewedAsset==null)throw new ArgumentNullException("capture/resolve");
   capture=captureExclusive;resolve=resolveReviewedAsset;cursor=readCursor;cancelled=isCancelled;
  }
  static int I(object x){if(!(x is int))throw new ArgumentException("Expected Int32 builtin argument");return (int)x;}
  static string S(object x){if(!(x is string))throw new ArgumentException("Expected string builtin argument");return (string)x;}
  static double Similarity(object x){
   if(!(x is double))throw new ArgumentException("Expected Double builtin similarity");double v=(double)x;
   if(Double.IsNaN(v)||Double.IsInfinity(v)||v<.1||v>1)throw new ArgumentException("Unverified builtin similarity");return v;
  }
  public object Invoke(string name,object[] args){
   if(args==null)throw new ArgumentNullException("args");
   if(cancelled!=null&&cancelled())throw new OperationCanceledException();
   if(name=="builtin_cursor"){
    if(args.Length!=0)throw new ArgumentException("Cursor arity");
    if(cursor==null)throw new NotSupportedException("A verified cursor provider was not supplied");
    var position=cursor();return checked(position.X*8192+position.Y);
   }
   int expected=name=="builtin_color"?7:name=="builtin_picture"?6:-1;
   if(expected<0)throw new NotSupportedException("Unknown builtin service "+name);
   if(args.Length!=expected)throw new ArgumentException("Builtin argument count");
   int left=I(args[0]),top=I(args[1]),right=I(args[2]),bottom=I(args[3]);
   if(left>right||top>bottom)throw new ArgumentException("Reversed builtin rectangle has not been replayed");
   string spec=S(args[4]);double sim=Similarity(args[expected-1]);
   int mode=0;VisionFrame template=null;
   if(name=="builtin_color"){
    mode=I(args[5]);if(mode<0||mode>1||!Regex.IsMatch(spec,"\\A[0-9a-fA-F]{6}\\z"))throw new ArgumentException("Unverified builtin color/mode");
   }else{
    template=resolve(spec);if(template==null)throw new InvalidOperationException("Asset resolver returned no image");
   }
   // The existing GDI sampler takes exclusive right/bottom; builtin calls do not.
   VisionFrame frame=capture(left,top,checked(right+1),checked(bottom+1));
   if(frame==null)throw new InvalidOperationException("Capture returned no frame");
   if(name=="builtin_color")return BuiltinColor.FindColor(frame,left,top,right,bottom,spec,mode,sim,cancelled);
   return BuiltinPicture.FindPic(frame,template,left,top,right,bottom,sim,cancelled);
  }
 }
}
