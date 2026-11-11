# 09 渴望島：缺失初始化線索

這是線索清單，尚未將未引用字串當作原始指令。
SL 截止點只供閱讀；它不是函式入口或完整缺失來源的界線。編譯器可能把右側表達式配置在截止點之後。

## 保留的位置群組

L00000..L00011 loc=0 flags=0 count=12 ops=30,30,30,30,30,30,30,30,30,30,30,29
L00012..L00012 loc=1 flags=0 count=1 ops=255
L00013..L00013 loc=2 flags=0 count=1 ops=255
L00014..L00014 loc=6 flags=0 count=1 ops=255
L00015..L00015 loc=7 flags=0 count=1 ops=255
L00016..L00016 loc=8 flags=0 count=1 ops=255
L00017..L00017 loc=10 flags=0 count=1 ops=255
L00018..L00018 loc=11 flags=0 count=1 ops=255
L00019..L00019 loc=12 flags=0 count=1 ops=255
L00020..L00020 loc=13 flags=0 count=1 ops=255
L00021..L00021 loc=15 flags=0 count=1 ops=255
L00022..L00022 loc=17 flags=0 count=1 ops=255
L00023..L00023 loc=18 flags=0 count=1 ops=255
L00024..L00024 loc=19 flags=0 count=1 ops=255
L00025..L00025 loc=20 flags=0 count=1 ops=255
L00026..L00027 loc=22 flags=0 count=2 ops=255,255
L00028..L00028 loc=23 flags=0 count=1 ops=255
L00029..L00029 loc=24 flags=0 count=1 ops=255
L00030..L00030 loc=25 flags=0 count=1 ops=255
L00031..L00031 loc=27 flags=0 count=1 ops=255
L00032..L00032 loc=28 flags=0 count=1 ops=255
L00033..L00033 loc=29 flags=0 count=1 ops=255
L00034..L00034 loc=30 flags=0 count=1 ops=255
L00035..L00035 loc=31 flags=0 count=1 ops=255
L00036..L00036 loc=32 flags=0 count=1 ops=255
L00037..L00039 loc=33 flags=0 count=3 ops=255,255,255
L00040..L00040 loc=34 flags=0 count=1 ops=255
L00041..L00041 loc=38 flags=0 count=1 ops=255
L00042..L00042 loc=39 flags=0 count=1 ops=255
L00043..L00043 loc=40 flags=0 count=1 ops=255
L00044..L00044 loc=41 flags=0 count=1 ops=255
L00045..L00045 loc=42 flags=0 count=1 ops=255
L00046..L00046 loc=43 flags=0 count=1 ops=255
L00047..L00047 loc=44 flags=0 count=1 ops=255
L00048..L00048 loc=45 flags=0 count=1 ops=255
L00049..L00049 loc=46 flags=0 count=1 ops=255
L00050..L00050 loc=47 flags=0 count=1 ops=255
L00051..L00051 loc=48 flags=0 count=1 ops=255
L00052..L00052 loc=49 flags=0 count=1 ops=255
L00053..L00053 loc=50 flags=0 count=1 ops=255
L00054..L00054 loc=54 flags=0 count=1 ops=255
L00055..L00057 loc=55 flags=0 count=3 ops=255,255,255
L00058..L00058 loc=56 flags=0 count=1 ops=255
L00059..L00059 loc=58 flags=0 count=1 ops=255
L00060..L00060 loc=59 flags=0 count=1 ops=255
L00061..L00062 loc=60 flags=0 count=2 ops=255,255
L00063..L00063 loc=61 flags=0 count=1 ops=255
L00064..L00064 loc=63 flags=0 count=1 ops=255
L00065..L00066 loc=64 flags=0 count=2 ops=255,255
L00067..L00067 loc=65 flags=0 count=1 ops=255
L00068..L00068 loc=66 flags=0 count=1 ops=255
L00069..L00069 loc=67 flags=0 count=1 ops=255
L00070..L00070 loc=69 flags=0 count=1 ops=255
L00071..L00072 loc=70 flags=0 count=2 ops=255,255
L00073..L00073 loc=72 flags=0 count=1 ops=255
L00074..L00074 loc=73 flags=0 count=1 ops=255
L00075..L00075 loc=74 flags=0 count=1 ops=255
L00076..L00076 loc=75 flags=0 count=1 ops=255
L00077..L00077 loc=76 flags=0 count=1 ops=255
L00078..L00078 loc=77 flags=0 count=1 ops=255
L00079..L00079 loc=78 flags=0 count=1 ops=255
L00080..L00080 loc=79 flags=0 count=1 ops=255
L00081..L00081 loc=80 flags=0 count=1 ops=255
L00082..L00083 loc=81 flags=0 count=2 ops=255,255
L00084..L00084 loc=82 flags=0 count=1 ops=255
L00085..L00085 loc=84 flags=0 count=1 ops=255
L00086..L00087 loc=85 flags=0 count=2 ops=255,255
L00088..L00088 loc=87 flags=0 count=1 ops=255
L00089..L00089 loc=88 flags=0 count=1 ops=255
L00090..L00090 loc=89 flags=0 count=1 ops=255
L00091..L00091 loc=90 flags=0 count=1 ops=255
L00092..L00092 loc=91 flags=0 count=1 ops=255
L00093..L00093 loc=92 flags=0 count=1 ops=255
L00094..L00094 loc=93 flags=0 count=1 ops=255
L00095..L00095 loc=94 flags=0 count=1 ops=255
L00096..L00096 loc=95 flags=0 count=1 ops=255
L00097..L00099 loc=96 flags=0 count=3 ops=255,255,255
L00100..L00100 loc=97 flags=0 count=1 ops=255
L00101..L00101 loc=98 flags=0 count=1 ops=255
L00102..L00102 loc=99 flags=0 count=1 ops=255
L00103..L00103 loc=100 flags=0 count=1 ops=255
L00104..L00104 loc=101 flags=0 count=1 ops=255
L00105..L00105 loc=102 flags=0 count=1 ops=255
L00106..L00106 loc=103 flags=0 count=1 ops=255
L00107..L00107 loc=104 flags=0 count=1 ops=255
L00108..L00108 loc=105 flags=0 count=1 ops=255
L00109..L00109 loc=106 flags=0 count=1 ops=255
L00110..L00110 loc=107 flags=0 count=1 ops=255
L00111..L00111 loc=108 flags=0 count=1 ops=255
L00112..L00112 loc=110 flags=0 count=1 ops=255
L00113..L00113 loc=111 flags=0 count=1 ops=255
L00114..L00114 loc=114 flags=0 count=1 ops=255
L00115..L00115 loc=117 flags=0 count=1 ops=255
L00116..L00116 loc=118 flags=0 count=1 ops=16

