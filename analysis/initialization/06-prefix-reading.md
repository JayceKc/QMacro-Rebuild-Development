# 06 單混沌地牢：缺失初始化線索

這是線索清單，尚未將未引用字串當作原始指令。
SL 截止點只供閱讀；它不是函式入口或完整缺失來源的界線。編譯器可能把右側表達式配置在截止點之後。

## 保留的位置群組

L00000..L00052 loc=0 flags=0 count=53 ops=30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30
L00053..L00054 loc=0 flags=1 count=2 ops=30,30
L00055..L00055 loc=0 flags=0 count=1 ops=29
L00056..L00056 loc=1 flags=0 count=1 ops=255
L00057..L00058 loc=3 flags=0 count=2 ops=255,255
L00059..L00059 loc=4 flags=0 count=1 ops=255
L00060..L00068 loc=5 flags=0 count=9 ops=255,255,255,255,255,255,255,255,255
L00069..L00069 loc=6 flags=0 count=1 ops=255
L00070..L00070 loc=7 flags=0 count=1 ops=255
L00071..L00071 loc=8 flags=0 count=1 ops=255
L00072..L00073 loc=9 flags=0 count=2 ops=255,2
L00074..L00075 loc=10 flags=0 count=2 ops=31,30
L00076..L00077 loc=11 flags=0 count=2 ops=31,30
L00078..L00079 loc=12 flags=0 count=2 ops=31,30
L00080..L00081 loc=13 flags=0 count=2 ops=31,30
L00082..L00083 loc=14 flags=0 count=2 ops=31,30
L00084..L00084 loc=15 flags=0 count=1 ops=30
L00085..L00085 loc=16 flags=0 count=1 ops=2
L00086..L00086 loc=17 flags=0 count=1 ops=13
L00087..L00087 loc=20 flags=0 count=1 ops=255
L00088..L00088 loc=21 flags=0 count=1 ops=255
L00089..L00089 loc=22 flags=0 count=1 ops=255
L00090..L00090 loc=24 flags=0 count=1 ops=255
L00091..L00091 loc=25 flags=0 count=1 ops=255
L00092..L00092 loc=26 flags=0 count=1 ops=255
L00093..L00093 loc=27 flags=0 count=1 ops=255
L00094..L00094 loc=28 flags=0 count=1 ops=255
L00095..L00095 loc=30 flags=0 count=1 ops=255
L00096..L00096 loc=31 flags=0 count=1 ops=255
L00097..L00097 loc=33 flags=0 count=1 ops=255
L00098..L00098 loc=34 flags=0 count=1 ops=255
L00099..L00099 loc=35 flags=0 count=1 ops=255
L00100..L00100 loc=36 flags=0 count=1 ops=255
L00101..L00102 loc=38 flags=0 count=2 ops=255,255
L00103..L00103 loc=39 flags=0 count=1 ops=255
L00104..L00104 loc=40 flags=0 count=1 ops=255
L00105..L00105 loc=41 flags=0 count=1 ops=255
L00106..L00106 loc=43 flags=0 count=1 ops=255
L00107..L00107 loc=44 flags=0 count=1 ops=255
L00108..L00108 loc=45 flags=0 count=1 ops=255
L00109..L00109 loc=46 flags=0 count=1 ops=255
L00110..L00110 loc=47 flags=0 count=1 ops=255
L00111..L00111 loc=48 flags=0 count=1 ops=255
L00112..L00112 loc=49 flags=0 count=1 ops=255
L00113..L00113 loc=50 flags=0 count=1 ops=255
L00114..L00116 loc=51 flags=0 count=3 ops=255,255,255
L00117..L00119 loc=52 flags=0 count=3 ops=255,255,255
L00120..L00124 loc=53 flags=0 count=5 ops=255,255,255,255,255
L00125..L00127 loc=54 flags=0 count=3 ops=255,255,255
L00128..L00132 loc=55 flags=0 count=5 ops=255,255,255,255,255
L00133..L00133 loc=56 flags=0 count=1 ops=255
L00134..L00136 loc=57 flags=0 count=3 ops=255,255,255
L00137..L00141 loc=58 flags=0 count=5 ops=255,255,255,255,255
L00142..L00146 loc=59 flags=0 count=5 ops=255,255,255,255,255
L00147..L00151 loc=60 flags=0 count=5 ops=255,255,255,255,255
L00152..L00156 loc=61 flags=0 count=5 ops=255,255,255,255,255
L00157..L00157 loc=62 flags=0 count=1 ops=255
L00158..L00158 loc=63 flags=0 count=1 ops=255
L00159..L00159 loc=64 flags=0 count=1 ops=255
L00160..L00162 loc=65 flags=0 count=3 ops=255,255,255
L00163..L00163 loc=66 flags=0 count=1 ops=255
L00164..L00167 loc=67 flags=0 count=4 ops=255,255,255,255
L00168..L00170 loc=68 flags=0 count=3 ops=255,255,255
L00171..L00171 loc=69 flags=0 count=1 ops=255
L00172..L00174 loc=70 flags=0 count=3 ops=255,255,255
L00175..L00175 loc=72 flags=0 count=1 ops=255
L00176..L00177 loc=73 flags=0 count=2 ops=255,255
L00178..L00178 loc=74 flags=0 count=1 ops=255
L00179..L00179 loc=75 flags=0 count=1 ops=255
L00180..L00180 loc=76 flags=0 count=1 ops=255
L00181..L00181 loc=78 flags=0 count=1 ops=255
L00182..L00185 loc=79 flags=0 count=4 ops=255,255,255,255
L00186..L00186 loc=80 flags=0 count=1 ops=255
L00187..L00187 loc=81 flags=0 count=1 ops=255
L00188..L00188 loc=82 flags=0 count=1 ops=255
L00189..L00189 loc=84 flags=0 count=1 ops=255
L00190..L00193 loc=85 flags=0 count=4 ops=255,255,255,255
L00194..L00194 loc=86 flags=0 count=1 ops=255
L00195..L00195 loc=87 flags=0 count=1 ops=255
L00196..L00196 loc=88 flags=0 count=1 ops=255
L00197..L00197 loc=90 flags=0 count=1 ops=255
L00198..L00201 loc=91 flags=0 count=4 ops=255,255,255,255
L00202..L00202 loc=92 flags=0 count=1 ops=255
L00203..L00203 loc=93 flags=0 count=1 ops=255
L00204..L00204 loc=94 flags=0 count=1 ops=255
L00205..L00208 loc=96 flags=0 count=4 ops=255,255,255,255
L00209..L00209 loc=97 flags=0 count=1 ops=255
L00210..L00210 loc=98 flags=0 count=1 ops=255
L00211..L00211 loc=99 flags=0 count=1 ops=255
L00212..L00212 loc=101 flags=0 count=1 ops=255
L00213..L00216 loc=102 flags=0 count=4 ops=255,255,255,255
L00217..L00217 loc=103 flags=0 count=1 ops=255
L00218..L00220 loc=104 flags=0 count=3 ops=255,255,255
L00221..L00223 loc=105 flags=0 count=3 ops=255,255,255
L00224..L00224 loc=107 flags=0 count=1 ops=255
L00225..L00226 loc=108 flags=0 count=2 ops=255,255
L00227..L00227 loc=109 flags=0 count=1 ops=255
L00228..L00229 loc=110 flags=0 count=2 ops=255,255
L00230..L00231 loc=111 flags=0 count=2 ops=255,255
L00232..L00232 loc=112 flags=0 count=1 ops=255
L00233..L00234 loc=113 flags=0 count=2 ops=255,255
L00235..L00236 loc=114 flags=0 count=2 ops=255,255
L00237..L00237 loc=115 flags=0 count=1 ops=255
L00238..L00239 loc=116 flags=0 count=2 ops=255,255
L00240..L00241 loc=117 flags=0 count=2 ops=255,255
L00242..L00242 loc=118 flags=0 count=1 ops=255
L00243..L00243 loc=119 flags=0 count=1 ops=255
L00244..L00244 loc=120 flags=0 count=1 ops=255
L00245..L00245 loc=121 flags=0 count=1 ops=255
L00246..L00246 loc=122 flags=0 count=1 ops=255
L00247..L00247 loc=127 flags=0 count=1 ops=255
L00248..L00251 loc=128 flags=0 count=4 ops=255,255,255,255
L00252..L00253 loc=129 flags=0 count=2 ops=255,255
L00254..L00254 loc=130 flags=0 count=1 ops=255
L00255..L00255 loc=131 flags=0 count=1 ops=255
L00256..L00256 loc=132 flags=0 count=1 ops=255
L00257..L00257 loc=133 flags=0 count=1 ops=255
L00258..L00258 loc=134 flags=0 count=1 ops=255
L00259..L00259 loc=135 flags=0 count=1 ops=255
L00260..L00260 loc=137 flags=0 count=1 ops=255
L00261..L00261 loc=138 flags=0 count=1 ops=255
L00262..L00262 loc=139 flags=0 count=1 ops=255
L00263..L00263 loc=140 flags=0 count=1 ops=255
L00264..L00264 loc=141 flags=0 count=1 ops=255
L00265..L00265 loc=142 flags=0 count=1 ops=255
L00266..L00266 loc=143 flags=0 count=1 ops=255
L00267..L00267 loc=144 flags=0 count=1 ops=255
L00268..L00268 loc=145 flags=0 count=1 ops=255
L00269..L00269 loc=146 flags=0 count=1 ops=255
L00270..L00270 loc=147 flags=0 count=1 ops=255
L00271..L00271 loc=148 flags=0 count=1 ops=255
L00272..L00272 loc=149 flags=0 count=1 ops=255
L00273..L00273 loc=150 flags=0 count=1 ops=255
L00274..L00274 loc=151 flags=0 count=1 ops=255
L00275..L00275 loc=152 flags=0 count=1 ops=255
L00276..L00276 loc=153 flags=0 count=1 ops=255
L00277..L00277 loc=154 flags=0 count=1 ops=255
L00278..L00278 loc=155 flags=0 count=1 ops=255
L00279..L00279 loc=156 flags=0 count=1 ops=255
L00280..L00280 loc=157 flags=0 count=1 ops=255
L00281..L00281 loc=158 flags=0 count=1 ops=255
L00282..L00282 loc=159 flags=0 count=1 ops=255
L00283..L00283 loc=160 flags=0 count=1 ops=255
L00284..L00284 loc=161 flags=0 count=1 ops=255
L00285..L00285 loc=162 flags=0 count=1 ops=255
L00286..L00286 loc=163 flags=0 count=1 ops=255
L00287..L00287 loc=164 flags=0 count=1 ops=255
L00288..L00288 loc=166 flags=0 count=1 ops=255
L00289..L00291 loc=167 flags=0 count=3 ops=255,255,255
L00292..L00293 loc=168 flags=0 count=2 ops=255,255
L00294..L00294 loc=169 flags=0 count=1 ops=255
L00295..L00295 loc=170 flags=0 count=1 ops=255
L00296..L00297 loc=171 flags=0 count=2 ops=255,255
L00298..L00298 loc=172 flags=0 count=1 ops=255
L00299..L00299 loc=173 flags=0 count=1 ops=255
L00300..L00300 loc=174 flags=0 count=1 ops=255
L00301..L00301 loc=175 flags=0 count=1 ops=255
L00302..L00302 loc=176 flags=0 count=1 ops=255
L00303..L00303 loc=177 flags=0 count=1 ops=255
L00304..L00304 loc=178 flags=0 count=1 ops=255
L00305..L00305 loc=179 flags=0 count=1 ops=255
L00306..L00306 loc=180 flags=0 count=1 ops=255
L00307..L00307 loc=181 flags=0 count=1 ops=255
L00308..L00308 loc=182 flags=0 count=1 ops=255
L00309..L00309 loc=183 flags=0 count=1 ops=255
L00310..L00310 loc=184 flags=0 count=1 ops=255
L00311..L00311 loc=185 flags=0 count=1 ops=255
L00312..L00312 loc=186 flags=0 count=1 ops=255
L00313..L00313 loc=187 flags=0 count=1 ops=255
L00314..L00314 loc=188 flags=0 count=1 ops=255
L00315..L00315 loc=189 flags=0 count=1 ops=255
L00316..L00316 loc=190 flags=0 count=1 ops=255
L00317..L00317 loc=191 flags=0 count=1 ops=255
L00318..L00318 loc=192 flags=0 count=1 ops=255
L00319..L00319 loc=193 flags=0 count=1 ops=255
L00320..L00320 loc=194 flags=0 count=1 ops=255
L00321..L00321 loc=197 flags=0 count=1 ops=255
L00322..L00322 loc=198 flags=0 count=1 ops=255
L00323..L00324 loc=199 flags=0 count=2 ops=255,255
L00325..L00325 loc=200 flags=0 count=1 ops=255
L00326..L00329 loc=201 flags=0 count=4 ops=255,255,255,255
L00330..L00331 loc=202 flags=0 count=2 ops=255,255
L00332..L00332 loc=203 flags=0 count=1 ops=255
L00333..L00335 loc=204 flags=0 count=3 ops=255,255,255
L00336..L00336 loc=206 flags=0 count=1 ops=255
L00337..L00337 loc=207 flags=0 count=1 ops=255
L00338..L00338 loc=208 flags=0 count=1 ops=255
L00339..L00339 loc=209 flags=0 count=1 ops=255
L00340..L00342 loc=210 flags=0 count=3 ops=255,255,255
L00343..L00343 loc=211 flags=0 count=1 ops=255
L00344..L00351 loc=212 flags=0 count=8 ops=255,255,255,255,255,255,255,255
L00352..L00352 loc=213 flags=0 count=1 ops=255
L00353..L00362 loc=214 flags=0 count=10 ops=255,255,255,255,255,255,255,255,255,255
L00363..L00363 loc=215 flags=0 count=1 ops=255
L00364..L00366 loc=216 flags=0 count=3 ops=255,255,255
L00367..L00367 loc=217 flags=0 count=1 ops=255
L00368..L00370 loc=218 flags=0 count=3 ops=255,255,255
L00371..L00373 loc=219 flags=0 count=3 ops=255,255,255
L00374..L00376 loc=220 flags=0 count=3 ops=255,255,255
L00377..L00377 loc=221 flags=0 count=1 ops=255
L00378..L00381 loc=222 flags=0 count=4 ops=255,255,255,255
L00382..L00382 loc=223 flags=0 count=1 ops=255
L00383..L00385 loc=224 flags=0 count=3 ops=255,255,255
L00386..L00386 loc=225 flags=0 count=1 ops=255
L00387..L00389 loc=226 flags=0 count=3 ops=255,255,255
L00390..L00390 loc=227 flags=0 count=1 ops=255
L00391..L00392 loc=228 flags=0 count=2 ops=255,255
L00393..L00393 loc=229 flags=0 count=1 ops=255
L00394..L00395 loc=230 flags=0 count=2 ops=255,255
L00396..L00396 loc=231 flags=0 count=1 ops=255
L00397..L00397 loc=232 flags=0 count=1 ops=255
L00398..L00398 loc=233 flags=0 count=1 ops=255
L00399..L00399 loc=234 flags=0 count=1 ops=255
L00400..L00400 loc=235 flags=0 count=1 ops=255
L00401..L00403 loc=236 flags=0 count=3 ops=255,255,255
L00404..L00404 loc=237 flags=0 count=1 ops=255
L00405..L00407 loc=238 flags=0 count=3 ops=255,255,255
L00408..L00408 loc=239 flags=0 count=1 ops=255
L00409..L00411 loc=240 flags=0 count=3 ops=255,255,255
L00412..L00412 loc=241 flags=0 count=1 ops=255
L00413..L00413 loc=242 flags=0 count=1 ops=255
L00414..L00414 loc=243 flags=0 count=1 ops=255
L00415..L00415 loc=269 flags=0 count=1 ops=255
L00416..L00416 loc=272 flags=0 count=1 ops=255
L00417..L00419 loc=273 flags=0 count=3 ops=255,255,255
L00420..L00420 loc=274 flags=0 count=1 ops=255
L00421..L00422 loc=275 flags=0 count=2 ops=255,255
L00423..L00423 loc=276 flags=0 count=1 ops=255
L00424..L00424 loc=277 flags=0 count=1 ops=255
L00425..L00425 loc=278 flags=0 count=1 ops=255
L00426..L00426 loc=279 flags=0 count=1 ops=255
L00427..L00427 loc=280 flags=0 count=1 ops=255
L00428..L00428 loc=281 flags=0 count=1 ops=255
L00429..L00429 loc=282 flags=0 count=1 ops=255
L00430..L00430 loc=283 flags=0 count=1 ops=255
L00431..L00431 loc=284 flags=0 count=1 ops=255
L00432..L00432 loc=285 flags=0 count=1 ops=255
L00433..L00433 loc=286 flags=0 count=1 ops=255
L00434..L00434 loc=287 flags=0 count=1 ops=255
L00435..L00437 loc=288 flags=0 count=3 ops=255,255,255
L00438..L00438 loc=289 flags=0 count=1 ops=255
L00439..L00439 loc=290 flags=0 count=1 ops=255
L00440..L00442 loc=291 flags=0 count=3 ops=255,255,255
L00443..L00445 loc=292 flags=0 count=3 ops=255,255,255
L00446..L00448 loc=293 flags=0 count=3 ops=255,255,255
L00449..L00449 loc=294 flags=0 count=1 ops=255
L00450..L00452 loc=295 flags=0 count=3 ops=255,255,255
L00453..L00453 loc=296 flags=0 count=1 ops=255
L00454..L00456 loc=297 flags=0 count=3 ops=255,255,255
L00457..L00457 loc=298 flags=0 count=1 ops=255
L00458..L00460 loc=299 flags=0 count=3 ops=255,255,255
L00461..L00464 loc=300 flags=0 count=4 ops=255,255,255,255
L00465..L00465 loc=301 flags=0 count=1 ops=255
L00466..L00466 loc=302 flags=0 count=1 ops=255
L00467..L00469 loc=303 flags=0 count=3 ops=255,255,255
L00470..L00470 loc=304 flags=0 count=1 ops=255
L00471..L00474 loc=305 flags=0 count=4 ops=255,255,255,255
L00475..L00478 loc=306 flags=0 count=4 ops=255,255,255,255
L00479..L00479 loc=307 flags=0 count=1 ops=255
L00480..L00482 loc=308 flags=0 count=3 ops=255,255,255
L00483..L00483 loc=309 flags=0 count=1 ops=255
L00484..L00484 loc=337 flags=0 count=1 ops=255
L00485..L00488 loc=338 flags=0 count=4 ops=255,255,255,255
L00489..L00489 loc=339 flags=0 count=1 ops=255
L00490..L00490 loc=340 flags=0 count=1 ops=255
L00491..L00492 loc=341 flags=0 count=2 ops=255,255
L00493..L00493 loc=342 flags=0 count=1 ops=255
L00494..L00496 loc=343 flags=0 count=3 ops=255,255,255
L00497..L00497 loc=344 flags=0 count=1 ops=255
L00498..L00498 loc=345 flags=0 count=1 ops=255
L00499..L00499 loc=346 flags=0 count=1 ops=255
L00500..L00500 loc=347 flags=0 count=1 ops=255
L00501..L00501 loc=367 flags=0 count=1 ops=255
L00502..L00502 loc=368 flags=0 count=1 ops=255
L00503..L00505 loc=369 flags=0 count=3 ops=255,255,255
L00506..L00506 loc=370 flags=0 count=1 ops=255
L00507..L00509 loc=371 flags=0 count=3 ops=255,255,255
L00510..L00510 loc=372 flags=0 count=1 ops=255
L00511..L00511 loc=373 flags=0 count=1 ops=255
L00512..L00513 loc=374 flags=0 count=2 ops=255,255
L00514..L00514 loc=375 flags=0 count=1 ops=255
L00515..L00517 loc=376 flags=0 count=3 ops=255,255,255
L00518..L00518 loc=377 flags=0 count=1 ops=255
L00519..L00519 loc=378 flags=0 count=1 ops=255
L00520..L00522 loc=379 flags=0 count=3 ops=255,255,255
L00523..L00523 loc=381 flags=0 count=1 ops=255
L00524..L00525 loc=382 flags=0 count=2 ops=255,255
L00526..L00526 loc=383 flags=0 count=1 ops=255
L00527..L00527 loc=384 flags=0 count=1 ops=255
L00528..L00530 loc=385 flags=0 count=3 ops=255,255,255
L00531..L00531 loc=387 flags=0 count=1 ops=255
L00532..L00532 loc=388 flags=0 count=1 ops=255
L00533..L00535 loc=389 flags=0 count=3 ops=255,255,255
L00536..L00536 loc=391 flags=0 count=1 ops=255
L00537..L00540 loc=392 flags=0 count=4 ops=255,255,255,255
L00541..L00541 loc=393 flags=0 count=1 ops=255
L00542..L00544 loc=394 flags=0 count=3 ops=255,255,255
L00545..L00545 loc=395 flags=0 count=1 ops=255
L00546..L00548 loc=396 flags=0 count=3 ops=255,255,255
L00549..L00549 loc=397 flags=0 count=1 ops=255
L00550..L00552 loc=398 flags=0 count=3 ops=255,255,255
L00553..L00553 loc=399 flags=0 count=1 ops=255
L00554..L00554 loc=401 flags=0 count=1 ops=255
L00555..L00557 loc=402 flags=0 count=3 ops=255,255,255
L00558..L00560 loc=403 flags=0 count=3 ops=255,255,255
L00561..L00561 loc=404 flags=0 count=1 ops=255
L00562..L00564 loc=405 flags=0 count=3 ops=255,255,255
L00565..L00567 loc=406 flags=0 count=3 ops=255,255,255
L00568..L00568 loc=407 flags=0 count=1 ops=255
L00569..L00569 loc=408 flags=0 count=1 ops=255

