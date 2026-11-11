# 10 自動按技能：缺失初始化線索

這是線索清單，尚未將未引用字串當作原始指令。
SL 截止點只供閱讀；它不是函式入口或完整缺失來源的界線。編譯器可能把右側表達式配置在截止點之後。

## 保留的位置群組

L00000..L00016 loc=0 flags=0 count=17 ops=30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,29
L00017..L00017 loc=1 flags=0 count=1 ops=255
L00018..L00018 loc=2 flags=0 count=1 ops=255
L00019..L00019 loc=6 flags=0 count=1 ops=255
L00020..L00020 loc=7 flags=0 count=1 ops=255
L00021..L00021 loc=8 flags=0 count=1 ops=255
L00022..L00022 loc=10 flags=0 count=1 ops=255
L00023..L00023 loc=11 flags=0 count=1 ops=255
L00024..L00024 loc=12 flags=0 count=1 ops=255
L00025..L00025 loc=13 flags=0 count=1 ops=255
L00026..L00026 loc=14 flags=0 count=1 ops=255
L00027..L00027 loc=16 flags=0 count=1 ops=255
L00028..L00028 loc=17 flags=0 count=1 ops=255
L00029..L00029 loc=19 flags=0 count=1 ops=255
L00030..L00030 loc=20 flags=0 count=1 ops=255
L00031..L00031 loc=21 flags=0 count=1 ops=255
L00032..L00032 loc=22 flags=0 count=1 ops=255
L00033..L00034 loc=24 flags=0 count=2 ops=255,255
L00035..L00035 loc=25 flags=0 count=1 ops=255
L00036..L00036 loc=26 flags=0 count=1 ops=255
L00037..L00037 loc=27 flags=0 count=1 ops=255
L00038..L00038 loc=29 flags=0 count=1 ops=255
L00039..L00039 loc=30 flags=0 count=1 ops=255
L00040..L00040 loc=31 flags=0 count=1 ops=255
L00041..L00041 loc=32 flags=0 count=1 ops=255
L00042..L00042 loc=33 flags=0 count=1 ops=255
L00043..L00043 loc=34 flags=0 count=1 ops=255
L00044..L00044 loc=35 flags=0 count=1 ops=255
L00045..L00045 loc=36 flags=0 count=1 ops=255
L00046..L00046 loc=37 flags=0 count=1 ops=255
L00047..L00049 loc=38 flags=0 count=3 ops=255,255,255
L00050..L00050 loc=39 flags=0 count=1 ops=255
L00051..L00053 loc=40 flags=0 count=3 ops=255,255,255
L00054..L00054 loc=41 flags=0 count=1 ops=255
L00055..L00059 loc=42 flags=0 count=5 ops=255,255,255,255,255
L00060..L00060 loc=43 flags=0 count=1 ops=255
L00061..L00063 loc=44 flags=0 count=3 ops=255,255,255
L00064..L00064 loc=45 flags=0 count=1 ops=255
L00065..L00066 loc=46 flags=0 count=2 ops=255,2
L00067..L00071 loc=47 flags=0 count=5 ops=37,30,2,30,38
L00072..L00073 loc=48 flags=0 count=2 ops=2,13
L00074..L00078 loc=49 flags=0 count=5 ops=255,255,255,255,255
L00079..L00079 loc=50 flags=0 count=1 ops=255
L00080..L00083 loc=51 flags=0 count=4 ops=255,255,255,255
L00084..L00087 loc=52 flags=0 count=4 ops=255,255,255,255
L00088..L00091 loc=53 flags=0 count=4 ops=255,255,255,255
L00092..L00095 loc=54 flags=0 count=4 ops=255,255,255,255
L00096..L00099 loc=55 flags=0 count=4 ops=255,255,255,255
L00100..L00103 loc=56 flags=0 count=4 ops=255,255,255,255
L00104..L00107 loc=57 flags=0 count=4 ops=255,255,255,255
L00108..L00111 loc=58 flags=0 count=4 ops=255,255,255,255
L00112..L00115 loc=59 flags=0 count=4 ops=255,255,255,255
L00116..L00119 loc=60 flags=0 count=4 ops=255,255,255,255
L00120..L00123 loc=61 flags=0 count=4 ops=255,255,255,255
L00124..L00127 loc=62 flags=0 count=4 ops=255,255,255,255
L00128..L00131 loc=63 flags=0 count=4 ops=255,255,255,255
L00132..L00135 loc=64 flags=0 count=4 ops=255,255,255,255
L00136..L00139 loc=65 flags=0 count=4 ops=255,255,255,255
L00140..L00143 loc=66 flags=0 count=4 ops=255,255,255,255
L00144..L00147 loc=67 flags=0 count=4 ops=255,255,255,255
L00148..L00151 loc=68 flags=0 count=4 ops=255,255,255,255
L00152..L00154 loc=69 flags=0 count=3 ops=255,255,255
L00155..L00155 loc=70 flags=0 count=1 ops=255
L00156..L00158 loc=72 flags=0 count=3 ops=255,255,255
L00159..L00159 loc=74 flags=0 count=1 ops=255
L00160..L00163 loc=75 flags=0 count=4 ops=255,255,255,255
L00164..L00166 loc=76 flags=0 count=3 ops=255,255,255
L00167..L00167 loc=77 flags=0 count=1 ops=255
L00168..L00170 loc=78 flags=0 count=3 ops=255,255,255
L00171..L00171 loc=80 flags=0 count=1 ops=255
L00172..L00175 loc=81 flags=0 count=4 ops=255,255,255,255
L00176..L00178 loc=82 flags=0 count=3 ops=255,255,255
L00179..L00179 loc=83 flags=0 count=1 ops=255
L00180..L00182 loc=84 flags=0 count=3 ops=255,255,255
L00183..L00183 loc=86 flags=0 count=1 ops=255
L00184..L00187 loc=87 flags=0 count=4 ops=255,255,255,255
L00188..L00188 loc=88 flags=0 count=1 ops=255
L00189..L00189 loc=89 flags=0 count=1 ops=255
L00190..L00190 loc=90 flags=0 count=1 ops=255
L00191..L00191 loc=92 flags=0 count=1 ops=255
L00192..L00192 loc=95 flags=0 count=1 ops=255
L00193..L00193 loc=96 flags=0 count=1 ops=255
L00194..L00194 loc=99 flags=0 count=1 ops=255
L00195..L00196 loc=100 flags=0 count=2 ops=255,255
L00197..L00197 loc=101 flags=0 count=1 ops=255
L00198..L00198 loc=102 flags=0 count=1 ops=255
L00199..L00207 loc=103 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00208..L00209 loc=104 flags=0 count=2 ops=255,255
L00210..L00211 loc=105 flags=0 count=2 ops=255,255
L00212..L00212 loc=106 flags=0 count=1 ops=255
L00213..L00213 loc=107 flags=0 count=1 ops=255
L00214..L00222 loc=108 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00223..L00224 loc=109 flags=0 count=2 ops=255,255
L00225..L00226 loc=110 flags=0 count=2 ops=255,255
L00227..L00227 loc=111 flags=0 count=1 ops=255
L00228..L00228 loc=112 flags=0 count=1 ops=255
L00229..L00237 loc=113 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00238..L00239 loc=114 flags=0 count=2 ops=255,255
L00240..L00241 loc=115 flags=0 count=2 ops=255,255
L00242..L00242 loc=116 flags=0 count=1 ops=255
L00243..L00243 loc=117 flags=0 count=1 ops=255
L00244..L00252 loc=118 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00253..L00253 loc=119 flags=0 count=1 ops=255
L00254..L00254 loc=121 flags=0 count=1 ops=255
L00255..L00256 loc=122 flags=0 count=2 ops=255,255
L00257..L00257 loc=123 flags=0 count=1 ops=255
L00258..L00258 loc=124 flags=0 count=1 ops=255
L00259..L00267 loc=125 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00268..L00269 loc=126 flags=0 count=2 ops=255,255
L00270..L00271 loc=127 flags=0 count=2 ops=255,255
L00272..L00272 loc=128 flags=0 count=1 ops=255
L00273..L00273 loc=129 flags=0 count=1 ops=255
L00274..L00282 loc=130 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00283..L00284 loc=131 flags=0 count=2 ops=255,255
L00285..L00286 loc=132 flags=0 count=2 ops=255,255
L00287..L00287 loc=133 flags=0 count=1 ops=255
L00288..L00288 loc=134 flags=0 count=1 ops=255
L00289..L00297 loc=135 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00298..L00299 loc=136 flags=0 count=2 ops=255,255
L00300..L00301 loc=137 flags=0 count=2 ops=255,255
L00302..L00302 loc=138 flags=0 count=1 ops=255
L00303..L00303 loc=139 flags=0 count=1 ops=255
L00304..L00312 loc=140 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00313..L00314 loc=141 flags=0 count=2 ops=255,255
L00315..L00316 loc=142 flags=0 count=2 ops=255,255
L00317..L00317 loc=143 flags=0 count=1 ops=255
L00318..L00318 loc=144 flags=0 count=1 ops=255
L00319..L00327 loc=145 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00328..L00328 loc=146 flags=0 count=1 ops=255
L00329..L00329 loc=148 flags=0 count=1 ops=255
L00330..L00331 loc=149 flags=0 count=2 ops=255,255
L00332..L00332 loc=150 flags=0 count=1 ops=255
L00333..L00333 loc=151 flags=0 count=1 ops=255
L00334..L00342 loc=152 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00343..L00343 loc=153 flags=0 count=1 ops=255
L00344..L00344 loc=155 flags=0 count=1 ops=255
L00345..L00346 loc=156 flags=0 count=2 ops=255,255
L00347..L00347 loc=157 flags=0 count=1 ops=255
L00348..L00348 loc=158 flags=0 count=1 ops=255
L00349..L00349 loc=159 flags=0 count=1 ops=255
L00350..L00350 loc=160 flags=0 count=1 ops=255
L00351..L00351 loc=161 flags=0 count=1 ops=255
L00352..L00352 loc=162 flags=0 count=1 ops=255
L00353..L00353 loc=163 flags=0 count=1 ops=255
L00354..L00354 loc=164 flags=0 count=1 ops=16

