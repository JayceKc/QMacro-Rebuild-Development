# 07 魔方：缺失初始化線索

這是線索清單，尚未將未引用字串當作原始指令。
SL 截止點只供閱讀；它不是函式入口或完整缺失來源的界線。編譯器可能把右側表達式配置在截止點之後。

## 保留的位置群組

L00000..L00030 loc=0 flags=0 count=31 ops=30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,29
L00031..L00031 loc=1 flags=0 count=1 ops=255
L00032..L00032 loc=2 flags=0 count=1 ops=255
L00033..L00033 loc=3 flags=0 count=1 ops=255
L00034..L00034 loc=7 flags=0 count=1 ops=255
L00035..L00035 loc=8 flags=0 count=1 ops=255
L00036..L00036 loc=9 flags=0 count=1 ops=255
L00037..L00037 loc=11 flags=0 count=1 ops=255
L00038..L00038 loc=12 flags=0 count=1 ops=255
L00039..L00039 loc=13 flags=0 count=1 ops=255
L00040..L00040 loc=14 flags=0 count=1 ops=255
L00041..L00041 loc=15 flags=0 count=1 ops=255
L00042..L00042 loc=17 flags=0 count=1 ops=255
L00043..L00043 loc=18 flags=0 count=1 ops=255
L00044..L00044 loc=20 flags=0 count=1 ops=255
L00045..L00045 loc=21 flags=0 count=1 ops=255
L00046..L00046 loc=22 flags=0 count=1 ops=255
L00047..L00047 loc=23 flags=0 count=1 ops=255
L00048..L00049 loc=25 flags=0 count=2 ops=255,255
L00050..L00050 loc=26 flags=0 count=1 ops=255
L00051..L00051 loc=27 flags=0 count=1 ops=255
L00052..L00052 loc=28 flags=0 count=1 ops=255
L00053..L00053 loc=30 flags=0 count=1 ops=255
L00054..L00054 loc=31 flags=0 count=1 ops=255
L00055..L00055 loc=32 flags=0 count=1 ops=255
L00056..L00056 loc=33 flags=0 count=1 ops=255
L00057..L00057 loc=34 flags=0 count=1 ops=255
L00058..L00058 loc=35 flags=0 count=1 ops=255
L00059..L00059 loc=36 flags=0 count=1 ops=255
L00060..L00060 loc=37 flags=0 count=1 ops=255
L00061..L00063 loc=38 flags=0 count=3 ops=255,255,255
L00064..L00064 loc=39 flags=0 count=1 ops=255
L00065..L00067 loc=40 flags=0 count=3 ops=255,255,255
L00068..L00068 loc=41 flags=0 count=1 ops=255
L00069..L00073 loc=42 flags=0 count=5 ops=255,255,255,255,255
L00074..L00074 loc=43 flags=0 count=1 ops=255
L00075..L00079 loc=44 flags=0 count=5 ops=255,255,255,255,255
L00080..L00080 loc=45 flags=0 count=1 ops=255
L00081..L00085 loc=46 flags=0 count=5 ops=255,255,255,255,255
L00086..L00086 loc=47 flags=0 count=1 ops=255
L00087..L00091 loc=48 flags=0 count=5 ops=255,255,255,255,255
L00092..L00092 loc=49 flags=0 count=1 ops=255
L00093..L00097 loc=50 flags=0 count=5 ops=255,255,255,255,255
L00098..L00098 loc=51 flags=0 count=1 ops=255
L00099..L00103 loc=52 flags=0 count=5 ops=255,255,255,255,255
L00104..L00104 loc=53 flags=0 count=1 ops=255
L00105..L00107 loc=54 flags=0 count=3 ops=255,255,255
L00108..L00108 loc=55 flags=0 count=1 ops=255
L00109..L00113 loc=56 flags=0 count=5 ops=255,255,255,255,255
L00114..L00114 loc=57 flags=0 count=1 ops=255
L00115..L00117 loc=58 flags=0 count=3 ops=255,255,255
L00118..L00118 loc=62 flags=0 count=1 ops=255
L00119..L00119 loc=63 flags=0 count=1 ops=255
L00120..L00123 loc=64 flags=0 count=4 ops=255,255,255,255
L00124..L00125 loc=65 flags=0 count=2 ops=255,255
L00126..L00126 loc=66 flags=0 count=1 ops=255
L00127..L00127 loc=67 flags=0 count=1 ops=255
L00128..L00128 loc=68 flags=0 count=1 ops=255
L00129..L00129 loc=69 flags=0 count=1 ops=255
L00130..L00130 loc=70 flags=0 count=1 ops=255
L00131..L00131 loc=71 flags=0 count=1 ops=255
L00132..L00132 loc=73 flags=0 count=1 ops=255
L00133..L00136 loc=74 flags=0 count=4 ops=255,255,255,255
L00137..L00137 loc=75 flags=0 count=1 ops=255
L00138..L00138 loc=76 flags=0 count=1 ops=255
L00139..L00140 loc=77 flags=0 count=2 ops=255,255
L00141..L00141 loc=78 flags=0 count=1 ops=255
L00142..L00142 loc=79 flags=0 count=1 ops=255
L00143..L00143 loc=80 flags=0 count=1 ops=255
L00144..L00144 loc=81 flags=0 count=1 ops=255
L00145..L00145 loc=82 flags=0 count=1 ops=255
L00146..L00146 loc=83 flags=0 count=1 ops=255
L00147..L00147 loc=85 flags=0 count=1 ops=255
L00148..L00151 loc=86 flags=0 count=4 ops=255,255,255,255
L00152..L00154 loc=87 flags=0 count=3 ops=255,255,255
L00155..L00155 loc=88 flags=0 count=1 ops=255
L00156..L00158 loc=89 flags=0 count=3 ops=255,255,255
L00159..L00159 loc=91 flags=0 count=1 ops=255
L00160..L00163 loc=92 flags=0 count=4 ops=255,255,255,255
L00164..L00166 loc=93 flags=0 count=3 ops=255,255,255
L00167..L00167 loc=94 flags=0 count=1 ops=255
L00168..L00170 loc=95 flags=0 count=3 ops=255,255,255
L00171..L00171 loc=97 flags=0 count=1 ops=255
L00172..L00175 loc=98 flags=0 count=4 ops=255,255,255,255
L00176..L00178 loc=99 flags=0 count=3 ops=255,255,255
L00179..L00179 loc=100 flags=0 count=1 ops=255
L00180..L00182 loc=101 flags=0 count=3 ops=255,255,255
L00183..L00183 loc=103 flags=0 count=1 ops=255
L00184..L00187 loc=104 flags=0 count=4 ops=255,255,255,255
L00188..L00190 loc=105 flags=0 count=3 ops=255,255,255
L00191..L00191 loc=106 flags=0 count=1 ops=255
L00192..L00194 loc=107 flags=0 count=3 ops=255,255,255
L00195..L00195 loc=109 flags=0 count=1 ops=255
L00196..L00198 loc=110 flags=0 count=3 ops=255,255,255
L00199..L00201 loc=111 flags=0 count=3 ops=255,255,255
L00202..L00202 loc=112 flags=0 count=1 ops=255
L00203..L00205 loc=113 flags=0 count=3 ops=255,255,255
L00206..L00208 loc=114 flags=0 count=3 ops=255,255,255
L00209..L00211 loc=115 flags=0 count=3 ops=255,255,255
L00212..L00212 loc=116 flags=0 count=1 ops=255
L00213..L00218 loc=117 flags=0 count=6 ops=255,255,255,255,255,255
L00219..L00219 loc=118 flags=0 count=1 ops=255
L00220..L00220 loc=119 flags=0 count=1 ops=255
L00221..L00221 loc=121 flags=0 count=1 ops=255
L00222..L00227 loc=122 flags=0 count=6 ops=255,255,255,255,255,255
L00228..L00228 loc=123 flags=0 count=1 ops=255
L00229..L00229 loc=124 flags=0 count=1 ops=255
L00230..L00230 loc=126 flags=0 count=1 ops=255
L00231..L00236 loc=127 flags=0 count=6 ops=255,255,255,255,255,255
L00237..L00237 loc=128 flags=0 count=1 ops=255
L00238..L00242 loc=129 flags=0 count=5 ops=255,255,255,255,255
L00243..L00243 loc=131 flags=0 count=1 ops=255
L00244..L00249 loc=132 flags=0 count=6 ops=255,255,255,255,255,255
L00250..L00250 loc=133 flags=0 count=1 ops=255
L00251..L00253 loc=134 flags=0 count=3 ops=255,255,255
L00254..L00254 loc=136 flags=0 count=1 ops=255
L00255..L00258 loc=137 flags=0 count=4 ops=255,255,255,255
L00259..L00259 loc=138 flags=0 count=1 ops=255
L00260..L00262 loc=139 flags=0 count=3 ops=255,255,255
L00263..L00265 loc=140 flags=0 count=3 ops=255,255,255
L00266..L00269 loc=141 flags=0 count=4 ops=255,255,255,255
L00270..L00270 loc=142 flags=0 count=1 ops=255
L00271..L00273 loc=143 flags=0 count=3 ops=255,255,255
L00274..L00274 loc=144 flags=0 count=1 ops=255
L00275..L00275 loc=146 flags=0 count=1 ops=255
L00276..L00278 loc=147 flags=0 count=3 ops=255,255,255
L00279..L00279 loc=149 flags=0 count=1 ops=255
L00280..L00280 loc=153 flags=0 count=1 ops=255
L00281..L00283 loc=154 flags=0 count=3 ops=255,255,255
L00284..L00286 loc=155 flags=0 count=3 ops=255,255,255
L00287..L00289 loc=156 flags=0 count=3 ops=255,255,255
L00290..L00290 loc=157 flags=0 count=1 ops=255
L00291..L00291 loc=158 flags=0 count=1 ops=255
L00292..L00292 loc=159 flags=0 count=1 ops=255
L00293..L00293 loc=160 flags=0 count=1 ops=255
L00294..L00294 loc=161 flags=0 count=1 ops=255
L00295..L00295 loc=162 flags=0 count=1 ops=255
L00296..L00296 loc=163 flags=0 count=1 ops=255
L00297..L00297 loc=164 flags=0 count=1 ops=255
L00298..L00298 loc=165 flags=0 count=1 ops=255
L00299..L00299 loc=166 flags=0 count=1 ops=255
L00300..L00300 loc=167 flags=0 count=1 ops=255
L00301..L00302 loc=168 flags=0 count=2 ops=255,255
L00303..L00303 loc=169 flags=0 count=1 ops=255
L00304..L00306 loc=171 flags=0 count=3 ops=255,255,255
L00307..L00308 loc=172 flags=0 count=2 ops=255,255
L00309..L00309 loc=173 flags=0 count=1 ops=255
L00310..L00310 loc=174 flags=0 count=1 ops=255
L00311..L00311 loc=175 flags=0 count=1 ops=255
L00312..L00312 loc=177 flags=0 count=1 ops=255
L00313..L00316 loc=178 flags=0 count=4 ops=255,255,255,255
L00317..L00317 loc=179 flags=0 count=1 ops=255
L00318..L00321 loc=180 flags=0 count=4 ops=255,255,255,255
L00322..L00322 loc=181 flags=0 count=1 ops=255
L00323..L00325 loc=182 flags=0 count=3 ops=255,255,255
L00326..L00327 loc=183 flags=0 count=2 ops=255,255
L00328..L00331 loc=184 flags=0 count=4 ops=255,255,255,255
L00332..L00332 loc=185 flags=0 count=1 ops=255
L00333..L00335 loc=186 flags=0 count=3 ops=255,255,255
L00336..L00336 loc=187 flags=0 count=1 ops=255
L00337..L00337 loc=192 flags=0 count=1 ops=255
L00338..L00341 loc=193 flags=0 count=4 ops=255,255,255,255
L00342..L00342 loc=194 flags=0 count=1 ops=255
L00343..L00351 loc=195 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00352..L00353 loc=196 flags=0 count=2 ops=255,255
L00354..L00357 loc=197 flags=0 count=4 ops=255,255,255,255
L00358..L00358 loc=198 flags=0 count=1 ops=255
L00359..L00367 loc=199 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00368..L00369 loc=200 flags=0 count=2 ops=255,255
L00370..L00373 loc=201 flags=0 count=4 ops=255,255,255,255
L00374..L00374 loc=202 flags=0 count=1 ops=255
L00375..L00383 loc=203 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00384..L00385 loc=204 flags=0 count=2 ops=255,255
L00386..L00389 loc=205 flags=0 count=4 ops=255,255,255,255
L00390..L00390 loc=206 flags=0 count=1 ops=255
L00391..L00399 loc=207 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00400..L00400 loc=208 flags=0 count=1 ops=255
L00401..L00401 loc=210 flags=0 count=1 ops=255
L00402..L00403 loc=211 flags=0 count=2 ops=255,255
L00404..L00404 loc=212 flags=0 count=1 ops=255
L00405..L00413 loc=213 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00414..L00415 loc=214 flags=0 count=2 ops=255,255
L00416..L00417 loc=215 flags=0 count=2 ops=255,255
L00418..L00418 loc=216 flags=0 count=1 ops=255
L00419..L00427 loc=217 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00428..L00429 loc=218 flags=0 count=2 ops=255,255
L00430..L00431 loc=219 flags=0 count=2 ops=255,255
L00432..L00432 loc=220 flags=0 count=1 ops=255
L00433..L00441 loc=221 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00442..L00442 loc=222 flags=0 count=1 ops=255
L00443..L00443 loc=223 flags=0 count=1 ops=255
L00444..L00444 loc=224 flags=0 count=1 ops=255
L00445..L00445 loc=226 flags=0 count=1 ops=255
L00446..L00448 loc=227 flags=0 count=3 ops=255,255,255
L00449..L00449 loc=228 flags=0 count=1 ops=255
L00450..L00450 loc=230 flags=0 count=1 ops=255
L00451..L00452 loc=231 flags=0 count=2 ops=255,255
L00453..L00453 loc=232 flags=0 count=1 ops=255
L00454..L00456 loc=234 flags=0 count=3 ops=255,255,255
L00457..L00458 loc=235 flags=0 count=2 ops=255,255
L00459..L00459 loc=236 flags=0 count=1 ops=255
L00460..L00460 loc=238 flags=0 count=1 ops=255
L00461..L00462 loc=239 flags=0 count=2 ops=255,255
L00463..L00463 loc=241 flags=0 count=1 ops=255
L00464..L00464 loc=243 flags=0 count=1 ops=255
L00465..L00466 loc=244 flags=0 count=2 ops=255,255
L00467..L00467 loc=246 flags=0 count=1 ops=255
L00468..L00468 loc=247 flags=0 count=1 ops=255
L00469..L00469 loc=248 flags=0 count=1 ops=255
L00470..L00470 loc=249 flags=0 count=1 ops=255
L00471..L00471 loc=250 flags=0 count=1 ops=255
L00472..L00472 loc=251 flags=0 count=1 ops=255
L00473..L00473 loc=252 flags=0 count=1 ops=255
L00474..L00474 loc=253 flags=0 count=1 ops=255
L00475..L00475 loc=254 flags=0 count=1 ops=255
L00476..L00476 loc=255 flags=0 count=1 ops=255
L00477..L00477 loc=256 flags=0 count=1 ops=255
L00478..L00478 loc=257 flags=0 count=1 ops=255
L00479..L00479 loc=258 flags=0 count=1 ops=255
L00480..L00480 loc=259 flags=0 count=1 ops=255
L00481..L00481 loc=268 flags=0 count=1 ops=255
L00482..L00484 loc=269 flags=0 count=3 ops=255,255,255
L00485..L00485 loc=270 flags=0 count=1 ops=255
L00486..L00486 loc=271 flags=0 count=1 ops=255
L00487..L00488 loc=272 flags=0 count=2 ops=255,255
L00489..L00489 loc=273 flags=0 count=1 ops=255
L00490..L00492 loc=274 flags=0 count=3 ops=255,255,255
L00493..L00493 loc=275 flags=0 count=1 ops=255
L00494..L00494 loc=276 flags=0 count=1 ops=255
L00495..L00495 loc=277 flags=0 count=1 ops=255
L00496..L00496 loc=278 flags=0 count=1 ops=255
L00497..L00498 loc=279 flags=0 count=2 ops=255,255
L00499..L00499 loc=280 flags=0 count=1 ops=255
L00500..L00502 loc=281 flags=0 count=3 ops=255,255,255
L00503..L00503 loc=282 flags=0 count=1 ops=255
L00504..L00504 loc=285 flags=0 count=1 ops=255
L00505..L00505 loc=287 flags=0 count=1 ops=255
L00506..L00508 loc=288 flags=0 count=3 ops=255,255,255
L00509..L00509 loc=289 flags=0 count=1 ops=255
L00510..L00513 loc=290 flags=0 count=4 ops=255,255,255,255
L00514..L00514 loc=291 flags=0 count=1 ops=255
L00515..L00522 loc=292 flags=0 count=8 ops=255,255,255,255,255,255,255,255
L00523..L00523 loc=293 flags=0 count=1 ops=255
L00524..L00530 loc=294 flags=0 count=7 ops=255,255,255,255,255,255,255