## 原 SL 字串順序

### SL[0] kind=decoded-text, 現有引用=True

Dim 暫存槽(256):Dim 目前呼叫框架,新呼叫框架:Set 目前呼叫框架=Nothing:Set 新呼叫框架=Nothing

### SL[1] kind=decoded-text, 現有引用=True

Class 框架類別_〔計算走塔圖〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[2] kind=decoded-text, 現有引用=True

Class 框架類別_〔再來一次〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[3] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥空轉〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[4] kind=decoded-text, 現有引用=True

Class 框架類別_〔找綠色過門〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[5] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃百分比藥6〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[6] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃百分比藥70〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[7] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃百分比藥40〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[8] kind=decoded-text, 現有引用=True

Class 框架類別_〔找圖二〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[9] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃百分比藥11〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[10] kind=decoded-text, 現有引用=True

Class 框架類別_〔找塔圖〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[11] kind=decoded-text, 現有引用=True

Class 框架類別_〔更多Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[12] kind=decoded-text, 現有引用=True

Class 框架類別_〔圣騎士專用〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[13] kind=decoded-text, 現有引用=True

Class 框架類別_〔圖402檢測跳躍〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[14] kind=decoded-text, 現有引用=True

Class 框架類別_〔檢查服務器界面〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[15] kind=decoded-text, 現有引用=True