## 原 SL 字串順序

### SL[0] kind=decoded-text, 現有引用=True

Dim 暫存槽(256):Dim 目前呼叫框架,新呼叫框架:Set 目前呼叫框架=Nothing:Set 新呼叫框架=Nothing

### SL[1] kind=decoded-text, 現有引用=True

Class 框架類別_〔啊不吃啊〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[2] kind=decoded-text, 現有引用=True

Class 框架類別_〔更多Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[3] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能三〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[4] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能四〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[5] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能一〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[6] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥11〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[7] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能二〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[8] kind=decoded-text, 現有引用=True

Class 框架類別_〔監控死亡〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[9] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥40〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[10] kind=decoded-text, 現有引用=True

Class 框架類別_〔不使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[11] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥6〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[12] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用X技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[13] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥70〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[14] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[15] kind=decoded-text, 現有引用=True

Class 框架類別_〔FORM1.INPUTBOX1.CHANGE〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[16] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[17] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[18] kind=text, 現有引用=False

SET WS=CREATEOBJECT("Wscript.Shell")

### SL[19] kind=decoded-text, 現有引用=False

Call WS.RUN("regsvr32 atl.dll /s")

### SL[20] kind=text, 現有引用=False

SET WS=nothing

### SL[21] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[22] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro\fz","fz.dll")