## 原 SL 字串順序

### SL[0] kind=decoded-text, 現有引用=True

Dim 暫存槽(256):Dim 目前呼叫框架,新呼叫框架:Set 目前呼叫框架=Nothing:Set 新呼叫框架=Nothing

### SL[1] kind=decoded-text, 現有引用=True

Class 框架類別_〔啊不吃啊〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[2] kind=decoded-text, 現有引用=True

Class 框架類別_〔更多Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[3] kind=decoded-text, 現有引用=True

Class 框架類別_〔普攻〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[4] kind=decoded-text, 現有引用=True

Class 框架類別_〔找按鈕〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[5] kind=decoded-text, 現有引用=True

Class 框架類別_〔中間過圖〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[6] kind=decoded-text, 現有引用=True

Class 框架類別_〔找怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[7] kind=decoded-text, 現有引用=True

Class 框架類別_〔不跟隨找怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[8] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能三〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[9] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能四〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[10] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能一〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[11] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥11〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[12] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能二〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[13] kind=decoded-text, 現有引用=True

Class 框架類別_〔檢查新舊ALTQ〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[14] kind=decoded-text, 現有引用=True

Class 框架類別_〔完成后的操作〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[15] kind=decoded-text, 現有引用=True

Class 框架類別_〔檢查技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[16] kind=decoded-text, 現有引用=True