Class 框架類別_〔找按鈕〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[16] kind=decoded-text, 現有引用=True

Class 框架類別_〔找怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[17] kind=decoded-text, 現有引用=True

Class 框架類別_〔退出副本〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[18] kind=decoded-text, 現有引用=True

Class 框架類別_〔找圖三〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[19] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能三〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[20] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能四〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[21] kind=decoded-text, 現有引用=True

Class 框架類別_〔按鈕點擊進本〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[22] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能一〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[23] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥11〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[24] kind=decoded-text, 現有引用=True

Class 框架類別_〔FORM1.BUTTON1.CLICK〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[25] kind=decoded-text, 現有引用=True

Class 框架類別_〔隨機技能二〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[26] kind=decoded-text, 現有引用=True

Class 框架類別_〔修理〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[27] kind=decoded-text, 現有引用=True

Class 框架類別_〔覺醒〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[28] kind=decoded-text, 現有引用=True

Class 框架類別_〔開始打怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[29] kind=decoded-text, 現有引用=True

Class 框架類別_〔檢查技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[30] kind=decoded-text, 現有引用=True

Class 框架類別_〔監控死亡〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[31] kind=decoded-text, 現有引用=True

Class 框架類別_〔重啟小功能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[32] kind=decoded-text, 現有引用=True

