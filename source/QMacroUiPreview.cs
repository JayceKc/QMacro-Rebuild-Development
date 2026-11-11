// Owned Unicode UI renderer. Reads inert control data; never executes a macro.
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using System.Web.Script.Serialization;
using QMacroRebuild;

public sealed class UiSurface:Panel {
 public readonly Dictionary<string,Control> Named=new Dictionary<string,Control>(StringComparer.OrdinalIgnoreCase);
 public readonly Dictionary<string,object> Definition;
 public readonly int Module;
 public event Action<string> PreviewAction;
 readonly ToolTip tips=new ToolTip(){AutoPopDelay=20000,InitialDelay=400,ReshowDelay=100};
 readonly List<Font> ownedFonts=new List<Font>();
 static int N(object value){return Convert.ToInt32(value);}
 public UiSurface(Dictionary<string,object> data,string root){
  Definition=data;Module=N(data["module"]);BackColor=Color.White;AutoScroll=false;
  Font=new Font("Microsoft JhengHei",10f,FontStyle.Regular,GraphicsUnit.Pixel);ownedFonts.Add(Font);Size=new Size(605,246);
  foreach(object item in (object[])data["controls"]){
   var spec=(Dictionary<string,object>)item;string kind=(string)spec["type"],name=(string)spec["name"];
   var rect=(object[])spec["rect"];
   if(kind=="Form"){
    Size=new Size(N(rect[2])-N(rect[0]),N(rect[3])-N(rect[1]));
    if(spec.ContainsKey("picture_path")){using(var image=Image.FromFile(Path.Combine(root,((string)spec["picture_path"]).Replace('/',Path.DirectorySeparatorChar))))BackgroundImage=new Bitmap(image);BackgroundImageLayout=ImageLayout.None;}
    continue;
   }
   string text=(string)spec["text"];Control control;
   if(kind=="ComboBox"){
    var combo=new ComboBox(){DropDownStyle=ComboBoxStyle.DropDownList,IntegralHeight=false};
    foreach(object value in (object[])spec["items"])combo.Items.Add((string)value);
    int selected=N(spec["selected"]);if(selected>=0&&selected<combo.Items.Count)combo.SelectedIndex=selected;
    combo.DropDownWidth=Math.Max(350,N(rect[2])-N(rect[0]));control=combo;
   }else if(kind=="CheckBox")control=new CheckBox(){Text=text,Checked=N(spec["checked"])==1,AutoSize=false};
   else if(kind=="InputBox"){
    var input=new TextBox(){Text=text,ReadOnly=(bool)spec["readonly"]};
    if(Module==10&&name=="InputBox1")input.TextChanged+=(s,e)=>{string last=Settings10.ApplyInputChange(input.Text);if(last!=input.Text){input.Text=last;input.SelectionStart=input.Text.Length;}};
    control=input;
   }else if(kind=="Button"){
    var button=new Button(){Text=text};button.Click+=(s,e)=>{if(PreviewAction!=null)PreviewAction(Module==6?"預覽：原回呼要求清理五個快取目錄；本版只記錄，沒有刪檔。":"此按鈕的完整流程尚未接入。");};control=button;
   }else if(kind=="PictureBox"){
    var picture=new PictureBox(){SizeMode=PictureBoxSizeMode.Normal};
    if(spec.ContainsKey("picture_path")){using(var image=Image.FromFile(Path.Combine(root,((string)spec["picture_path"]).Replace('/',Path.DirectorySeparatorChar))))picture.Image=new Bitmap(image);}
    control=picture;
   }
   else throw new InvalidDataException("Unknown UI type "+kind);
   var nativeFont=new Font("Microsoft JhengHei",Math.Max(8,N(spec["font_pixels"])),FontStyle.Regular,GraphicsUnit.Pixel);ownedFonts.Add(nativeFont);
   control.Name=name;control.Tag=kind;control.Font=nativeFont;control.SetBounds(N(rect[0]),N(rect[1]),Math.Max(2,N(rect[2])-N(rect[0])),Math.Max(2,N(rect[3])-N(rect[1])));
   tips.SetToolTip(control,control.Text);
   if(control is ComboBox){var combo=(ComboBox)control;combo.SelectedIndexChanged+=(s,e)=>tips.SetToolTip(combo,combo.Text);}
   control.Visible=(bool)spec["visible"];control.Enabled=(bool)spec["enabled"];Controls.Add(control);Named.Add(name,control);if(kind=="PictureBox")control.SendToBack();
  }
  // One stored form is five pixels narrower than a visible child. Preserve
  // child positions while expanding the owned canvas to avoid clipping it.
  foreach(Control child in Controls)if(!(child is PictureBox))Size=new Size(Math.Max(Width,child.Right),Math.Max(Height,child.Bottom));
 }
 protected override void Dispose(bool disposing){
  if(disposing){tips.Dispose();if(BackgroundImage!=null)BackgroundImage.Dispose();foreach(var picture in Named.Values.OfType<PictureBox>())if(picture.Image!=null)picture.Image.Dispose();}
  base.Dispose(disposing);if(disposing)foreach(var font in ownedFonts)font.Dispose();
 }
 public Dictionary<string,object> Snapshot(){
  var state=new Dictionary<string,object>(StringComparer.OrdinalIgnoreCase);
  foreach(var item in Named){string key="Form1."+item.Key;Control control=item.Value;
   if(control is ComboBox){state[key+".ListIndex"]=((ComboBox)control).SelectedIndex;state[key+".Text"]=control.Text;}
   else if(control is CheckBox)state[key+".Value"]=((CheckBox)control).Checked?1:0;
   else if(control is TextBox)state[key+".Text"]=control.Text;
  }
  return state;
 }
}
public sealed class UiPreview:Form {
 readonly string root;readonly JavaScriptSerializer json=new JavaScriptSerializer(){MaxJsonLength=16*1024*1024};
 readonly object[] forms;readonly ComboBox selector=new ComboBox(){DropDownStyle=ComboBoxStyle.DropDownList};
 readonly Panel host=new Panel(){AutoScroll=true};readonly TextBox result=new TextBox(){Multiline=true,ReadOnly=true,ScrollBars=ScrollBars.Vertical};
 UiSurface current;
 public UiPreview(string projectRoot){
  root=projectRoot;var catalog=(Dictionary<string,object>)json.DeserializeObject(File.ReadAllText(Path.Combine(root,"data","ui-forms.json")));forms=(object[])catalog["forms"];
  Text="QMacro 繁體介面與設定預覽";ClientSize=new Size(850,570);Font=new Font("Microsoft JhengHei",10);AutoScaleMode=AutoScaleMode.None;
  var title=new Label(){Text="介面與設定預覽｜此版本不會送出遊戲按鍵",Left=18,Top=15,Width=800,Height=28};Controls.Add(title);
  selector.SetBounds(18,51,810,30);Controls.Add(selector);
  foreach(object item in forms){var f=(Dictionary<string,object>)item;selector.Items.Add(f["container"]+"　"+f["name"]);}
  host.SetBounds(18,95,810,280);host.BackColor=Color.FromArgb(241,245,249);Controls.Add(host);
  var inspect=new Button(){Text="檢查設定",Left=18,Top=388,Width=140,Height=34};inspect.Click+=(s,e)=>Inspect();Controls.Add(inspect);
  var save=new Button(){Text="輸出設定",Left=171,Top=388,Width=140,Height=34};save.Click+=(s,e)=>SaveSnapshot();Controls.Add(save);
  result.SetBounds(18,435,810,115);Controls.Add(result);selector.SelectedIndexChanged+=(s,e)=>SelectForm();selector.SelectedIndex=9;
 }
 void SelectForm(){if(current!=null){host.Controls.Remove(current);current.Dispose();}current=new UiSurface((Dictionary<string,object>)forms[selector.SelectedIndex],root);current.PreviewAction+=s=>result.Text=s;current.Location=new Point(10,10);host.Controls.Add(current);result.Text="已載入原始控制項、選項及預設值。";}
 void Inspect(){
  try{
   var state=current.Snapshot();
   if(current.Module==10){var cfg=Settings10.Resolve(state);string skill=((ComboBox)current.Named["ComboBox2"]).Text,potion=((ComboBox)current.Named["ComboBox1"]).Text;
    result.Text="設定已核對。"+Environment.NewLine+"技能："+skill+Environment.NewLine+"吃藥："+potion+"；F1="+cfg.UseF1+"；1="+cfg.UseOne+Environment.NewLine+"G="+cfg.PressG+"；復活="+cfg.Revive+"。尚未啟動遊戲操作。";
   }else result.Text="已讀取 "+state.Count+" 個設定值。這組的完整啟動流程仍在還原中。";
  }catch(Exception ex){result.Text=ex.Message;}
 }
 void SaveSnapshot(){string directory=Path.Combine(root,"settings");Directory.CreateDirectory(directory);string file=Path.Combine(directory,DateTime.Now.ToString("yyyyMMdd-HHmmss-fff")+"-"+((string)current.Definition["container"]).Replace('/','-')+".json");File.WriteAllText(file,json.Serialize(current.Snapshot()),new System.Text.UTF8Encoding(false));result.Text="已輸出設定："+file;}
 static string Root(){string local=AppDomain.CurrentDomain.BaseDirectory;return File.Exists(Path.Combine(local,"data","ui-forms.json"))?local:Path.GetFullPath(Path.Combine(local,".."));}
 [STAThread]public static int Main(string[] args){
  Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);string root=Root();
  if(args.Length==2&&args[0]=="--verify")return Verify(root,args[1]);
  Application.Run(new UiPreview(root));return 0;
 }
 static int Verify(string root,string output){
  Directory.CreateDirectory(output);var json=new JavaScriptSerializer(){MaxJsonLength=16*1024*1024};var catalog=(Dictionary<string,object>)json.DeserializeObject(File.ReadAllText(Path.Combine(root,"data","ui-forms.json")));
  var results=new List<object>();string error=null;int controls=0;
  try{foreach(object item in (object[])catalog["forms"]){var spec=(Dictionary<string,object>)item;
   using(var form=new OffscreenUiForm())using(var surface=new UiSurface(spec,root)){
    form.ClientSize=surface.Size;form.Controls.Add(surface);form.Show();Application.DoEvents();
    foreach(Control c in surface.Controls)c.CreateControl();
    using(var image=new Bitmap(surface.Width,surface.Height)){surface.DrawToBitmap(image,surface.ClientRectangle);image.Save(Path.Combine(output,((string)spec["container"]).Replace('/','-')+".png"));}
    foreach(var c in surface.Named.Values)if(!(c is PictureBox)&&(c.Bounds.Right>surface.Width||c.Bounds.Bottom>surface.Height||c.Left<0||c.Top<0))throw new Exception("Control outside source form: "+c.Name);
    int visible=surface.Named.Values.Count(c=>c.Visible);if(visible!=surface.Named.Count)throw new Exception("UI children did not become drawable");
    var snapshot=surface.Snapshot();if(surface.Module==10){
     var cfg=Settings10.Resolve(snapshot);RequireDefault(cfg);
     var input=(TextBox)surface.Named["InputBox1"];input.Text="123";if(input.Text!="3")throw new Exception("Actual input change event failed");input.Text="45";if(input.Text!="5")throw new Exception("Repeated input change event failed");
     ((CheckBox)surface.Named["CheckBox4"]).Checked=true;input.Text="";bool rejected=false;try{Settings10.Resolve(surface.Snapshot());}catch(ArgumentException){rejected=true;}if(!rejected)throw new Exception("Empty G wait accepted by UI");
    }
    controls+=surface.Named.Count+1;results.Add(new{container=spec["container"],controls=surface.Named.Count+1,properties=snapshot.Count});
   }
  }}catch(Exception ex){error=ex.ToString();}
  File.WriteAllText(Path.Combine(output,"ui-render-verification.json"),json.Serialize(new{ok=error==null,error=error,forms=results,controls=controls,original_native_loaded=false,game_input_sent=false,wrapper_artwork_restored=false,full_program_restored=false}),new System.Text.UTF8Encoding(false));return error==null?0:1;
 }
 static void RequireDefault(Settings10 cfg){if(cfg.PotionIndex!=0||cfg.SkillIndex!=0||cfg.SpeedIndex!=0||cfg.Flags!=0||cfg.GText!="5")throw new Exception("Original UI defaults changed");}
}
public sealed class OffscreenUiForm:Form {
 public OffscreenUiForm(){ShowInTaskbar=false;AutoScaleMode=AutoScaleMode.None;StartPosition=FormStartPosition.Manual;Location=new Point(-20000,-20000);Opacity=0;FormBorderStyle=FormBorderStyle.None;}
 protected override bool ShowWithoutActivation {get{return true;}}
 protected override CreateParams CreateParams {get{var p=base.CreateParams;p.ExStyle|=0x08000080;return p;}}
}