Class 框架類別_〔全局找圖〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[17] kind=decoded-text, 現有引用=True

Class 框架類別_〔四分鐘一次表情〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[18] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥40〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[19] kind=decoded-text, 現有引用=True

Class 框架類別_〔換角色〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[20] kind=decoded-text, 現有引用=True

Class 框架類別_〔不使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[21] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥6〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[22] kind=decoded-text, 現有引用=True

Class 框架類別_〔三分鐘一次表情〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[23] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用X技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[24] kind=decoded-text, 現有引用=True

Class 框架類別_〔第一次打怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[25] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥70〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[26] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[27] kind=decoded-text, 現有引用=True

Class 框架類別_〔二分鐘一次表情〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[28] kind=decoded-text, 現有引用=True

Class 框架類別_〔接周任務〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[29] kind=decoded-text, 現有引用=True

Class 框架類別_〔點確定〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[30] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[31] kind=decoded-text, 現有引用=False

Call QMLibrary.OpenLog("C:\方舟混沌\新魔方.log")

### SL[32] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[33] kind=text, 現有引用=False

SET WS=CREATEOBJECT("Wscript.Shell")

### SL[34] kind=decoded-text, 現有引用=False

Call WS.RUN("regsvr32 atl.dll /s")

### SL[35] kind=text, 現有引用=False