Class 框架類別_〔找對話〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[33] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥40〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[34] kind=decoded-text, 現有引用=True

Class 框架類別_〔紫門打完撿東西〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[35] kind=decoded-text, 現有引用=True

Class 框架類別_〔圖四地牢找怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[36] kind=decoded-text, 現有引用=True

Class 框架類別_〔不使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[37] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥6〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[38] kind=decoded-text, 現有引用=True

Class 框架類別_〔按G〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[39] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃地牢氣息藥〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[40] kind=decoded-text, 現有引用=True

Class 框架類別_〔半魔專用〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[41] kind=decoded-text, 現有引用=True

Class 框架類別_〔判斷紫金門〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[42] kind=decoded-text, 現有引用=True

Class 框架類別_〔第一次打怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[43] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用ZX技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[44] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃藥70〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[45] kind=decoded-text, 現有引用=True

Class 框架類別_〔切換道具欄〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[46] kind=decoded-text, 現有引用=True

Class 框架類別_〔停止打怪〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[47] kind=decoded-text, 現有引用=True

Class 框架類別_〔使用Z技能〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[48] kind=decoded-text, 現有引用=True

Class 框架類別_〔吃百分比藥空轉〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[49] kind=decoded-text, 現有引用=True

Class 框架類別_〔傘蘿專用〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[50] kind=decoded-text, 現有引用=True