### SL[23] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","fzreg.dll")

### SL[24] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","*.bmp")

### SL[25] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[26] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(QMLibrary.CallAPI2("C:\users\mymacro\fzreg.dll", "SetDllPathW", "C:\users\mymacro\fz\fz.dll", 0))

### SL[27] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[28] kind=text, 現有引用=False

SET DM=CREATEOBJECT("dm.dmsoft")

### SL[29] kind=decoded-text, 現有引用=False

Call DM.SETSHOWERRORMSG(0)

### SL[30] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[31] kind=decoded-text, 現有引用=False

〔版本〕=DM.VER()

### SL[32] kind=text, 現有引用=False

Sgn((〔版本〕=7.2450))

### SL[33] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("成功"))

### SL[34] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("失败"))

### SL[35] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[36] kind=decoded-text, 現有引用=False

〔鼠標〕=DM.ENABLEREALMOUSE(2,10,60)

### SL[37] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("鼠标" & 〔鼠標〕)

### SL[38] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[39] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[40] kind=empty, 現有引用=False



### SL[41] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[42] kind=text, 現有引用=False

〔索引〕=ARRAY(0,1,2,3,4,5,6,7,8,9,10)

### SL[43] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[44] kind=text, 現有引用=False

Form1.ComboBox1.ListIndex