SET WS=nothing

### SL[36] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[37] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro\fz","fz.dll")

### SL[38] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","fzreg.dll")

### SL[39] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","*.bmp")

### SL[40] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[41] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(QMLibrary.CallAPI2("C:\users\mymacro\fzreg.dll", "SetDllPathW", "C:\users\mymacro\fz\fz.dll", 0))

### SL[42] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[43] kind=text, 現有引用=False

SET DM=CREATEOBJECT("dm.dmsoft")

### SL[44] kind=decoded-text, 現有引用=False

Call DM.SETSHOWERRORMSG(0)

### SL[45] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[46] kind=decoded-text, 現有引用=False

〔版本〕=DM.VER()

### SL[47] kind=text, 現有引用=False

Sgn((〔版本〕=7.2450))

### SL[48] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("成功"))

### SL[49] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("失败"))

### SL[50] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[51] kind=decoded-text, 現有引用=False

〔鼠標〕=DM.ENABLEREALMOUSE(2,10,60)

### SL[52] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("鼠标" & 〔鼠標〕)

### SL[53] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[54] kind=empty, 現有引用=False



### SL[55] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[56] kind=text, 現有引用=False

〔索引〕=ARRAY(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30)

### SL[57] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[58] kind=text, 現有引用=False

Form1.ComboBox1.ListIndex