Class 框架類別_〔計算走位〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[51] kind=decoded-text, 現有引用=True

Class 框架類別_〔找綠色〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[52] kind=decoded-text, 現有引用=True

Class 框架類別_〔找圖四〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[53] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[54] kind=text, 現有引用=True

FILE
If IsEmpty(FILE) Then Set FILE=CreateObject("QMPlugin.File")

### SL[55] kind=decoded-text, 現有引用=False

Call FILE.CREATEFOLDER("C:\方舟混沌\")

### SL[56] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[57] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔重啟小功能〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[58] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[59] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[60] kind=text, 現有引用=False

〔重啟小功能ID〕

### SL[61] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[62] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[63] kind=decoded-text, 現有引用=False

Call QMLibrary.OpenLog("C:\方舟混沌\运行日志.log")

### SL[64] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[65] kind=text, 現有引用=True

Set 新呼叫框架=New 框架類別_〔FORM1.BUTTON1.CLICK〕::Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[66] kind=decoded-text, 現有引用=True

Call FILE.DELETEFOLDER("C:\方舟混沌")

### SL[67] kind=decoded-text, 現有引用=True

Call FILE.DELETEFOLDER("C:\Users\mymacro")

### SL[68] kind=decoded-text, 現有引用=True

Call FILE.DELETEFOLDER("C:\Users\Administrator\AppData\Roaming\qmacro")

### SL[69] kind=decoded-text, 現有引用=True

Call FILE.DELETEFOLDER("C:\Users\Administrator\AppData\Roaming\MyMacro")

### SL[70] kind=decoded-text, 現有引用=True

Call FILE.DELETEFOLDER("C:\Users\Administrator\AppData\Roaming\MacroCommerce")

### SL[71] kind=decoded-text, 現有引用=True

Call QMLibrary.MessageNotify(1,"缓存文件已删除")

### SL[72] kind=text, 現有引用=True

傳回值=目前呼叫框架.函式回傳欄位:Set 新呼叫框架=目前呼叫框架:Set 目前呼叫框架=目前呼叫框架.上層呼叫框架:Set 新呼叫框架=Nothing

### SL[73] kind=text, 現有引用=False

SET WS=CREATEOBJECT("Wscript.Shell")

### SL[74] kind=decoded-text, 現有引用=False

Call WS.RUN("regsvr32 atl.dll /s")

### SL[75] kind=text, 現有引用=False

SET WS=nothing

### SL[76] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[77] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro\fz","fz.dll")

### SL[78] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","fzreg.dll")

### SL[79] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","*.bmp")

### SL[80] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[81] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(QMLibrary.CallAPI2("C:\users\mymacro\fzreg.dll", "SetDllPathW", "C:\users\mymacro\fz\fz.dll", 0))

### SL[82] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[83] kind=text, 現有引用=False

SET DM=CREATEOBJECT("dm.dmsoft")

### SL[84] kind=decoded-text, 現有引用=False

Call DM.SETSHOWERRORMSG(0)

### SL[85] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[86] kind=decoded-text, 現有引用=False

〔版本〕=DM.VER()

### SL[87] kind=text, 現有引用=False

Sgn((〔版本〕=7.2450))

### SL[88] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("成功"))

### SL[89] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("失败"))

### SL[90] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[91] kind=decoded-text, 現有引用=False

〔鼠標〕=DM.ENABLEREALMOUSE(2,10,60)

### SL[92] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("鼠标" & 〔鼠標〕)

### SL[93] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[94] kind=empty, 現有引用=False



### SL[95] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[96] kind=text, 現有引用=False

〔索引〕=ARRAY(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)

### SL[97] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[98] kind=text, 現有引用=False

Form1.ComboBox1.ListIndex

### SL[99] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[100] kind=text, 現有引用=False

〔吃藥〕=〔索引〕(暫存槽(1))

### SL[101] kind=text, 現有引用=False

Form1.ComboBox2.ListIndex

### SL[102] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[103] kind=text, 現有引用=False

〔技能釋放〕=〔索引〕(暫存槽(1))

### SL[104] kind=text, 現有引用=False

Form1.ComboBox3.ListIndex

### SL[105] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[106] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[107] kind=text, 現有引用=False

〔版本選擇〕

### SL[108] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[109] kind=decoded-text, 現有引用=False

傳回值=暫存槽(1)

### SL[110] kind=text, 現有引用=False

〔獎勵次數〕

### SL[111] kind=text, 現有引用=False

暫存槽(1)=〔索引〕(FORM1.COMBOBOX4.LISTINDEX)

### SL[112] kind=text, 現有引用=False

Form1.ComboBox5.ListIndex

### SL[113] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[114] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[115] kind=text, 現有引用=False

〔覺醒釋放〕

### SL[116] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[117] kind=decoded-text, 現有引用=False

〔刷幾次修理〕=〔索引〕(FORM1.COMBOBOX6.LISTINDEX)

### SL[118] kind=text, 現有引用=False

Form1.ComboBox7.ListIndex

### SL[119] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[120] kind=text, 現有引用=False

〔吃百分比藥〕=〔索引〕(暫存槽(1))

### SL[121] kind=text, 現有引用=False

Form1.ComboBox8.ListIndex

### SL[122] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[123] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[124] kind=text, 現有引用=False

〔復活〕

### SL[125] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[126] kind=text, 現有引用=False

Form1.ComboBox11.ListIndex

### SL[127] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[128] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[129] kind=text, 現有引用=False

〔道具欄〕

### SL[130] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[131] kind=text, 現有引用=False

Form1.ComboBox12.ListIndex

### SL[132] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[133] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[134] kind=text, 現有引用=False

〔圖四行進速度〕

### SL[135] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[136] kind=text, 現有引用=False

Form1.ComboBox13.ListIndex

### SL[137] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[138] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[139] kind=text, 現有引用=False

〔技能頻率〕

### SL[140] kind=text, 現有引用=False

暫存槽(2)=〔索引〕(暫存槽(1))

### SL[141] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[142] kind=decoded-text, 現有引用=False

〔會員〕=〔索引〕(FORM1.COMBOBOX99.LISTINDEX)

### SL[143] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[144] kind=decoded-text, 現有引用=False

傳回值=暫存槽(1)

### SL[145] kind=text, 現有引用=False

〔天選〕

### SL[146] kind=text, 現有引用=False

暫存槽(1)=QMLibrary.GetGlobalVar("MMVerifyCode", 0)

### SL[147] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[148] kind=text, 現有引用=False

Form1.CheckBox1.Value

### SL[149] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[150] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[151] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[152] kind=text, 現有引用=False

〔一層覺醒〕

### SL[153] kind=text, 現有引用=False

暫存槽(2)=1

### SL[154] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[155] kind=text, 現有引用=False

〔一層覺醒〕

### SL[156] kind=text, 現有引用=False

暫存槽(3)=0

### SL[157] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[158] kind=text, 現有引用=False

Sgn(FORM1.CHECKBOX2.VALUE=1)

### SL[159] kind=decoded-text, 現有引用=False

〔重連〕=1

### SL[160] kind=text, 現有引用=False

〔重連〕=0

### SL[161] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[162] kind=text, 現有引用=False

Form1.CheckBox3.Value

### SL[163] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[164] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[165] kind=text, 現有引用=False

〔勾選銀幣藥〕=1

### SL[166] kind=text, 現有引用=False

〔勾選銀幣藥〕=0

### SL[167] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[168] kind=text, 現有引用=False

Form1.CheckBox4.Value

### SL[169] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[170] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[171] kind=text, 現有引用=False

〔勾選百分比藥〕=1

### SL[172] kind=text, 現有引用=False

〔勾選百分比藥〕=0

### SL[173] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[174] kind=text, 現有引用=False

Form1.CheckBox5.Value

### SL[175] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[176] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[177] kind=text, 現有引用=False

〔吃氣息藥〕=1

### SL[178] kind=text, 現有引用=False

〔吃氣息藥〕=0

### SL[179] kind=text, 現有引用=False

Form1.CheckBox6.Value

### SL[180] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[181] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[182] kind=text, 現有引用=False

〔吃第二格藥〕=1

### SL[183] kind=text, 現有引用=False

〔吃第二格藥〕=0

### SL[184] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[185] kind=text, 現有引用=False

〔版本選擇〕

### SL[186] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[187] kind=text, 現有引用=False

Sgn(暫存槽(1)=5)

### SL[188] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[189] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[190] kind=text, 現有引用=False

〔版本選擇〕

### SL[191] kind=text, 現有引用=False

暫存槽(2)=1

### SL[192] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[193] kind=text, 現有引用=False

〔不打紫門〕

### SL[194] kind=text, 現有引用=False

暫存槽(3)=1

### SL[195] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[196] kind=text, 現有引用=False

Sgn(〔刷幾次修理〕=0)

### SL[197] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[198] kind=text, 現有引用=False

JCXL=6

### SL[199] kind=text, 現有引用=False

Sgn(〔刷幾次修理〕=1)

### SL[200] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[201] kind=text, 現有引用=False

JCXL=10

### SL[202] kind=text, 現有引用=False

Sgn(〔刷幾次修理〕=2)

### SL[203] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[204] kind=text, 現有引用=False

JCXL=15

### SL[205] kind=text, 現有引用=False

Sgn(〔刷幾次修理〕=3)

### SL[206] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[207] kind=text, 現有引用=False

JCXL=20

### SL[208] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[209] kind=text, 現有引用=False

JCXL=6

### SL[210] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[211] kind=text, 現有引用=False

〔天選〕

### SL[212] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[213] kind=text, 現有引用=False

Sgn(暫存槽(1)="")

### SL[214] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[215] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[216] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((2000))

### SL[217] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[218] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((4000))

### SL[219] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((5000))

### SL[220] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[221] kind=text, 現有引用=False

Randomize

### SL[222] kind=text, 現有引用=False

YDX=INT(5*RND+35)

### SL[223] kind=text, 現有引用=False

Randomize

### SL[224] kind=text, 現有引用=False

YDY=INT(10*RND+10)

### SL[225] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[226] kind=decoded-text, 現有引用=False

Call DM.MOVETO(YDX,YDY)

### SL[227] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[228] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[229] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[230] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint((">>>>>>脚本启动"))

### SL[231] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[232] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[233] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[234] kind=text, 現有引用=False

Randomize

### SL[235] kind=text, 現有引用=False

YDX=INT(5*RND+35)

### SL[236] kind=text, 現有引用=False

Randomize

### SL[237] kind=text, 現有引用=False

YDY=INT(10*RND+10)

### SL[238] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[239] kind=decoded-text, 現有引用=False

Call DM.MOVETO(YDX,YDY)

### SL[240] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[241] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[242] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[243] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[244] kind=decoded-text, 現有引用=False

Call DM.MOVETO(958,975)

### SL[245] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[246] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[247] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[248] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[249] kind=text, 現有引用=False

〔天選〕

### SL[250] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[251] kind=text, 現有引用=False

DM_RET=DM.FINDCOLOR(160,1,260,25,暫存槽(1) & "-151515",0.9,0,INTX,INTY)

### SL[252] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[253] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[254] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDCOLOR(1637,72,1860,274,"A39D8D-000000|A29D8E-000000|A39D91-000000|A39D8F-00000|A49B92-000000",1,0,INTX,INTY)

### SL[255] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[256] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[257] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[258] kind=decoded-text, 現有引用=False

Call DM.MOVETO(1904,283)

### SL[259] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(200)

### SL[260] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[261] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[262] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Enter",g_iSimulateModeInVBSBlock,1)

### SL[263] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(600)

### SL[264] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Enter",g_iSimulateModeInVBSBlock,1)

### SL[265] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(600)

### SL[266] kind=decoded-text, 現有引用=False

Call DM.MOVETO(1907,90)

### SL[267] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(200)

### SL[268] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[269] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(700)

### SL[270] kind=decoded-text, 現有引用=False

Call DM.MOVETO(1874,103)

### SL[271] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(200)

### SL[272] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[273] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(300)

### SL[274] kind=decoded-text, 現有引用=False

Call DM.MOVETO(1873,73)

### SL[275] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(200)

### SL[276] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[277] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[278] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[279] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint((">>>>>>找按钮对话"))

### SL[280] kind=text, 現有引用=False

Sgn((〔會員〕=0))

### SL[281] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[282] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找按鈕〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[283] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[284] kind=text, 現有引用=False

Sgn((〔會員〕=1))

### SL[285] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[286] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找對話〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[287] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[288] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[289] kind=text, 現有引用=False

〔重連〕=0

### SL[290] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[291] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("开始修理"))

### SL[292] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔修理〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[293] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[294] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[295] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔覺醒〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[296] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[297] kind=text, 現有引用=False

〔覺醒ID〕=暫存槽(1)

### SL[298] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[299] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[300] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔監控死亡〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[301] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[302] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[303] kind=text, 現有引用=False

〔監控死亡ID〕

### SL[304] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[305] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[306] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[307] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔切換道具欄〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[308] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[309] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[310] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔按鈕點擊進本〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[311] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[312] kind=text, 現有引用=False

傳回值=暫存槽(1)

### SL[313] kind=text, 現有引用=False

〔重新開始〕

### SL[314] kind=text, 現有引用=False

暫存槽(1)=0

### SL[315] kind=text, 現有引用=False

傳回值=暫存槽(1)

### SL[316] kind=text, 現有引用=False

〔找到紫門〕

### SL[317] kind=text, 現有引用=False

暫存槽(1)=0

### SL[318] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[319] kind=text, 現有引用=False

〔按鈕界面〕

### SL[320] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[321] kind=text, 現有引用=False

Sgn(暫存槽(1)=4)

### SL[322] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[323] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找圖四〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[324] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[325] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[326] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔第一次打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[327] kind=text, 現有引用=False

暫存槽(3)=傳回值

### SL[328] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[329] kind=text, 現有引用=False

Sgn(〔吃氣息藥〕=1)

### SL[330] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[331] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[332] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[333] kind=decoded-text, 現有引用=False

Call DM.MOVETO(958,975)

### SL[334] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[335] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[336] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[337] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔再來一次〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[338] kind=text, 現有引用=False

暫存槽(4)=傳回值

### SL[339] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[340] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找圖四〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[341] kind=text, 現有引用=False

暫存槽(5)=傳回值

### SL[342] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[343] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔開始打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[344] kind=text, 現有引用=False

暫存槽(6)=傳回值

### SL[345] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[346] kind=decoded-text, 現有引用=False

Call QMLibrary.ExitScript(0)

### SL[347] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[348] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔第一次打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[349] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[350] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[351] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[352] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[353] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("----------开始循环-----------"))

### SL[354] kind=text, 現有引用=False

〔刷本累計次數〕=〔刷本累計次數〕+1

### SL[355] kind=text, 現有引用=False

〔是否修理次數〕=〔是否修理次數〕+1

### SL[356] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("刷本累计次数" & 〔刷本累計次數〕))

### SL[357] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[358] kind=decoded-text, 現有引用=False

FORM1.INPUTBOX1.TEXT=〔刷本累計次數〕

### SL[359] kind=decoded-text, 現有引用=False

FORM1.INPUTBOX2.TEXT=〔金門累計次數〕

### SL[360] kind=decoded-text, 現有引用=False

FORM1.INPUTBOX3.TEXT=〔紫門累計次數〕

### SL[361] kind=decoded-text, 現有引用=False

FORM1.INPUTBOX4.TEXT=〔卡住累計次數〕

### SL[362] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[363] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----找图二"))

### SL[364] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找圖二〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[365] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[366] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[367] kind=text, 現有引用=False

〔找到圖三〕=0

### SL[368] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[369] kind=text, 現有引用=False

〔卡了〕

### SL[370] kind=text, 現有引用=False

暫存槽(2)=0

### SL[371] kind=text, 現有引用=False

傳回值=暫存槽(3)

### SL[372] kind=text, 現有引用=False

〔找到紫金〕

### SL[373] kind=text, 現有引用=False

暫存槽(3)=0

### SL[374] kind=text, 現有引用=False

傳回值=暫存槽(4)

### SL[375] kind=text, 現有引用=False

〔卡點〕

### SL[376] kind=text, 現有引用=False

暫存槽(4)=0

### SL[377] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[378] kind=text, 現有引用=False

傳回值=暫存槽(5)

### SL[379] kind=text, 現有引用=False

〔層數〕

### SL[380] kind=text, 現有引用=False

暫存槽(5)=2

### SL[381] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----开始打怪二层"))

### SL[382] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔開始打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[383] kind=text, 現有引用=False

暫存槽(6)=傳回值

### SL[384] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[385] kind=text, 現有引用=False

傳回值=暫存槽(7)

### SL[386] kind=text, 現有引用=False

〔層數〕

### SL[387] kind=text, 現有引用=False

暫存槽(7)=3

### SL[388] kind=text, 現有引用=False

〔版本選擇〕

### SL[389] kind=text, 現有引用=False

暫存槽(8)=傳回值

### SL[390] kind=text, 現有引用=False

Sgn((暫存槽(8)=1))

### SL[391] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[392] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----第一次找图三"))

### SL[393] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找圖三〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[394] kind=text, 現有引用=False

暫存槽(9)=傳回值

### SL[395] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[396] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔開始打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[397] kind=text, 現有引用=False

暫存槽(10)=傳回值

### SL[398] kind=text, 現有引用=False

〔版本選擇〕

### SL[399] kind=text, 現有引用=False

暫存槽(11)=傳回值

### SL[400] kind=text, 現有引用=False

Sgn((暫存槽(11)=0))

### SL[401] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[402] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找綠色〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[403] kind=text, 現有引用=False

暫存槽(12)=傳回值

### SL[404] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[405] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[406] kind=text, 現有引用=False

〔版本選擇〕

### SL[407] kind=text, 現有引用=False

暫存槽(13)=傳回值

### SL[408] kind=text, 現有引用=False

Sgn((暫存槽(13)=1))

### SL[409] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[410] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----三层打完了再来一次"))

### SL[411] kind=text, 現有引用=False

Sgn(〔吃氣息藥〕=1)

### SL[412] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[413] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔再來一次〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[414] kind=text, 現有引用=False

暫存槽(14)=傳回值

### SL[415] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[416] kind=decoded-text, 現有引用=False

Call QMLibrary.ExitScript(0)

### SL[417] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[418] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----退出副本"))

### SL[419] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔退出副本〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[420] kind=text, 現有引用=False

暫存槽(15)=傳回值

### SL[421] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((500))

### SL[422] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找綠色〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[423] kind=text, 現有引用=False

暫存槽(16)=傳回值

### SL[424] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[425] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----找按钮"))

### SL[426] kind=text, 現有引用=False

Sgn((〔會員〕=0))

### SL[427] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[428] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找按鈕〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[429] kind=text, 現有引用=False

暫存槽(17)=傳回值

### SL[430] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[431] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔找對話〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[432] kind=text, 現有引用=False

暫存槽(18)=傳回值

### SL[433] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[434] kind=text, 現有引用=False

Sgn((〔是否修理次數〕>=JCXL))

### SL[435] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[436] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----有会员6次宠物修理"))

### SL[437] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔修理〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[438] kind=text, 現有引用=False

暫存槽(19)=傳回值

### SL[439] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[440] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----按钮点击进本"))

### SL[441] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔按鈕點擊進本〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[442] kind=text, 現有引用=False

暫存槽(20)=傳回值

### SL[443] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[444] kind=text, 現有引用=False

〔重新開始〕

### SL[445] kind=text, 現有引用=False

暫存槽(21)=傳回值

### SL[446] kind=text, 現有引用=False

Sgn((暫存槽(21)=1))

### SL[447] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[448] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔退出副本〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[449] kind=text, 現有引用=False

暫存槽(22)=傳回值

### SL[450] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((10000))

### SL[451] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔按鈕點擊進本〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[452] kind=text, 現有引用=False

暫存槽(23)=傳回值

### SL[453] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[454] kind=text, 現有引用=False

傳回值=暫存槽(24)

### SL[455] kind=text, 現有引用=False

〔重新開始〕

### SL[456] kind=text, 現有引用=False

暫存槽(24)=0

### SL[457] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[458] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[459] kind=text, 現有引用=False

傳回值=暫存槽(25)

### SL[460] kind=text, 現有引用=False

〔層數〕

### SL[461] kind=text, 現有引用=False

暫存槽(25)=1

### SL[462] kind=text, 現有引用=False

傳回值=暫存槽(26)

### SL[463] kind=text, 現有引用=False

〔找到紫金〕

### SL[464] kind=text, 現有引用=False

暫存槽(26)=0

### SL[465] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("-----主控-----开始打怪一层"))

### SL[466] kind=text, 現有引用=False

傳回值=暫存槽(27)

### SL[467] kind=text, 現有引用=False

〔重新開始〕

### SL[468] kind=text, 現有引用=False

暫存槽(27)=0

### SL[469] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔開始打怪〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[470] kind=text, 現有引用=False

暫存槽(28)=傳回值

### SL[471] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[472] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("----------结束循环-----------"))

