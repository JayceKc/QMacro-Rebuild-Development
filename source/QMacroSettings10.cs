using System;
using System.Collections.Generic;
namespace QMacroRebuild {
 public sealed class Settings10 {
  public int PotionIndex,SkillIndex,SpeedIndex,Flags;
  public string GText;
  public bool PressG,UseF1,UseOne,Revive;
  public int SkillEntry,PotionEntry,DeathEntry;
  public static string ApplyInputChange(string text){return text.Length==0?"":text.Substring(text.Length-1);}
  public static Settings10 Resolve(IDictionary<string,object> ui){
   var value=new Settings10();value.PotionIndex=Convert.ToInt32(ui["Form1.ComboBox1.ListIndex"]);
   value.SkillIndex=Convert.ToInt32(ui["Form1.ComboBox2.ListIndex"]);value.SpeedIndex=Convert.ToInt32(ui["Form1.ComboBox3.ListIndex"]);
   if(value.PotionIndex<0||value.PotionIndex>4||value.SkillIndex<0||value.SkillIndex>3||value.SpeedIndex<0||value.SpeedIndex>3)throw new ArgumentException("請先選擇有效的模式與速度。");
   value.UseF1=Convert.ToInt32(ui["Form1.CheckBox1.Value"])==1;value.UseOne=Convert.ToInt32(ui["Form1.CheckBox2.Value"])==1;
   value.Revive=Convert.ToInt32(ui["Form1.CheckBox3.Value"])==1;bool g=Convert.ToInt32(ui["Form1.CheckBox4.Value"])==1;
   value.GText=Convert.ToString(ui["Form1.InputBox1.Text"]);
   if(g&&(value.GText.Length!=1||value.GText[0]<'1'||value.GText[0]>'9'))throw new ArgumentException("勾選 G 時，等待秒數請填入 1 到 9。");
   value.PressG=g;value.Flags=(value.UseF1?1:0)|(value.UseOne?2:0)|(value.Revive?4:0)|(g?8:0);
   value.SkillEntry=new[]{959,1054,1136,1231}[value.SkillIndex];value.PotionEntry=new[]{1538,1326,1379,1432,1485}[value.PotionIndex];value.DeathEntry=value.Revive?1551:0;
   return value;
  }
 }
}