### SL[59] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[60] kind=text, 現有引用=False

〔表情〕=〔索引〕(暫存槽(1))

### SL[61] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[62] kind=text, 現有引用=False

Form1.ComboBox2.ListIndex

### SL[63] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[64] kind=text, 現有引用=False

〔技能釋放〕=〔索引〕(暫存槽(1))

### SL[65] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[66] kind=text, 現有引用=False

Form1.ComboBox3.ListIndex

### SL[67] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[68] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[69] kind=text, 現有引用=False

〔周常〕

### SL[70] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[71] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[72] kind=text, 現有引用=False

Form1.ComboBox4.ListIndex

### SL[73] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[74] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[75] kind=text, 現有引用=False

〔難度〕

### SL[76] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[77] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[78] kind=text, 現有引用=False

Form1.ComboBox5.ListIndex

### SL[79] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[80] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[81] kind=text, 現有引用=False

〔刷幾次〕

### SL[82] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[83] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[84] kind=text, 現有引用=False

Form1.ComboBox6.ListIndex

### SL[85] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[86] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[87] kind=text, 現有引用=False

〔角色開始〕

### SL[88] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[89] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[90] kind=text, 現有引用=False

Form1.ComboBox7.ListIndex

### SL[91] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[92] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[93] kind=text, 現有引用=False

〔角色結束〕

### SL[94] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[95] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[96] kind=text, 現有引用=False

Form1.ComboBox8.ListIndex

### SL[97] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[98] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[99] kind=text, 現有引用=False

〔完成之后〕

### SL[100] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[101] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[102] kind=text, 現有引用=False

Form1.ComboBox9.ListIndex

### SL[103] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[104] kind=text, 現有引用=False

〔吃藥〕=〔索引〕(暫存槽(1))

### SL[105] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[106] kind=text, 現有引用=False

Form1.ComboBox99.ListIndex

### SL[107] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[108] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[109] kind=text, 現有引用=False

〔是否組隊〕

### SL[110] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[111] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[112] kind=decoded-text, 現有引用=False

傳回值=暫存槽(1)

### SL[113] kind=text, 現有引用=False

〔天選〕

### SL[114] kind=text, 現有引用=False

暫存槽(1)=QMLibrary.GetGlobalVar("MMVerifyCode", 0)

### SL[115] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[116] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[117] kind=text, 現有引用=False

〔天選〕

### SL[118] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[119] kind=text, 現有引用=False

Sgn(暫存槽(1)="")

### SL[120] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[121] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[122] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((2000))

### SL[123] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[124] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((4000))

### SL[125] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((5000))

### SL[126] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[127] kind=text, 現有引用=False

〔天選〕

### SL[128] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[129] kind=text, 現有引用=False

Sgn(暫存槽(1)="4AD733")

### SL[130] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[131] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[132] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[133] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((2000))

### SL[134] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[135] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((4000))

### SL[136] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((5000))

### SL[137] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[138] kind=text, 現有引用=False

Form1.CheckBox1.Value

### SL[139] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[140] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[141] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[142] kind=text, 現有引用=False

〔使用覺醒〕

### SL[143] kind=text, 現有引用=False

暫存槽(2)=1

### SL[144] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[145] kind=text, 現有引用=False

〔使用覺醒〕

### SL[146] kind=text, 現有引用=False

暫存槽(3)=0

### SL[147] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[148] kind=text, 現有引用=False

Form1.CheckBox2.Value

### SL[149] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[150] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[151] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[152] kind=text, 現有引用=False

〔賣萌〕

### SL[153] kind=text, 現有引用=False

暫存槽(2)=1

### SL[154] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[155] kind=text, 現有引用=False

〔賣萌〕

### SL[156] kind=text, 現有引用=False

暫存槽(3)=0

### SL[157] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[158] kind=text, 現有引用=False