## 原 SL 字串順序

### SL[0] kind=decoded-text, 現有引用=True

Dim 暫存槽(256):Dim 目前呼叫框架,新呼叫框架:Set 目前呼叫框架=Nothing:Set 新呼叫框架=Nothing

### SL[1] kind=decoded-text, 現有引用=True

Class 框架類別_〔更多Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[2] kind=decoded-text, 現有引用=True

Class 框架類別_〔找怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[3] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能三〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[4] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能四〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[5] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能一〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[6] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能二〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[7] kind=decoded-text, 現有引用=True

Class 框架類別_〔不使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[8] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用X技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[9] kind=decoded-text, 現有引用=True

Class 框架類別_〔第一次打怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[10] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[11] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[12] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[13] kind=text, 現有引用=False

SET WS=CREATEOBJECT("Wscript.Shell")

### SL[14] kind=decoded-text, 現有引用=False

Call WS.RUN("regsvr32 atl.dll /s")

### SL[15] kind=text, 現有引用=False

SET WS=nothing

### SL[16] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[17] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro\fz","fz.dll")

### SL[18] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","fzreg.dll")

### SL[19] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","*.bmp")

### SL[20] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(QMLibrary.CallAPI2("C:\users\mymacro\fzreg.dll", "SetDllPathW", "C:\users\mymacro\fz\fz.dll", 0))

### SL[21] kind=text, 現有引用=False

SET DM=CREATEOBJECT("dm.dmsoft")

### SL[22] kind=decoded-text, 現有引用=False

Call DM.SETSHOWERRORMSG(0)

