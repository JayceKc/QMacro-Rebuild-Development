// Module-scoped original images. No cross-container fallback or original DLL load.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
namespace QMacroRebuild {
 public sealed class OriginalAssetResolver {
  readonly string root;
  readonly Dictionary<string,Dictionary<string,object>> files=new Dictionary<string,Dictionary<string,object>>(StringComparer.OrdinalIgnoreCase);
  readonly Dictionary<string,VisionFrame> cache=new Dictionary<string,VisionFrame>(StringComparer.Ordinal);
  public readonly string CanonicalContainer;
  public int ImageCount {get{return files.Count;}}
  public OriginalAssetResolver(string projectRoot,string container){
   root=Path.GetFullPath(projectRoot).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;
   var document=(Dictionary<string,object>)new JavaScriptSerializer(){MaxJsonLength=32*1024*1024}.DeserializeObject(File.ReadAllText(Path.Combine(root,"data","asset-catalog.json")));
   if(Convert.ToInt32(document["schema"])!=1)throw new InvalidDataException("Unknown image catalog schema");
   foreach(object item in (object[])document["containers"]){var entry=(Dictionary<string,object>)item;if((string)entry["container"]==container){string side=container.Split('/')[0];if(side!="account"&&side!="card")throw new InvalidDataException("Unknown container side");CanonicalContainer=side+"/"+Convert.ToInt32(entry["canonical_module"]).ToString("D2");break;}}
   if(CanonicalContainer==null)throw new ArgumentException("Unknown image container");
   foreach(object item in (object[])document["images"]){var image=(Dictionary<string,object>)item;if((string)image["container"]!=CanonicalContainer)continue;
    string name=(string)image["filename"],expected="assets/restored/"+CanonicalContainer+"/attachments/"+name;
    if(name!=Path.GetFileName(name)||String.IsNullOrEmpty(name)||(string)image["bundle_path"]!=expected)throw new InvalidDataException("Image path/name mismatch");files.Add(name,image);
   }
  }
  static string Name(string originalPath){
   if(String.IsNullOrEmpty(originalPath))throw new FileNotFoundException("No image filename supplied");
   const string prefix=@"C:\users\mymacro\";
   string name=originalPath.StartsWith(prefix,StringComparison.OrdinalIgnoreCase)?originalPath.Substring(prefix.Length):originalPath;
   if(name!=Path.GetFileName(name)||name.Contains(":"))throw new ArgumentException("Image is outside the mapped original attachment root");return name;
  }
  static string Hash(byte[] bytes){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
  public string ResolveFile(string originalPath){
   Dictionary<string,object> entry;if(!files.TryGetValue(Name(originalPath),out entry))throw new FileNotFoundException("Image is absent from "+CanonicalContainer,originalPath);
   string path=Path.GetFullPath(Path.Combine(root,((string)entry["bundle_path"]).Replace('/',Path.DirectorySeparatorChar)));
   if(!path.StartsWith(root,StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Image escaped project directory");
   byte[] bytes=File.ReadAllBytes(path);if(bytes.LongLength!=Convert.ToInt64(entry["bytes"])||Hash(bytes)!=(string)entry["sha256"])throw new InvalidDataException("Image source digest mismatch: "+originalPath);return path;
  }
  public VisionFrame ResolveImage(string originalPath){
   string name=Name(originalPath);Dictionary<string,object> entry;if(!files.TryGetValue(name,out entry))throw new FileNotFoundException("Image is absent from "+CanonicalContainer,originalPath);
   string hash=(string)entry["sha256"];lock(cache){VisionFrame frame;if(cache.TryGetValue(hash,out frame))return frame;frame=VisionFrame.ReadBmp(ResolveFile(originalPath));cache.Add(hash,frame);return frame;}
  }
 }
}