Form1.CheckBox3.Value

### SL[159] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[160] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[161] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[162] kind=text, 現有引用=False

〔找頭背〕

### SL[163] kind=text, 現有引用=False

暫存槽(2)=1

### SL[164] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[165] kind=text, 現有引用=False

〔找頭背〕

### SL[166] kind=text, 現有引用=False

暫存槽(3)=0

### SL[167] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[168] kind=text, 現有引用=False

Form1.CheckBox4.Value

### SL[169] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[170] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[171] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[172] kind=text, 現有引用=False

〔公會任務〕

### SL[173] kind=text, 現有引用=False

暫存槽(2)=1

### SL[174] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[175] kind=text, 現有引用=False

〔公會任務〕

### SL[176] kind=text, 現有引用=False

暫存槽(3)=0

### SL[177] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[178] kind=text, 現有引用=False

傳回值=暫存槽(1)

### SL[179] kind=text, 現有引用=False

〔完成次數〕

### SL[180] kind=text, 現有引用=False

暫存槽(1)=0

### SL[181] kind=text, 現有引用=False

傳回值=暫存槽(1)

### SL[182] kind=text, 現有引用=False

〔通關次數〕

### SL[183] kind=text, 現有引用=False

暫存槽(1)=0

### SL[184] kind=text, 現有引用=False

〔需要退出〕=0

### SL[185] kind=text, 現有引用=False

傳回值=暫存槽(1)

### SL[186] kind=text, 現有引用=False

〔層數〕

### SL[187] kind=text, 現有引用=False

暫存槽(1)=0

### SL[188] kind=text, 現有引用=False

傳回值=暫存槽(1)

### SL[189] kind=text, 現有引用=False

〔幸運怪〕

### SL[190] kind=text, 現有引用=False

暫存槽(1)=0

### SL[191] kind=text, 現有引用=False

傳回值=暫存槽(1)

### SL[192] kind=text, 現有引用=False

〔進圖走位〕

### SL[193] kind=text, 現有引用=False

暫存槽(1)=0

### SL[194] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[195] kind=text, 現有引用=False

〔角色結束〕

### SL[196] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[197] kind=text, 現有引用=False

〔角色開始〕

### SL[198] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[199] kind=text, 現有引用=False

Sgn(暫存槽(2)>0 and 暫存槽(1)=0)

### SL[200] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[201] kind=decoded-text, 現有引用=False

Call QMLibrary.ExitScript(0)

### SL[202] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[203] kind=text, 現有引用=False

〔角色結束〕

### SL[204] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[205] kind=text, 現有引用=False

〔角色開始〕

### SL[206] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[207] kind=text, 現有引用=False

Sgn(暫存槽(2)=0 and 暫存槽(1)>0)

### SL[208] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[209] kind=decoded-text, 現有引用=False

Call QMLibrary.ExitScript(0)

### SL[210] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[211] kind=text, 現有引用=False

〔角色結束〕

### SL[212] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[213] kind=text, 現有引用=False

〔角色開始〕

### SL[214] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[215] kind=text, 現有引用=False

Sgn(暫存槽(2)>0 and 暫存槽(1)>0)

### SL[216] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[217] kind=text, 現有引用=False

〔角色開始〕

### SL[218] kind=text, 現有引用=False

暫存槽(3)=傳回值

### SL[219] kind=text, 現有引用=False

傳回值=暫存槽(4)

### SL[220] kind=text, 現有引用=False

〔要切角色〕

### SL[221] kind=text, 現有引用=False

暫存槽(4)=暫存槽(3)

### SL[222] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[223] kind=text, 現有引用=False

〔角色結束〕

### SL[224] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[225] kind=text, 現有引用=False

〔角色開始〕

### SL[226] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[227] kind=text, 現有引用=False

Sgn(暫存槽(2)=0 or 暫存槽(1)=0)

### SL[228] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[229] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[230] kind=text, 現有引用=False

〔角色開始〕

### SL[231] kind=text, 現有引用=False

暫存槽(3)=0

### SL[232] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[233] kind=text, 現有引用=False

〔是否組隊〕

### SL[234] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[235] kind=text, 現有引用=False

Sgn(暫存槽(1)=4)

### SL[236] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[237] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[238] kind=text, 現有引用=False

〔是否組隊〕

### SL[239] kind=text, 現有引用=False

暫存槽(2)=2

### SL[240] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[241] kind=text, 現有引用=False

〔只打一關〕

### SL[242] kind=text, 現有引用=False

暫存槽(3)=1

### SL[243] kind=text, 現有引用=False

〔周常〕

### SL[244] kind=text, 現有引用=False

暫存槽(4)=傳回值

### SL[245] kind=text, 現有引用=False

Sgn(暫存槽(4)=0)

### SL[246] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[247] kind=text, 現有引用=False

傳回值=暫存槽(5)

### SL[248] kind=text, 現有引用=False

〔周常〕

### SL[249] kind=text, 現有引用=False

暫存槽(5)=1

### SL[250] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[251] kind=text, 現有引用=False

傳回值=暫存槽(6)

