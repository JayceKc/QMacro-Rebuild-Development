// Typed dual-interface calls use the extracted x86 typelib offsets. Guest only.
using System;
using System.Runtime.InteropServices;
public sealed class GuestNativeDual:IDisposable {
 object instance;IntPtr native;
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int IntInt(IntPtr self,int value,out int result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int StrInt(IntPtr self,[MarshalAs(UnmanagedType.BStr)]string value,out int result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int StrStrInt(IntPtr self,[MarshalAs(UnmanagedType.BStr)]string a,[MarshalAs(UnmanagedType.BStr)]string b,out int result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int StrString(IntPtr self,[MarshalAs(UnmanagedType.BStr)]string value,out IntPtr result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int XYString(IntPtr self,int x,int y,out IntPtr result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int NoArgsString(IntPtr self,out IntPtr result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int XYInt(IntPtr self,int x,int y,out int result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int TripleInt(IntPtr self,int a,int b,int c,out int result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int QuadString(IntPtr self,int x,int y,int width,int height,out IntPtr result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int PicSearch(IntPtr self,int x1,int y1,int x2,int y2,[MarshalAs(UnmanagedType.BStr)]string files,[MarshalAs(UnmanagedType.BStr)]string delta,double similarity,int direction,[MarshalAs(UnmanagedType.Struct)]out object x,[MarshalAs(UnmanagedType.Struct)]out object y,out int result);
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int ColorSearch(IntPtr self,int x1,int y1,int x2,int y2,[MarshalAs(UnmanagedType.BStr)]string colors,double similarity,int direction,[MarshalAs(UnmanagedType.Struct)]out object x,[MarshalAs(UnmanagedType.Struct)]out object y,out int result);
 GuestNativeDual(){
  instance=GuestNativePlugin.Create();IntPtr unknown=Marshal.GetIUnknownForObject(instance);
  try{Guid iid=new Guid("f3f54bc2-d6d1-4a85-b943-16287ecea64c");Marshal.ThrowExceptionForHR(Marshal.QueryInterface(unknown,ref iid,out native));}
  catch{Marshal.FinalReleaseComObject(instance);instance=null;throw;}
  finally{Marshal.Release(unknown);}
 }
 public static GuestNativeDual Open(){return new GuestNativeDual();}
 Delegate Method(int offset,Type type){if(native==IntPtr.Zero)throw new ObjectDisposedException("GuestNativeDual");if(IntPtr.Size!=4)throw new NotSupportedException("Extracted x86 ABI only");return Marshal.GetDelegateForFunctionPointer(Marshal.ReadIntPtr(Marshal.ReadIntPtr(native),offset),type);}
 int StringInteger(int offset,string value){int result;Marshal.ThrowExceptionForHR(((StrInt)Method(offset,typeof(StrInt)))(native,value,out result));return result;}
 public int SetShowErrorMsg(int value){int result;Marshal.ThrowExceptionForHR(((IntInt)Method(228,typeof(IntInt)))(native,value,out result));return result;}
 public int SetPicPwd(string value){return StringInteger(580,value);}
 public int LoadPic(string value){return StringInteger(400,value);}
 public int SetDisplayInput(string value){return StringInteger(620,value);}
 public int ImageToBmp(string input,string output){int result;Marshal.ThrowExceptionForHR(((StrStrInt)Method(784,typeof(StrStrInt)))(native,input,output,out result));return result;}
 public string GetPicSize(string input){IntPtr text=IntPtr.Zero;try{Marshal.ThrowExceptionForHR(((StrString)Method(768,typeof(StrString)))(native,input,out text));return text==IntPtr.Zero?"":Marshal.PtrToStringBSTR(text);}finally{if(text!=IntPtr.Zero)Marshal.FreeBSTR(text);}}
 public string GetColor(int x,int y){IntPtr text=IntPtr.Zero;try{Marshal.ThrowExceptionForHR(((XYString)Method(132,typeof(XYString)))(native,x,y,out text));return text==IntPtr.Zero?"":Marshal.PtrToStringBSTR(text);}finally{if(text!=IntPtr.Zero)Marshal.FreeBSTR(text);}}
 public string Ver(){IntPtr text=IntPtr.Zero;try{Marshal.ThrowExceptionForHR(((NoArgsString)Method(28,typeof(NoArgsString)))(native,out text));return text==IntPtr.Zero?"":Marshal.PtrToStringBSTR(text);}finally{if(text!=IntPtr.Zero)Marshal.FreeBSTR(text);}}
 public int MoveTo(int x,int y){int result;Marshal.ThrowExceptionForHR(((XYInt)Method(124,typeof(XYInt)))(native,x,y,out result));return result;}
 public int EnableRealMouse(int mode,int delay,int step){int result;Marshal.ThrowExceptionForHR(((TripleInt)Method(1020,typeof(TripleInt)))(native,mode,delay,step,out result));return result;}
 public string MoveToEx(int x,int y,int width,int height){IntPtr text=IntPtr.Zero;try{Marshal.ThrowExceptionForHR(((QuadString)Method(500,typeof(QuadString)))(native,x,y,width,height,out text));return text==IntPtr.Zero?"":Marshal.PtrToStringBSTR(text);}finally{if(text!=IntPtr.Zero)Marshal.FreeBSTR(text);}}
 public int FindPic(int x1,int y1,int x2,int y2,string files,string delta,double similarity,int direction,out object x,out object y){int result;Marshal.ThrowExceptionForHR(((PicSearch)Method(456,typeof(PicSearch)))(native,x1,y1,x2,y2,files,delta,similarity,direction,out x,out y,out result));return result;}
 public int FindColor(int x1,int y1,int x2,int y2,string colors,double similarity,int direction,out object x,out object y){int result;Marshal.ThrowExceptionForHR(((ColorSearch)Method(176,typeof(ColorSearch)))(native,x1,y1,x2,y2,colors,similarity,direction,out x,out y,out result));return result;}
 public void Dispose(){if(native!=IntPtr.Zero){Marshal.Release(native);native=IntPtr.Zero;}if(instance!=null){Marshal.FinalReleaseComObject(instance);instance=null;}}
}