### SL[45] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[46] kind=text, 現有引用=False

〔吃藥〕=〔索引〕(暫存槽(1))

### SL[47] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[48] kind=text, 現有引用=False

Form1.ComboBox2.ListIndex

### SL[49] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[50] kind=text, 現有引用=False

〔技能釋放〕=〔索引〕(暫存槽(1))

### SL[51] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[52] kind=text, 現有引用=False

Form1.ComboBox3.ListIndex

### SL[53] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[54] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[55] kind=text, 現有引用=False

〔按鍵快慢〕

### SL[56] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[57] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[58] kind=decoded-text, 現有引用=False

傳回值=暫存槽(1)

### SL[59] kind=text, 現有引用=False

〔天選〕

### SL[60] kind=text, 現有引用=False

暫存槽(1)=QMLibrary.GetGlobalVar("MMVerifyCode", 0)

### SL[61] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[62] kind=text, 現有引用=True

Set 新呼叫框架=New 框架類別_〔FORM1.INPUTBOX1.CHANGE〕::Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[63] kind=text, 現有引用=True

Form1.InputBox1.Text

### SL[64] kind=decoded-text, 現有引用=True

目前呼叫框架.暫存槽(1)=傳回值

### SL[65] kind=decoded-text, 現有引用=True

傳回值=目前呼叫框架.暫存槽(2)

### SL[66] kind=text, 現有引用=True

Form1.InputBox1.Text

### SL[67] kind=text, 現有引用=True

目前呼叫框架.暫存槽(2)=RIGHT(目前呼叫框架.暫存槽(1),1)

### SL[68] kind=text, 現有引用=True

傳回值=目前呼叫框架.函式回傳欄位:Set 新呼叫框架=目前呼叫框架:Set 目前呼叫框架=目前呼叫框架.上層呼叫框架:Set 新呼叫框架=Nothing

### SL[69] kind=text, 現有引用=False

Form1.InputBox1.Text

### SL[70] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[71] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[72] kind=text, 現有引用=False

GMS

### SL[73] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[74] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[75] kind=text, 現有引用=False

Form1.CheckBox4.Value

### SL[76] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[77] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[78] kind=text, 現有引用=False

GMS

### SL[79] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[80] kind=text, 現有引用=False

Sgn(暫存槽(2)=1)

### SL[81] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[82] kind=text, 現有引用=False

〔按G嗎〕

### SL[83] kind=text, 現有引用=False

暫存槽(3)=1

### SL[84] kind=text, 現有引用=False

GMS

### SL[85] kind=text, 現有引用=False

暫存槽(4)=傳回值

### SL[86] kind=text, 現有引用=False

Sgn(暫存槽(4)=2)

### SL[87] kind=text, 現有引用=False

傳回值=暫存槽(5)

### SL[88] kind=text, 現有引用=False

〔按G嗎〕

### SL[89] kind=text, 現有引用=False

暫存槽(5)=1

### SL[90] kind=text, 現有引用=False

GMS

### SL[91] kind=text, 現有引用=False

暫存槽(6)=傳回值

### SL[92] kind=text, 現有引用=False

Sgn(暫存槽(6)=3)

### SL[93] kind=text, 現有引用=False

傳回值=暫存槽(7)

### SL[94] kind=text, 現有引用=False

〔按G嗎〕

### SL[95] kind=text, 現有引用=False

暫存槽(7)=1

### SL[96] kind=text, 現有引用=False

GMS

### SL[97] kind=text, 現有引用=False

暫存槽(8)=傳回值

### SL[98] kind=text, 現有引用=False

Sgn(暫存槽(8)=4)

### SL[99] kind=text, 現有引用=False

傳回值=暫存槽(9)

### SL[100] kind=text, 現有引用=False

〔按G嗎〕

### SL[101] kind=text, 現有引用=False

暫存槽(9)=1

### SL[102] kind=text, 現有引用=False

