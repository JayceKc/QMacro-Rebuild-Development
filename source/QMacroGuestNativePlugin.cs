// Direct COM class factory, fixed isolated guest and fixed packed DLL only.
// Does not register a DLL or depend on the interactive user's HKCU registry.
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using Microsoft.Win32;
public static class GuestNativePlugin {
 const string Dll=@"C:\Users\Public\Documents\QMacroLab\fz.dll";
 const string Digest="a23fb027db71c668f8bc13399d148c6ed18f8ef242121e58f73a5e4f57eb3bfc";
 static IntPtr module;
 [ComImport,Guid("00000001-0000-0000-C000-000000000046"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 interface IClassFactory {
  [PreserveSig]int CreateInstance(IntPtr outer,ref Guid interfaceId,[MarshalAs(UnmanagedType.Interface)]out object instance);
  [PreserveSig]int LockServer([MarshalAs(UnmanagedType.Bool)]bool locked);
 }
 [UnmanagedFunctionPointer(CallingConvention.StdCall)]delegate int GetClassObject(ref Guid classId,ref Guid interfaceId,out IntPtr factory);
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]static extern IntPtr LoadLibraryEx(string file,IntPtr reserved,uint flags);
 [DllImport("kernel32.dll",CharSet=CharSet.Ansi,ExactSpelling=true,SetLastError=true)]static extern IntPtr GetProcAddress(IntPtr library,string name);
 public static object Create(){
  string vendor=Convert.ToString(Registry.GetValue(@"HKEY_LOCAL_MACHINE\HARDWARE\DESCRIPTION\System\BIOS","SystemManufacturer",""));
  if(vendor.IndexOf("VMware",StringComparison.OrdinalIgnoreCase)<0||Environment.MachineName!="DESKTOP-GAR2QIL"||Environment.UserName!="kc")throw new InvalidOperationException("Fixed isolated VMware guest only");
  using(var hash=SHA256.Create())if(BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes(Dll))).Replace("-","").ToLowerInvariant()!=Digest)throw new InvalidDataException("Original packed DLL hash mismatch");
  if(module==IntPtr.Zero){module=LoadLibraryEx(Dll,IntPtr.Zero,0x100|0x800);if(module==IntPtr.Zero)throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());}
  IntPtr entry=GetProcAddress(module,"DllGetClassObject");if(entry==IntPtr.Zero)throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
  var get=(GetClassObject)Marshal.GetDelegateForFunctionPointer(entry,typeof(GetClassObject));
  Guid clsid=new Guid("26037A0E-7CBD-4FFF-9C63-56F2D0770214"),factoryId=new Guid("00000001-0000-0000-C000-000000000046"),dispatch=new Guid("00020400-0000-0000-C000-000000000046");
  IntPtr pointer=IntPtr.Zero;object factory=null;
  try{
   Marshal.ThrowExceptionForHR(get(ref clsid,ref factoryId,out pointer));if(pointer==IntPtr.Zero)throw new Exception("Missing class factory");
   factory=Marshal.GetObjectForIUnknown(pointer);object instance;Marshal.ThrowExceptionForHR(((IClassFactory)factory).CreateInstance(IntPtr.Zero,ref dispatch,out instance));
   if(instance==null)throw new Exception("Missing native dispatch instance");return instance;
  }finally{if(factory!=null)Marshal.FinalReleaseComObject(factory);if(pointer!=IntPtr.Zero)Marshal.Release(pointer);}
  // Keep the module loaded until this short-lived probe process exits.
 }
}