### SL[252] kind=text, 現有引用=False

〔只打一關〕

### SL[253] kind=text, 現有引用=False

暫存槽(6)=0

### SL[254] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[255] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint((">>>>>>脚本启动"))

### SL[256] kind=text, 現有引用=False

〔角色開始〕

### SL[257] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[258] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("角色开始" & 暫存槽(1))

### SL[259] kind=text, 現有引用=False

〔角色結束〕

### SL[260] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[261] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("角色结束" & 暫存槽(1))

### SL[262] kind=text, 現有引用=False

〔要切角色〕

### SL[263] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[264] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("要切开始" & 暫存槽(1))

### SL[265] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[266] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[267] kind=text, 現有引用=False

Randomize

### SL[268] kind=text, 現有引用=False

YDX=INT(5*RND+35)

### SL[269] kind=text, 現有引用=False

Randomize

### SL[270] kind=text, 現有引用=False

YDY=INT(10*RND+10)

### SL[271] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[272] kind=decoded-text, 現有引用=False

Call DM.MOVETO(YDX,YDY)

### SL[273] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[274] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[275] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[276] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[277] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[278] kind=text, 現有引用=False

〔天選〕

### SL[279] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[280] kind=text, 現有引用=False

DM_RET=DM.FINDCOLOR(160,1,260,25,暫存槽(1) & "-151515",0.9,0,INTX,INTY)

### SL[281] kind=text, 現有引用=False

Sgn((INTX>=0))

### SL[282] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[283] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[284] kind=text, 現有引用=False

〔角色開始〕

### SL[285] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[286] kind=text, 現有引用=False

Sgn(暫存槽(1)>0)

### SL[287] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[288] kind=text, 現有引用=False

〔是否組隊〕

### SL[289] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[290] kind=text, 現有引用=False

Sgn(暫存槽(2)=0)

### SL[291] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[292] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔換角色〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[293] kind=text, 現有引用=False

暫存槽(3)=傳回值

### SL[294] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[295] kind=text, 現有引用=False

〔是否組隊〕

### SL[296] kind=text, 現有引用=False

暫存槽(4)=傳回值

### SL[297] kind=text, 現有引用=False

Sgn(暫存槽(4)=2)

### SL[298] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[299] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔換角色〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[300] kind=text, 現有引用=False

暫存槽(5)=傳回值

### SL[301] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[302] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[303] kind=text, 現有引用=False

〔是否組隊〕

### SL[304] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[305] kind=text, 現有引用=False

Sgn(暫存槽(1)=0)

### SL[306] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[307] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔全局找圖〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[308] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[309] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[310] kind=text, 現有引用=False

〔全局找圖ID〕

### SL[311] kind=text, 現有引用=False

暫存槽(3)=暫存槽(2)

### SL[312] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[313] kind=text, 現有引用=False

〔是否組隊〕

### SL[314] kind=text, 現有引用=False

暫存槽(4)=傳回值

### SL[315] kind=text, 現有引用=False

Sgn(暫存槽(4)=2)

### SL[316] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[317] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔全局找圖〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[318] kind=text, 現有引用=False

暫存槽(5)=傳回值

### SL[319] kind=text, 現有引用=False

傳回值=暫存槽(6)

### SL[320] kind=text, 現有引用=False

〔全局找圖ID〕

### SL[321] kind=text, 現有引用=False

暫存槽(6)=暫存槽(5)

### SL[322] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[323] kind=text, 現有引用=False

〔是否組隊〕

### SL[324] kind=text, 現有引用=False

暫存槽(7)=傳回值

### SL[325] kind=text, 現有引用=False

Sgn(暫存槽(7)=1)

### SL[326] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[327] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔點確定〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[328] kind=text, 現有引用=False

暫存槽(8)=傳回值

### SL[329] kind=text, 現有引用=False

傳回值=暫存槽(9)

### SL[330] kind=text, 現有引用=False

〔點確定ID〕

### SL[331] kind=text, 現有引用=False

暫存槽(9)=暫存槽(8)

### SL[332] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[333] kind=text, 現有引用=False

〔是否組隊〕

### SL[334] kind=text, 現有引用=False

暫存槽(10)=傳回值

### SL[335] kind=text, 現有引用=False

Sgn(暫存槽(10)=3)

### SL[336] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[337] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔點確定〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[338] kind=text, 現有引用=False

暫存槽(11)=傳回值

### SL[339] kind=text, 現有引用=False

傳回值=暫存槽(12)

### SL[340] kind=text, 現有引用=False

〔點確定ID〕

### SL[341] kind=text, 現有引用=False

暫存槽(12)=暫存槽(11)

### SL[342] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[343] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[344] kind=text, 現有引用=False

Sgn(〔表情〕=1)

### SL[345] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[346] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔二分鐘一次表情〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[347] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[348] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[349] kind=text, 現有引用=False

〔表情ID〕

### SL[350] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[351] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[352] kind=text, 現有引用=False

Sgn(〔表情〕=2)

### SL[353] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[354] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔三分鐘一次表情〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[355] kind=text, 現有引用=False

暫存槽(3)=傳回值