GMS

### SL[103] kind=text, 現有引用=False

暫存槽(10)=傳回值

### SL[104] kind=text, 現有引用=False

Sgn(暫存槽(10)=5)

### SL[105] kind=text, 現有引用=False

傳回值=暫存槽(11)

### SL[106] kind=text, 現有引用=False

〔按G嗎〕

### SL[107] kind=text, 現有引用=False

暫存槽(11)=1

### SL[108] kind=text, 現有引用=False

GMS

### SL[109] kind=text, 現有引用=False

暫存槽(12)=傳回值

### SL[110] kind=text, 現有引用=False

Sgn(暫存槽(12)=6)

### SL[111] kind=text, 現有引用=False

傳回值=暫存槽(13)

### SL[112] kind=text, 現有引用=False

〔按G嗎〕

### SL[113] kind=text, 現有引用=False

暫存槽(13)=1

### SL[114] kind=text, 現有引用=False

GMS

### SL[115] kind=text, 現有引用=False

暫存槽(14)=傳回值

### SL[116] kind=text, 現有引用=False

Sgn(暫存槽(14)=7)

### SL[117] kind=text, 現有引用=False

傳回值=暫存槽(15)

### SL[118] kind=text, 現有引用=False

〔按G嗎〕

### SL[119] kind=text, 現有引用=False

暫存槽(15)=1

### SL[120] kind=text, 現有引用=False

GMS

### SL[121] kind=text, 現有引用=False

暫存槽(16)=傳回值

### SL[122] kind=text, 現有引用=False

Sgn(暫存槽(16)=8)

### SL[123] kind=text, 現有引用=False

傳回值=暫存槽(17)

### SL[124] kind=text, 現有引用=False

〔按G嗎〕

### SL[125] kind=text, 現有引用=False

暫存槽(17)=1

### SL[126] kind=text, 現有引用=False

GMS

### SL[127] kind=text, 現有引用=False

暫存槽(18)=傳回值

### SL[128] kind=text, 現有引用=False

Sgn(暫存槽(18)=9)

### SL[129] kind=text, 現有引用=False

傳回值=暫存槽(19)

### SL[130] kind=text, 現有引用=False

〔按G嗎〕

### SL[131] kind=text, 現有引用=False

暫存槽(19)=1

### SL[132] kind=text, 現有引用=False

傳回值=暫存槽(20)

### SL[133] kind=text, 現有引用=False

〔按G嗎〕

### SL[134] kind=text, 現有引用=False

暫存槽(20)=0

### SL[135] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[136] kind=text, 現有引用=False

Form1.CheckBox1.Value

### SL[137] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[138] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[139] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[140] kind=text, 現有引用=False

〔吃藥F1鍵〕

### SL[141] kind=text, 現有引用=False

暫存槽(2)=1

### SL[142] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[143] kind=text, 現有引用=False

〔吃藥F1鍵〕

### SL[144] kind=text, 現有引用=False

暫存槽(3)=0

### SL[145] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[146] kind=text, 現有引用=False

Form1.CheckBox2.Value

### SL[147] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[148] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[149] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[150] kind=text, 現有引用=False

〔吃藥1鍵〕

### SL[151] kind=text, 現有引用=False

暫存槽(2)=1

### SL[152] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[153] kind=text, 現有引用=False

〔吃藥1鍵〕

### SL[154] kind=text, 現有引用=False

暫存槽(3)=0

### SL[155] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[156] kind=text, 現有引用=False

Form1.CheckBox3.Value

### SL[157] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[158] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[159] kind=text, 現有引用=False

〔復活〕=1

### SL[160] kind=text, 現有引用=False

〔復活〕=0

### SL[161] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[162] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[163] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint((">>>>>>脚本启动"))

### SL[164] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[165] kind=text, 現有引用=False

Sgn((〔技能釋放〕=0))

### SL[166] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[167] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("使用Z技能"))

### SL[168] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔使用Z技能〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[169] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[170] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[171] kind=text, 現有引用=False

〔放技能ID〕

### SL[172] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[173] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[174] kind=text, 現有引用=False

Sgn((〔技能釋放〕=1))

### SL[175] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[176] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("不使用Z技能"))

### SL[177] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔不使用Z技能〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[178] kind=text, 現有引用=False