### SL[23] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[24] kind=decoded-text, 現有引用=False

〔版本〕=DM.VER()

### SL[25] kind=text, 現有引用=False

Sgn((〔版本〕=7.2450))

### SL[26] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("成功"))

### SL[27] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("失败"))

### SL[28] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[29] kind=decoded-text, 現有引用=False

〔鼠標〕=DM.ENABLEREALMOUSE(2,10,60)

### SL[30] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("鼠标" & 〔鼠標〕)

### SL[31] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[32] kind=text, 現有引用=False

〔索引〕=ARRAY(0,1,2,3,4,5)

### SL[33] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[34] kind=text, 現有引用=False

Form1.ComboBox2.ListIndex

### SL[35] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[36] kind=text, 現有引用=False

〔技能釋放〕=〔索引〕(暫存槽(1))

### SL[37] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[38] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[39] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[40] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[41] kind=text, 現有引用=False

Randomize

### SL[42] kind=text, 現有引用=False

YDX=INT(5*RND+35)

### SL[43] kind=text, 現有引用=False

Randomize

### SL[44] kind=text, 現有引用=False

YDY=INT(10*RND+10)

### SL[45] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[46] kind=decoded-text, 現有引用=False

Call DM.MOVETO(YDX,YDY)

### SL[47] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[48] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[49] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1500))

### SL[50] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint((">>>>>>脚本启动"))

### SL[51] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[52] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔第一次打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[53] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[54] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[55] kind=text, 現有引用=False

〔擊殺〕=0

### SL[56] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[57] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[58] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[59] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDCOLOR(515,147,1468,840,"C9993E-050505|CC9D44-050505|C28D42-050505",0.9,6,INTX,INTY)

### SL[60] kind=text, 現有引用=False

Sgn((INTX>=0))

### SL[61] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[62] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseMove(INTX,INTY,g_iSimulateModeInVBSBlock,0)

### SL[63] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[64] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(316,110,1530,840,"C:\users\mymacro\xuetiao1.bmp|C:\users\mymacro\xuetiao2.bmp|C:\users\mymacro\xuetiao5.bmp","151515",0.9,2,INTX,INTY)

### SL[65] kind=text, 現有引用=False

Sgn((INTX>=0))

### SL[66] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[67] kind=text, 現有引用=False

INTY=INTY+70

### SL[68] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[69] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseMove(INTX,INTY,g_iSimulateModeInVBSBlock,0)

### SL[70] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[71] kind=decoded-text, 現有引用=False

Call QMLibrary.ThreadControl((〔放技能ID〕), 2)

### SL[72] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[73] kind=decoded-text, 現有引用=False

Call QMLibrary.ThreadControl((〔找怪ID〕), 2)

### SL[74] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[75] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[76] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[77] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(600,10,800,135,"C:\users\mymacro\jingyingtou1.bmp|C:\users\mymacro\jingyingtou2.bmp","222222",0.8,0,INTX,INTY)

### SL[78] kind=text, 現有引用=False

Sgn((INTX>=0))

### SL[79] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[80] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[81] kind=decoded-text, 現有引用=False

Call QMLibrary.ThreadControl((〔放技能ID〕), 1)

### SL[82] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[83] kind=decoded-text, 現有引用=False

Call QMLibrary.ThreadControl((〔找怪ID〕), 1)

### SL[84] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[85] kind=text, 現有引用=False

〔擊殺〕=〔擊殺〕+1

### SL[86] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[87] kind=decoded-text, 現有引用=False

傳回值=暫存槽(1)

### SL[88] kind=text, 現有引用=False

Form1.InputBox2.Text

### SL[89] kind=text, 現有引用=False

暫存槽(1)=〔擊殺〕

### SL[90] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[91] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseMove(805,500,g_iSimulateModeInVBSBlock,0)

### SL[92] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[93] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[94] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(2,g_iSimulateModeInVBSBlock,1)

### SL[95] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(500)

### SL[96] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(2,g_iSimulateModeInVBSBlock,1)

### SL[97] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(3000)

### SL[98] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(2,g_iSimulateModeInVBSBlock,1)

### SL[99] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(3000)

### SL[100] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[101] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[102] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