### SL[356] kind=text, 現有引用=False

傳回值=暫存槽(4)

### SL[357] kind=text, 現有引用=False

〔表情ID〕

### SL[358] kind=text, 現有引用=False

暫存槽(4)=暫存槽(3)

### SL[359] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[360] kind=text, 現有引用=False

Sgn(〔表情〕=3)

### SL[361] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[362] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔四分鐘一次表情〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[363] kind=text, 現有引用=False

暫存槽(5)=傳回值

### SL[364] kind=text, 現有引用=False

傳回值=暫存槽(6)

### SL[365] kind=text, 現有引用=False

〔表情ID〕

### SL[366] kind=text, 現有引用=False

暫存槽(6)=暫存槽(5)

### SL[367] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[368] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[369] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[370] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔第一次打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[371] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[372] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[373] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[374] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[375] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[376] kind=text, 現有引用=False

〔天選〕

### SL[377] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[378] kind=text, 現有引用=False

DM_RET=DM.FINDCOLOR(160,1,260,25,暫存槽(1) & "-151515",0.9,0,INTX,INTY)

### SL[379] kind=text, 現有引用=False

Sgn((INTX>=0))

### SL[380] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[381] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(58,161,265,176,"C:\users\mymacro\xiayc1.bmp|C:\users\mymacro\xiayc2.bmp","191919",0.9,0,INTX,INTY)

### SL[382] kind=text, 現有引用=False

Sgn((INTX>=0))

### SL[383] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[384] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1050,907,1159,949,"C:\users\mymacro\fanx1.bmp|C:\users\mymacro\fanx2.bmp|C:\users\mymacro\fanx3.bmp","191919",0.9,0,INTX,INTY)

### SL[385] kind=text, 現有引用=False

Sgn((INTX>=0))

### SL[386] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[387] kind=text, 現有引用=False

Randomize

### SL[388] kind=text, 現有引用=False

X=INT(15*RND-15)

### SL[389] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[390] kind=text, 現有引用=False

Randomize

### SL[391] kind=text, 現有引用=False

Y=INT(15*RND-15)

### SL[392] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[393] kind=decoded-text, 現有引用=False

Call DM.MOVETO(636+X,865+Y)

### SL[394] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[395] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(2,g_iSimulateModeInVBSBlock,1)

### SL[396] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((600))

### SL[397] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(2,g_iSimulateModeInVBSBlock,1)

### SL[398] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[399] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[400] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[401] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[402] kind=text, 現有引用=False

〔幸運怪〕

### SL[403] kind=text, 現有引用=False

暫存槽(2)=0

### SL[404] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[405] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1500,45,1715,113,"C:\users\mymacro\mfxy1.bmp|C:\users\mymacro\mfxy2.bmp|C:\users\mymacro\mfxy3.bmp","151515",0.8,0,INTX,INTY)

### SL[406] kind=text, 現有引用=False

Sgn(INTX>0)

### SL[407] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[408] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[409] kind=text, 現有引用=False

〔幸運怪〕

### SL[410] kind=text, 現有引用=False

暫存槽(3)=1

### SL[411] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[412] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[413] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1500,45,1715,113,"C:\users\mymacro\mfxy4.bmp|C:\users\mymacro\mfxy5.bmp|C:\users\mymacro\mfxy6.bmp|C:\users\mymacro\mfxy7.bmp|C:\users\mymacro\mfxy8.bmp","151515",0.9,0,INTX,INTY)

### SL[414] kind=text, 現有引用=False

Sgn(INTX>0)

### SL[415] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[416] kind=text, 現有引用=False

傳回值=暫存槽(4)

### SL[417] kind=text, 現有引用=False

〔幸運怪〕

### SL[418] kind=text, 現有引用=False

暫存槽(4)=1

### SL[419] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[420] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[421] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[422] kind=text, 現有引用=False

〔找怪ID〕

### SL[423] kind=text, 現有引用=False

暫存槽(5)=傳回值

### SL[424] kind=decoded-text, 現有引用=False

Call QMLibrary.ThreadControl((暫存槽(5)), 2)

### SL[425] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[426] kind=text, 現有引用=False

〔幸運怪〕

### SL[427] kind=text, 現有引用=False

暫存槽(6)=傳回值

### SL[428] kind=text, 現有引用=False

Sgn(暫存槽(6)=1)

### SL[429] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[430] kind=text, 現有引用=False

〔是否組隊〕

### SL[431] kind=text, 現有引用=False

暫存槽(7)=傳回值

### SL[432] kind=text, 現有引用=False

〔是否組隊〕

### SL[433] kind=text, 現有引用=False

暫存槽(8)=傳回值

### SL[434] kind=text, 現有引用=False

〔是否組隊〕

### SL[435] kind=text, 現有引用=False

暫存槽(9)=傳回值

### SL[436] kind=text, 現有引用=False

Sgn(暫存槽(9)=0 or 暫存槽(8)=1 or 暫存槽(7)=3)

### SL[437] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[438] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔普攻〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[439] kind=text, 現有引用=False

暫存槽(10)=傳回值