暫存槽(3)=傳回值

### SL[179] kind=text, 現有引用=False

傳回值=暫存槽(4)

### SL[180] kind=text, 現有引用=False

〔放技能ID〕

### SL[181] kind=text, 現有引用=False

暫存槽(4)=暫存槽(3)

### SL[182] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[183] kind=text, 現有引用=False

Sgn((〔技能釋放〕=2))

### SL[184] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[185] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("更多Z技能"))

### SL[186] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔更多Z技能〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[187] kind=text, 現有引用=False

暫存槽(5)=傳回值

### SL[188] kind=text, 現有引用=False

傳回值=暫存槽(6)

### SL[189] kind=text, 現有引用=False

〔放技能ID〕

### SL[190] kind=text, 現有引用=False

暫存槽(6)=暫存槽(5)

### SL[191] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[192] kind=text, 現有引用=False

Sgn((〔技能釋放〕=3))

### SL[193] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[194] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("使用X技能"))

### SL[195] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔使用X技能〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[196] kind=text, 現有引用=False

暫存槽(7)=傳回值

### SL[197] kind=text, 現有引用=False

傳回值=暫存槽(8)

### SL[198] kind=text, 現有引用=False

〔放技能ID〕

### SL[199] kind=text, 現有引用=False

暫存槽(8)=暫存槽(7)

### SL[200] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[201] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[202] kind=text, 現有引用=False

Sgn((〔吃藥〕=0))

### SL[203] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[204] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("啊不吃啊"))

### SL[205] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔啊不吃啊〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[206] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[207] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[208] kind=text, 現有引用=False

〔吃藥ID〕

### SL[209] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[210] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[211] kind=text, 現有引用=False

Sgn((〔吃藥〕=1))

### SL[212] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[213] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("吃药11%"))

### SL[214] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔吃藥11〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[215] kind=text, 現有引用=False

暫存槽(3)=傳回值

### SL[216] kind=text, 現有引用=False

傳回值=暫存槽(4)

### SL[217] kind=text, 現有引用=False

〔吃藥ID〕

### SL[218] kind=text, 現有引用=False

暫存槽(4)=暫存槽(3)

### SL[219] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[220] kind=text, 現有引用=False

Sgn((〔吃藥〕=2))

### SL[221] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[222] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("吃药40%"))

### SL[223] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔吃藥40〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[224] kind=text, 現有引用=False

暫存槽(5)=傳回值

### SL[225] kind=text, 現有引用=False

傳回值=暫存槽(6)

### SL[226] kind=text, 現有引用=False

〔吃藥ID〕

### SL[227] kind=text, 現有引用=False

暫存槽(6)=暫存槽(5)

### SL[228] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[229] kind=text, 現有引用=False

Sgn((〔吃藥〕=3))

### SL[230] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[231] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("吃药70%"))

### SL[232] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔吃藥70〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[233] kind=text, 現有引用=False

暫存槽(7)=傳回值

### SL[234] kind=text, 現有引用=False

傳回值=暫存槽(8)

### SL[235] kind=text, 現有引用=False

〔吃藥ID〕

### SL[236] kind=text, 現有引用=False

暫存槽(8)=暫存槽(7)

### SL[237] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[238] kind=text, 現有引用=False

Sgn((〔吃藥〕=4))

### SL[239] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[240] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("吃药6%"))

### SL[241] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔吃藥6〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[242] kind=text, 現有引用=False

暫存槽(9)=傳回值

### SL[243] kind=text, 現有引用=False

傳回值=暫存槽(10)

### SL[244] kind=text, 現有引用=False

〔吃藥ID〕

### SL[245] kind=text, 現有引用=False

暫存槽(10)=暫存槽(9)

### SL[246] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[247] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[248] kind=text, 現有引用=False

Sgn((〔復活〕=1))

### SL[249] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[250] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("监控死亡"))

### SL[251] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔監控死亡〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[252] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[253] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[254] kind=text, 現有引用=False

〔監控死亡ID〕

### SL[255] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[256] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[257] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[258] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[259] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[260] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(2000)

### SL[261] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(3000)

### SL[262] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(4000)

### SL[263] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(5000)

### SL[264] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(6000)

