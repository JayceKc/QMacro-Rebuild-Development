# 08 挖礦採花：缺失初始化線索

這是線索清單，尚未將未引用字串當作原始指令。
SL 截止點只供閱讀；它不是函式入口或完整缺失來源的界線。編譯器可能把右側表達式配置在截止點之後。

## 保留的位置群組

L00000..L00006 loc=0 flags=0 count=7 ops=30,30,30,30,30,30,29
L00007..L00007 loc=1 flags=0 count=1 ops=255
L00008..L00008 loc=5 flags=0 count=1 ops=255
L00009..L00009 loc=6 flags=0 count=1 ops=255
L00010..L00010 loc=7 flags=0 count=1 ops=255
L00011..L00011 loc=9 flags=0 count=1 ops=255
L00012..L00012 loc=10 flags=0 count=1 ops=255
L00013..L00013 loc=11 flags=0 count=1 ops=255
L00014..L00014 loc=12 flags=0 count=1 ops=255
L00015..L00015 loc=13 flags=0 count=1 ops=255
L00016..L00016 loc=15 flags=0 count=1 ops=255
L00017..L00017 loc=16 flags=0 count=1 ops=255
L00018..L00018 loc=18 flags=0 count=1 ops=255
L00019..L00019 loc=19 flags=0 count=1 ops=255
L00020..L00020 loc=20 flags=0 count=1 ops=255
L00021..L00021 loc=21 flags=0 count=1 ops=255
L00022..L00023 loc=23 flags=0 count=2 ops=255,255
L00024..L00024 loc=24 flags=0 count=1 ops=255
L00025..L00025 loc=25 flags=0 count=1 ops=255
L00026..L00026 loc=26 flags=0 count=1 ops=255
L00027..L00027 loc=28 flags=0 count=1 ops=255
L00028..L00028 loc=29 flags=0 count=1 ops=255
L00029..L00029 loc=30 flags=0 count=1 ops=255
L00030..L00030 loc=31 flags=0 count=1 ops=255
L00031..L00031 loc=32 flags=0 count=1 ops=255
L00032..L00032 loc=33 flags=0 count=1 ops=255
L00033..L00033 loc=34 flags=0 count=1 ops=255
L00034..L00034 loc=35 flags=0 count=1 ops=255
L00035..L00037 loc=36 flags=0 count=3 ops=255,255,255
L00038..L00038 loc=37 flags=0 count=1 ops=255
L00039..L00041 loc=38 flags=0 count=3 ops=255,255,255
L00042..L00042 loc=39 flags=0 count=1 ops=255
L00043..L00045 loc=40 flags=0 count=3 ops=255,255,255
L00046..L00046 loc=41 flags=0 count=1 ops=255
L00047..L00049 loc=42 flags=0 count=3 ops=255,255,255
L00050..L00050 loc=43 flags=0 count=1 ops=255
L00051..L00054 loc=44 flags=0 count=4 ops=255,255,255,255
L00055..L00055 loc=45 flags=0 count=1 ops=255
L00056..L00056 loc=46 flags=0 count=1 ops=255
L00057..L00057 loc=47 flags=0 count=1 ops=255
L00058..L00058 loc=49 flags=0 count=1 ops=255
L00059..L00062 loc=50 flags=0 count=4 ops=255,255,255,255
L00063..L00063 loc=51 flags=0 count=1 ops=255
L00064..L00064 loc=52 flags=0 count=1 ops=255
L00065..L00065 loc=53 flags=0 count=1 ops=255
L00066..L00066 loc=57 flags=0 count=1 ops=255
L00067..L00067 loc=58 flags=0 count=1 ops=255
L00068..L00068 loc=59 flags=0 count=1 ops=255
L00069..L00069 loc=60 flags=0 count=1 ops=255
L00070..L00070 loc=61 flags=0 count=1 ops=255
L00071..L00071 loc=62 flags=0 count=1 ops=255
L00072..L00072 loc=63 flags=0 count=1 ops=255
L00073..L00073 loc=64 flags=0 count=1 ops=255
L00074..L00074 loc=65 flags=0 count=1 ops=255
L00075..L00075 loc=66 flags=0 count=1 ops=255
L00076..L00076 loc=67 flags=0 count=1 ops=255
L00077..L00078 loc=68 flags=0 count=2 ops=255,255
L00079..L00079 loc=69 flags=0 count=1 ops=255
L00080..L00089 loc=70 flags=0 count=10 ops=255,255,255,255,255,255,255,255,255,255
L00090..L00090 loc=74 flags=0 count=1 ops=255
L00091..L00091 loc=75 flags=0 count=1 ops=255
L00092..L00092 loc=76 flags=0 count=1 ops=255
L00093..L00093 loc=77 flags=0 count=1 ops=255
L00094..L00094 loc=78 flags=0 count=1 ops=255
L00095..L00095 loc=79 flags=0 count=1 ops=255
L00096..L00096 loc=80 flags=0 count=1 ops=255
L00097..L00097 loc=81 flags=0 count=1 ops=255
L00098..L00098 loc=82 flags=0 count=1 ops=255
L00099..L00099 loc=83 flags=0 count=1 ops=255
L00100..L00101 loc=85 flags=0 count=2 ops=255,255
L00102..L00102 loc=87 flags=0 count=1 ops=255
L00103..L00104 loc=88 flags=0 count=2 ops=255,255
L00105..L00105 loc=89 flags=0 count=1 ops=255
L00106..L00108 loc=90 flags=0 count=3 ops=255,255,255
L00109..L00110 loc=91 flags=0 count=2 ops=255,255
L00111..L00111 loc=92 flags=0 count=1 ops=255
L00112..L00114 loc=93 flags=0 count=3 ops=255,255,255
L00115..L00115 loc=94 flags=0 count=1 ops=255
L00116..L00116 loc=95 flags=0 count=1 ops=255
L00117..L00118 loc=96 flags=0 count=2 ops=255,255
L00119..L00119 loc=97 flags=0 count=1 ops=255
L00120..L00122 loc=98 flags=0 count=3 ops=255,255,255
L00123..L00123 loc=100 flags=0 count=1 ops=255
L00124..L00124 loc=101 flags=0 count=1 ops=255
L00125..L00125 loc=102 flags=0 count=1 ops=255
L00126..L00126 loc=103 flags=0 count=1 ops=255
L00127..L00127 loc=105 flags=0 count=1 ops=255
L00128..L00129 loc=106 flags=0 count=2 ops=255,255
L00130..L00130 loc=107 flags=0 count=1 ops=255
L00131..L00131 loc=108 flags=0 count=1 ops=255
L00132..L00132 loc=109 flags=0 count=1 ops=255
L00133..L00133 loc=110 flags=0 count=1 ops=255
L00134..L00134 loc=111 flags=0 count=1 ops=255
L00135..L00135 loc=112 flags=0 count=1 ops=255
L00136..L00136 loc=113 flags=0 count=1 ops=255
L00137..L00137 loc=114 flags=0 count=1 ops=255
L00138..L00138 loc=115 flags=0 count=1 ops=255
L00139..L00140 loc=116 flags=0 count=2 ops=255,255
L00141..L00141 loc=117 flags=0 count=1 ops=255
L00142..L00142 loc=118 flags=0 count=1 ops=255
L00143..L00143 loc=119 flags=0 count=1 ops=255
L00144..L00144 loc=120 flags=0 count=1 ops=255
L00145..L00145 loc=121 flags=0 count=1 ops=255
L00146..L00146 loc=122 flags=0 count=1 ops=255
L00147..L00147 loc=123 flags=0 count=1 ops=255
L00148..L00148 loc=124 flags=0 count=1 ops=255
L00149..L00149 loc=125 flags=0 count=1 ops=255
L00150..L00150 loc=126 flags=0 count=1 ops=255
L00151..L00151 loc=127 flags=0 count=1 ops=255
L00152..L00152 loc=128 flags=0 count=1 ops=255
L00153..L00153 loc=129 flags=0 count=1 ops=255
L00154..L00154 loc=130 flags=0 count=1 ops=255
L00155..L00155 loc=131 flags=0 count=1 ops=255
L00156..L00156 loc=132 flags=0 count=1 ops=255
L00157..L00157 loc=133 flags=0 count=1 ops=255
L00158..L00158 loc=134 flags=0 count=1 ops=255
L00159..L00159 loc=135 flags=0 count=1 ops=255
L00160..L00160 loc=136 flags=0 count=1 ops=255
L00161..L00161 loc=137 flags=0 count=1 ops=255
L00162..L00162 loc=138 flags=0 count=1 ops=255
L00163..L00163 loc=139 flags=0 count=1 ops=255
L00164..L00164 loc=141 flags=0 count=1 ops=255
L00165..L00165 loc=142 flags=0 count=1 ops=255
L00166..L00166 loc=143 flags=0 count=1 ops=255
L00167..L00167 loc=144 flags=0 count=1 ops=255
L00168..L00168 loc=145 flags=0 count=1 ops=255
L00169..L00169 loc=146 flags=0 count=1 ops=255
L00170..L00170 loc=148 flags=0 count=1 ops=255
L00171..L00172 loc=149 flags=0 count=2 ops=255,255
L00173..L00173 loc=150 flags=0 count=1 ops=255
L00174..L00174 loc=151 flags=0 count=1 ops=255
L00175..L00175 loc=152 flags=0 count=1 ops=255
L00176..L00176 loc=153 flags=0 count=1 ops=255
L00177..L00177 loc=154 flags=0 count=1 ops=255
L00178..L00178 loc=155 flags=0 count=1 ops=255
L00179..L00179 loc=156 flags=0 count=1 ops=255
L00180..L00180 loc=157 flags=0 count=1 ops=255
L00181..L00181 loc=158 flags=0 count=1 ops=255
L00182..L00183 loc=159 flags=0 count=2 ops=255,255
L00184..L00184 loc=160 flags=0 count=1 ops=255
L00185..L00185 loc=161 flags=0 count=1 ops=255
L00186..L00186 loc=162 flags=0 count=1 ops=255
L00187..L00187 loc=163 flags=0 count=1 ops=255
L00188..L00188 loc=164 flags=0 count=1 ops=255
L00189..L00189 loc=165 flags=0 count=1 ops=255
L00190..L00190 loc=166 flags=0 count=1 ops=255
L00191..L00191 loc=167 flags=0 count=1 ops=255
L00192..L00192 loc=168 flags=0 count=1 ops=255
L00193..L00193 loc=169 flags=0 count=1 ops=255
L00194..L00194 loc=170 flags=0 count=1 ops=255
L00195..L00195 loc=171 flags=0 count=1 ops=255
L00196..L00196 loc=172 flags=0 count=1 ops=255
L00197..L00197 loc=173 flags=0 count=1 ops=255
L00198..L00198 loc=174 flags=0 count=1 ops=255
L00199..L00199 loc=175 flags=0 count=1 ops=255
L00200..L00200 loc=176 flags=0 count=1 ops=255
L00201..L00201 loc=177 flags=0 count=1 ops=255
L00202..L00202 loc=178 flags=0 count=1 ops=255
L00203..L00203 loc=179 flags=0 count=1 ops=255
L00204..L00204 loc=180 flags=0 count=1 ops=255
L00205..L00205 loc=181 flags=0 count=1 ops=255
L00206..L00206 loc=182 flags=0 count=1 ops=255
L00207..L00207 loc=183 flags=0 count=1 ops=255
L00208..L00208 loc=185 flags=0 count=1 ops=255
L00209..L00209 loc=186 flags=0 count=1 ops=255
L00210..L00210 loc=187 flags=0 count=1 ops=255
L00211..L00211 loc=190 flags=0 count=1 ops=255
L00212..L00213 loc=191 flags=0 count=2 ops=255,255
L00214..L00214 loc=192 flags=0 count=1 ops=255
L00215..L00215 loc=193 flags=0 count=1 ops=255
L00216..L00218 loc=194 flags=0 count=3 ops=255,255,255
L00219..L00219 loc=195 flags=0 count=1 ops=255
L00220..L00220 loc=196 flags=0 count=1 ops=255
L00221..L00221 loc=197 flags=0 count=1 ops=255
L00222..L00223 loc=198 flags=0 count=2 ops=255,255
L00224..L00224 loc=199 flags=0 count=1 ops=255
L00225..L00225 loc=200 flags=0 count=1 ops=255
L00226..L00226 loc=201 flags=0 count=1 ops=255
L00227..L00227 loc=202 flags=0 count=1 ops=255
L00228..L00228 loc=203 flags=0 count=1 ops=255
L00229..L00229 loc=204 flags=0 count=1 ops=255
L00230..L00230 loc=205 flags=0 count=1 ops=255
L00231..L00231 loc=206 flags=0 count=1 ops=255
L00232..L00232 loc=207 flags=0 count=1 ops=255
L00233..L00233 loc=208 flags=0 count=1 ops=255
L00234..L00234 loc=209 flags=0 count=1 ops=255
L00235..L00235 loc=210 flags=0 count=1 ops=255
L00236..L00236 loc=211 flags=0 count=1 ops=255
L00237..L00237 loc=212 flags=0 count=1 ops=255
L00238..L00238 loc=213 flags=0 count=1 ops=255
L00239..L00239 loc=214 flags=0 count=1 ops=255
L00240..L00240 loc=215 flags=0 count=1 ops=255
L00241..L00241 loc=216 flags=0 count=1 ops=255
L00242..L00242 loc=217 flags=0 count=1 ops=255
L00243..L00243 loc=218 flags=0 count=1 ops=255
L00244..L00244 loc=219 flags=0 count=1 ops=255
L00245..L00245 loc=220 flags=0 count=1 ops=255
L00246..L00246 loc=221 flags=0 count=1 ops=255
L00247..L00247 loc=222 flags=0 count=1 ops=255
L00248..L00248 loc=223 flags=0 count=1 ops=255
L00249..L00249 loc=224 flags=0 count=1 ops=255
L00250..L00250 loc=225 flags=0 count=1 ops=255
L00251..L00251 loc=230 flags=0 count=1 ops=255
L00252..L00252 loc=231 flags=0 count=1 ops=255
L00253..L00253 loc=232 flags=0 count=1 ops=255
L00254..L00255 loc=233 flags=0 count=2 ops=255,255
L00256..L00256 loc=234 flags=0 count=1 ops=255
L00257..L00257 loc=235 flags=0 count=1 ops=255
L00258..L00258 loc=236 flags=0 count=1 ops=255
L00259..L00259 loc=237 flags=0 count=1 ops=255
L00260..L00260 loc=238 flags=0 count=1 ops=255
L00261..L00261 loc=239 flags=0 count=1 ops=255
L00262..L00262 loc=240 flags=0 count=1 ops=255
L00263..L00264 loc=242 flags=0 count=2 ops=255,255
L00265..L00265 loc=244 flags=0 count=1 ops=255
L00266..L00267 loc=245 flags=0 count=2 ops=255,255
L00268..L00268 loc=246 flags=0 count=1 ops=255
L00269..L00271 loc=247 flags=0 count=3 ops=255,255,255
L00272..L00273 loc=248 flags=0 count=2 ops=255,255
L00274..L00274 loc=249 flags=0 count=1 ops=255
L00275..L00277 loc=250 flags=0 count=3 ops=255,255,255
L00278..L00278 loc=251 flags=0 count=1 ops=255
L00279..L00279 loc=252 flags=0 count=1 ops=255
L00280..L00281 loc=253 flags=0 count=2 ops=255,255
L00282..L00282 loc=254 flags=0 count=1 ops=255
L00283..L00285 loc=255 flags=0 count=3 ops=255,255,255
L00286..L00286 loc=256 flags=0 count=1 ops=255
L00287..L00287 loc=258 flags=0 count=1 ops=255
L00288..L00288 loc=259 flags=0 count=1 ops=255
L00289..L00289 loc=260 flags=0 count=1 ops=255
L00290..L00290 loc=261 flags=0 count=1 ops=255
L00291..L00291 loc=263 flags=0 count=1 ops=255
L00292..L00293 loc=264 flags=0 count=2 ops=255,255
L00294..L00294 loc=265 flags=0 count=1 ops=255
L00295..L00295 loc=266 flags=0 count=1 ops=255
L00296..L00296 loc=267 flags=0 count=1 ops=255
L00297..L00297 loc=268 flags=0 count=1 ops=255
L00298..L00298 loc=269 flags=0 count=1 ops=255
L00299..L00299 loc=270 flags=0 count=1 ops=255
L00300..L00300 loc=271 flags=0 count=1 ops=255
L00301..L00301 loc=272 flags=0 count=1 ops=255
L00302..L00302 loc=273 flags=0 count=1 ops=255
L00303..L00303 loc=274 flags=0 count=1 ops=255
L00304..L00304 loc=275 flags=0 count=1 ops=255
L00305..L00306 loc=276 flags=0 count=2 ops=255,255
L00307..L00307 loc=277 flags=0 count=1 ops=255
L00308..L00308 loc=278 flags=0 count=1 ops=255
L00309..L00309 loc=279 flags=0 count=1 ops=255
L00310..L00310 loc=280 flags=0 count=1 ops=255
L00311..L00311 loc=281 flags=0 count=1 ops=255
L00312..L00312 loc=282 flags=0 count=1 ops=255
L00313..L00313 loc=283 flags=0 count=1 ops=255
L00314..L00314 loc=284 flags=0 count=1 ops=255
L00315..L00315 loc=285 flags=0 count=1 ops=255
L00316..L00316 loc=286 flags=0 count=1 ops=255
L00317..L00317 loc=287 flags=0 count=1 ops=255
L00318..L00318 loc=288 flags=0 count=1 ops=255
L00319..L00319 loc=289 flags=0 count=1 ops=255
L00320..L00320 loc=290 flags=0 count=1 ops=255
L00321..L00321 loc=291 flags=0 count=1 ops=255
L00322..L00322 loc=292 flags=0 count=1 ops=255
L00323..L00323 loc=293 flags=0 count=1 ops=255
L00324..L00324 loc=294 flags=0 count=1 ops=255
L00325..L00325 loc=295 flags=0 count=1 ops=255
L00326..L00326 loc=296 flags=0 count=1 ops=255
L00327..L00327 loc=297 flags=0 count=1 ops=255
L00328..L00328 loc=298 flags=0 count=1 ops=255
L00329..L00329 loc=299 flags=0 count=1 ops=255
L00330..L00330 loc=301 flags=0 count=1 ops=255
L00331..L00331 loc=302 flags=0 count=1 ops=255
L00332..L00332 loc=303 flags=0 count=1 ops=255
L00333..L00333 loc=304 flags=0 count=1 ops=255
L00334..L00334 loc=305 flags=0 count=1 ops=255
L00335..L00335 loc=306 flags=0 count=1 ops=255
L00336..L00336 loc=308 flags=0 count=1 ops=255
L00337..L00338 loc=309 flags=0 count=2 ops=255,255
L00339..L00339 loc=310 flags=0 count=1 ops=255
L00340..L00340 loc=311 flags=0 count=1 ops=255
L00341..L00341 loc=312 flags=0 count=1 ops=255
L00342..L00342 loc=313 flags=0 count=1 ops=255
L00343..L00343 loc=314 flags=0 count=1 ops=255
L00344..L00344 loc=315 flags=0 count=1 ops=255
L00345..L00345 loc=316 flags=0 count=1 ops=255
L00346..L00346 loc=317 flags=0 count=1 ops=255
L00347..L00347 loc=318 flags=0 count=1 ops=255
L00348..L00349 loc=319 flags=0 count=2 ops=255,255
L00350..L00350 loc=320 flags=0 count=1 ops=255
L00351..L00351 loc=321 flags=0 count=1 ops=255
L00352..L00352 loc=322 flags=0 count=1 ops=255
L00353..L00353 loc=323 flags=0 count=1 ops=255
L00354..L00354 loc=324 flags=0 count=1 ops=255
L00355..L00355 loc=325 flags=0 count=1 ops=255
L00356..L00356 loc=326 flags=0 count=1 ops=255
L00357..L00357 loc=327 flags=0 count=1 ops=255
L00358..L00358 loc=328 flags=0 count=1 ops=255
L00359..L00359 loc=329 flags=0 count=1 ops=255
L00360..L00360 loc=330 flags=0 count=1 ops=255
L00361..L00361 loc=331 flags=0 count=1 ops=255
L00362..L00362 loc=332 flags=0 count=1 ops=255
L00363..L00363 loc=333 flags=0 count=1 ops=255
L00364..L00364 loc=334 flags=0 count=1 ops=255
L00365..L00365 loc=335 flags=0 count=1 ops=255
L00366..L00366 loc=336 flags=0 count=1 ops=255
L00367..L00367 loc=337 flags=0 count=1 ops=255
L00368..L00368 loc=338 flags=0 count=1 ops=255
L00369..L00369 loc=339 flags=0 count=1 ops=255
L00370..L00370 loc=340 flags=0 count=1 ops=255
L00371..L00371 loc=341 flags=0 count=1 ops=255
L00372..L00372 loc=342 flags=0 count=1 ops=255
L00373..L00373 loc=343 flags=0 count=1 ops=255
L00374..L00374 loc=345 flags=0 count=1 ops=255
L00375..L00375 loc=346 flags=0 count=1 ops=255
L00376..L00376 loc=347 flags=0 count=1 ops=255
L00377..L00377 loc=349 flags=0 count=1 ops=255
L00378..L00379 loc=350 flags=0 count=2 ops=255,255
L00380..L00380 loc=351 flags=0 count=1 ops=255
L00381..L00381 loc=352 flags=0 count=1 ops=255
L00382..L00384 loc=353 flags=0 count=3 ops=255,255,255
L00385..L00385 loc=354 flags=0 count=1 ops=255
L00386..L00386 loc=355 flags=0 count=1 ops=255
L00387..L00387 loc=356 flags=0 count=1 ops=255
L00388..L00389 loc=357 flags=0 count=2 ops=255,255
L00390..L00390 loc=358 flags=0 count=1 ops=255
L00391..L00391 loc=359 flags=0 count=1 ops=255
L00392..L00392 loc=360 flags=0 count=1 ops=255
L00393..L00393 loc=361 flags=0 count=1 ops=255
L00394..L00394 loc=362 flags=0 count=1 ops=255
L00395..L00395 loc=363 flags=0 count=1 ops=255
L00396..L00396 loc=364 flags=0 count=1 ops=255
L00397..L00397 loc=365 flags=0 count=1 ops=255
L00398..L00398 loc=366 flags=0 count=1 ops=255
L00399..L00399 loc=367 flags=0 count=1 ops=255
L00400..L00400 loc=368 flags=0 count=1 ops=255
L00401..L00401 loc=369 flags=0 count=1 ops=255
L00402..L00402 loc=370 flags=0 count=1 ops=255
L00403..L00403 loc=371 flags=0 count=1 ops=255
L00404..L00404 loc=372 flags=0 count=1 ops=255
L00405..L00405 loc=373 flags=0 count=1 ops=255
L00406..L00406 loc=374 flags=0 count=1 ops=255
L00407..L00407 loc=375 flags=0 count=1 ops=255
L00408..L00408 loc=376 flags=0 count=1 ops=255
L00409..L00409 loc=377 flags=0 count=1 ops=255
L00410..L00410 loc=378 flags=0 count=1 ops=255
L00411..L00411 loc=379 flags=0 count=1 ops=255
L00412..L00412 loc=380 flags=0 count=1 ops=255
L00413..L00413 loc=381 flags=0 count=1 ops=255
L00414..L00414 loc=382 flags=0 count=1 ops=255
L00415..L00415 loc=383 flags=0 count=1 ops=255
L00416..L00416 loc=384 flags=0 count=1 ops=255
L00417..L00417 loc=389 flags=0 count=1 ops=255
L00418..L00418 loc=390 flags=0 count=1 ops=255
L00419..L00419 loc=391 flags=0 count=1 ops=255
L00420..L00421 loc=392 flags=0 count=2 ops=255,255
L00422..L00422 loc=393 flags=0 count=1 ops=255
L00423..L00423 loc=394 flags=0 count=1 ops=255
L00424..L00424 loc=395 flags=0 count=1 ops=255
L00425..L00425 loc=396 flags=0 count=1 ops=255
L00426..L00426 loc=397 flags=0 count=1 ops=255
L00427..L00427 loc=398 flags=0 count=1 ops=255
L00428..L00428 loc=399 flags=0 count=1 ops=255
L00429..L00430 loc=401 flags=0 count=2 ops=255,255
L00431..L00431 loc=403 flags=0 count=1 ops=255
L00432..L00433 loc=404 flags=0 count=2 ops=255,255
L00434..L00434 loc=405 flags=0 count=1 ops=255
L00435..L00437 loc=406 flags=0 count=3 ops=255,255,255
L00438..L00439 loc=407 flags=0 count=2 ops=255,255
L00440..L00440 loc=408 flags=0 count=1 ops=255
L00441..L00443 loc=409 flags=0 count=3 ops=255,255,255
L00444..L00444 loc=410 flags=0 count=1 ops=255
L00445..L00445 loc=411 flags=0 count=1 ops=255
L00446..L00447 loc=412 flags=0 count=2 ops=255,255
L00448..L00448 loc=413 flags=0 count=1 ops=255
L00449..L00451 loc=414 flags=0 count=3 ops=255,255,255
L00452..L00452 loc=415 flags=0 count=1 ops=255
L00453..L00453 loc=417 flags=0 count=1 ops=255
L00454..L00454 loc=418 flags=0 count=1 ops=255
L00455..L00455 loc=419 flags=0 count=1 ops=255
L00456..L00456 loc=420 flags=0 count=1 ops=255
L00457..L00457 loc=422 flags=0 count=1 ops=255
L00458..L00459 loc=423 flags=0 count=2 ops=255,255
L00460..L00460 loc=424 flags=0 count=1 ops=255
L00461..L00461 loc=425 flags=0 count=1 ops=255
L00462..L00462 loc=426 flags=0 count=1 ops=255
L00463..L00463 loc=427 flags=0 count=1 ops=255
L00464..L00464 loc=428 flags=0 count=1 ops=255
L00465..L00465 loc=429 flags=0 count=1 ops=255
L00466..L00466 loc=430 flags=0 count=1 ops=255
L00467..L00467 loc=431 flags=0 count=1 ops=255
L00468..L00468 loc=432 flags=0 count=1 ops=255
L00469..L00470 loc=433 flags=0 count=2 ops=255,255
L00471..L00471 loc=434 flags=0 count=1 ops=255
L00472..L00472 loc=435 flags=0 count=1 ops=255
L00473..L00473 loc=436 flags=0 count=1 ops=255
L00474..L00474 loc=437 flags=0 count=1 ops=255
L00475..L00475 loc=438 flags=0 count=1 ops=255
L00476..L00476 loc=439 flags=0 count=1 ops=255
L00477..L00477 loc=440 flags=0 count=1 ops=255
L00478..L00478 loc=441 flags=0 count=1 ops=255
L00479..L00479 loc=442 flags=0 count=1 ops=255
L00480..L00480 loc=443 flags=0 count=1 ops=255
L00481..L00481 loc=444 flags=0 count=1 ops=255
L00482..L00482 loc=445 flags=0 count=1 ops=255
L00483..L00483 loc=446 flags=0 count=1 ops=255
L00484..L00484 loc=447 flags=0 count=1 ops=255
L00485..L00485 loc=448 flags=0 count=1 ops=255
L00486..L00486 loc=449 flags=0 count=1 ops=255
L00487..L00487 loc=450 flags=0 count=1 ops=255
L00488..L00488 loc=451 flags=0 count=1 ops=255
L00489..L00489 loc=452 flags=0 count=1 ops=255
L00490..L00490 loc=453 flags=0 count=1 ops=255
L00491..L00491 loc=454 flags=0 count=1 ops=255
L00492..L00492 loc=455 flags=0 count=1 ops=255
L00493..L00493 loc=456 flags=0 count=1 ops=255
L00494..L00494 loc=458 flags=0 count=1 ops=255
L00495..L00495 loc=459 flags=0 count=1 ops=255
L00496..L00496 loc=460 flags=0 count=1 ops=255
L00497..L00497 loc=461 flags=0 count=1 ops=255
L00498..L00498 loc=462 flags=0 count=1 ops=255
L00499..L00499 loc=463 flags=0 count=1 ops=255
L00500..L00500 loc=465 flags=0 count=1 ops=255
L00501..L00502 loc=466 flags=0 count=2 ops=255,255
L00503..L00503 loc=467 flags=0 count=1 ops=255
L00504..L00504 loc=468 flags=0 count=1 ops=255
L00505..L00505 loc=469 flags=0 count=1 ops=255
L00506..L00506 loc=470 flags=0 count=1 ops=255

## 原 SL 字串順序

### SL[0] kind=decoded-text, 現有引用=True

Dim 暫存槽(256):Dim 目前呼叫框架,新呼叫框架:Set 目前呼叫框架=Nothing:Set 新呼叫框架=Nothing

### SL[1] kind=decoded-text, 現有引用=True

Class 框架類別_〔返回莊園〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[2] kind=decoded-text, 現有引用=True

Class 框架類別_〔工具紅了〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[3] kind=decoded-text, 現有引用=True

Class 框架類別_〔檢查活力條〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[4] kind=decoded-text, 現有引用=True

Class 框架類別_〔計算走位〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[5] kind=decoded-text, 現有引用=True

Class 框架類別_〔挖礦按G游戲〕:Dim 上層呼叫框架,函式回傳欄位,暫存槽(256):End Class

### SL[6] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[7] kind=text, 現有引用=False

SET WS=CREATEOBJECT("Wscript.Shell")

### SL[8] kind=decoded-text, 現有引用=False

Call WS.RUN("regsvr32 atl.dll /s")

### SL[9] kind=text, 現有引用=False

SET WS=nothing

### SL[10] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[11] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro\fz","fz.dll")

### SL[12] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","fzreg.dll")

### SL[13] kind=decoded-text, 現有引用=False

Call QMLibrary.ExtractAttachment("C:\users\mymacro","*.bmp")

### SL[14] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[15] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(QMLibrary.CallAPI2("C:\users\mymacro\fzreg.dll", "SetDllPathW", "C:\users\mymacro\fz\fz.dll", 0))

### SL[16] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[17] kind=text, 現有引用=False

SET DM=CREATEOBJECT("dm.dmsoft")

### SL[18] kind=decoded-text, 現有引用=False

Call DM.SETSHOWERRORMSG(0)

### SL[19] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[20] kind=decoded-text, 現有引用=False

〔版本〕=DM.VER()

### SL[21] kind=text, 現有引用=False

Sgn((〔版本〕=7.2450))

### SL[22] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("成功"))

### SL[23] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("失败"))

### SL[24] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[25] kind=empty, 現有引用=False



### SL[26] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[27] kind=decoded-text, 現有引用=False

〔鼠標〕=DM.ENABLEREALMOUSE(2,10,60)

### SL[28] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint("鼠标" & 〔鼠標〕)

### SL[29] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[30] kind=text, 現有引用=False

〔索引〕=ARRAY(0,1,2,3,4,5,6,7,8,9,10)

### SL[31] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[32] kind=text, 現有引用=False

Form1.ComboBox1.ListIndex

### SL[33] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[34] kind=text, 現有引用=False

〔功能〕=〔索引〕(暫存槽(1))

### SL[35] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[36] kind=text, 現有引用=False

Form1.ComboBox2.ListIndex

### SL[37] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[38] kind=text, 現有引用=False

〔修理〕=〔索引〕(暫存槽(1))

### SL[39] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[40] kind=text, 現有引用=False

Form1.ComboBox3.ListIndex

### SL[41] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[42] kind=text, 現有引用=False

〔完成之后〕=〔索引〕(暫存槽(1))

### SL[43] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(50)

### SL[44] kind=decoded-text, 現有引用=False

傳回值=暫存槽(1)

### SL[45] kind=text, 現有引用=False

〔天選〕

### SL[46] kind=text, 現有引用=False

暫存槽(1)=QMLibrary.GetGlobalVar("MMVerifyCode", 0)

### SL[47] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[48] kind=text, 現有引用=False

Form1.CheckBox3.Value

### SL[49] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[50] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[51] kind=text, 現有引用=False

〔沒有活力回家〕=1

### SL[52] kind=text, 現有引用=False

〔沒有活力回家〕=0

### SL[53] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[54] kind=text, 現有引用=False

Form1.CheckBox2.Value

### SL[55] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[56] kind=text, 現有引用=False

Sgn(暫存槽(1)=1)

### SL[57] kind=text, 現有引用=False

〔沒有耐久回家〕=1

### SL[58] kind=text, 現有引用=False

〔沒有耐久回家〕=0

### SL[59] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[60] kind=text, 現有引用=False

Randomize

### SL[61] kind=text, 現有引用=False

YDX=INT(5*RND+35)

### SL[62] kind=text, 現有引用=False

Randomize

### SL[63] kind=text, 現有引用=False

YDY=INT(10*RND+10)

### SL[64] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[65] kind=decoded-text, 現有引用=False

Call DM.MOVETO(YDX,YDY)

### SL[66] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((300))

### SL[67] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[68] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((2000))

### SL[69] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint((">>>>>>脚本启动"))

### SL[70] kind=text, 現有引用=False

Sgn(〔功能〕=1 or 〔功能〕=2 or 〔功能〕=3)

### SL[71] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[72] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔挖礦按G游戲〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[73] kind=text, 現有引用=False

暫存槽(1)=傳回值

### SL[74] kind=text, 現有引用=False

傳回值=暫存槽(2)

### SL[75] kind=text, 現有引用=False

〔挖礦按G游戲ID〕

### SL[76] kind=text, 現有引用=False

暫存槽(2)=暫存槽(1)

### SL[77] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(1000)

### SL[78] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[79] kind=text, 現有引用=False

XX1=1743.0

### SL[80] kind=text, 現有引用=False

YY1=168.0

### SL[81] kind=text, 現有引用=False

〔派〕=3.1415926

### SL[82] kind=text, 現有引用=False

〔無目標〕=0

### SL[83] kind=text, 現有引用=False

〔花兒名字〕=0

### SL[84] kind=text, 現有引用=False

〔礦物名字〕=0

### SL[85] kind=text, 現有引用=False

〔走位〕=0

### SL[86] kind=text, 現有引用=False

〔無綠色〕=0

### SL[87] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[88] kind=text, 現有引用=False

Sgn(〔功能〕=0)

### SL[89] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[90] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[91] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[92] kind=text, 現有引用=False

〔天選〕

### SL[93] kind=decoded-text, 現有引用=False

暫存槽(1)=傳回值

### SL[94] kind=text, 現有引用=False

DM_RET=DM.FINDCOLOR(160,1,260,25,暫存槽(1) & "-151515",0.9,0,INTX,INTY)

### SL[95] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[96] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[97] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔檢查活力條〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[98] kind=text, 現有引用=False

暫存槽(2)=傳回值

### SL[99] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[100] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1364,55,1476,119,"C:\users\mymacro\shgj1.bmp|C:\users\mymacro\shgj2.bmp|C:\users\mymacro\shgj3.bmp|C:\users\mymacro\shgj4.bmp","151515",0.9,0,INTX,INTY)

### SL[101] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[102] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[103] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔工具紅了〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[104] kind=text, 現有引用=False

暫存槽(3)=傳回值

### SL[105] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[106] kind=text, 現有引用=False

INTXX=0

### SL[107] kind=text, 現有引用=False

INTYY=0

### SL[108] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[109] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(658,208,1389,775,"C:\users\mymacro\douya1.bmp|C:\users\mymacro\douya2.bmp","151515",0.9,0,INTXX,INTYY)

### SL[110] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[111] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到豆芽图标"))

### SL[112] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[113] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("G",g_iSimulateModeInVBSBlock,1)

### SL[114] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[115] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("G",g_iSimulateModeInVBSBlock,1)

### SL[116] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((2000))

### SL[117] kind=text, 現有引用=False

INTXX=0

### SL[118] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[119] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(658,208,1389,775,"C:\users\mymacro\douya1.bmp|C:\users\mymacro\douya2.bmp","151515",0.9,0,INTXX,INTYY)

### SL[120] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[121] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到豆芽图标"))

### SL[122] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[123] kind=decoded-text, 現有引用=False

Call DM.MOVETOEX(860,440,200,200)

### SL[124] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[125] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[126] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[127] kind=text, 現有引用=False

Randomize

### SL[128] kind=text, 現有引用=False

YC=INT(116*RND+66)

### SL[129] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[130] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Q",g_iSimulateModeInVBSBlock,1)

### SL[131] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[132] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("F",g_iSimulateModeInVBSBlock,1)

### SL[133] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[134] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("E",g_iSimulateModeInVBSBlock,1)

### SL[135] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[136] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("A",g_iSimulateModeInVBSBlock,1)

### SL[137] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[138] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("D",g_iSimulateModeInVBSBlock,1)

### SL[139] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[140] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("R",g_iSimulateModeInVBSBlock,1)

### SL[141] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[142] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[143] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[144] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[145] kind=text, 現有引用=False

〔花兒名字〕=0

### SL[146] kind=text, 現有引用=False

〔走位〕=0

### SL[147] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[148] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[149] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1,1,1920,977,"C:\users\mymacro\mingzi1.bmp|C:\users\mymacro\mingzi2.bmp|C:\users\mymacro\mingzi3.bmp|C:\users\mymacro\mingzi4.bmp|C:\users\mymacro\mingzi5.bmp|C:\users\mymacro\mingzi6.bmp","050505",0.9,0,INTXX,INTYY)

### SL[150] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[151] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[152] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到花名字"))

### SL[153] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[154] kind=decoded-text, 現有引用=False

Call DM.MOVETO(INTXX,INTYY)

### SL[155] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[156] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(2,g_iSimulateModeInVBSBlock,1)

### SL[157] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[158] kind=text, 現有引用=False

〔花兒名字〕=〔花兒名字〕+1

### SL[159] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[160] kind=text, 現有引用=False

Sgn(〔花兒名字〕>5)

### SL[161] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[162] kind=text, 現有引用=False

〔花兒名字〕=0

### SL[163] kind=text, 現有引用=False

〔走位〕=0

### SL[164] kind=decoded-text, 現有引用=False

Call DM.MOVETOEX(860,440,200,200)

### SL[165] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[166] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[167] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[168] kind=text, 現有引用=False

Randomize

### SL[169] kind=text, 現有引用=False

YC=INT(116*RND+66)

### SL[170] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[171] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Q",g_iSimulateModeInVBSBlock,1)

### SL[172] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[173] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("F",g_iSimulateModeInVBSBlock,1)

### SL[174] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[175] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("E",g_iSimulateModeInVBSBlock,1)

### SL[176] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[177] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("A",g_iSimulateModeInVBSBlock,1)

### SL[178] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[179] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("D",g_iSimulateModeInVBSBlock,1)

### SL[180] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[181] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("R",g_iSimulateModeInVBSBlock,1)

### SL[182] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[183] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[184] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[185] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((700))

### SL[186] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[187] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDCOLOR(1593,38,1891,296,"88B53B-030303|89B83F-030303|95BC4C-030303|85AE3F-030303|85B336-030303|88AF41-030303",1,4,INTXX,INTYY)

### SL[188] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[189] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到小地图叶子"))

### SL[190] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[191] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔計算走位〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[192] kind=text, 現有引用=False

暫存槽(4)=傳回值

### SL[193] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[194] kind=text, 現有引用=False

〔走位〕=〔走位〕+1

### SL[195] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[196] kind=text, 現有引用=False

Sgn(〔走位〕>10)

### SL[197] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[198] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Space",g_iSimulateModeInVBSBlock,1)

### SL[199] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[200] kind=decoded-text, 現有引用=False

Call DM.MOVETOEX(860,440,200,200)

### SL[201] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[202] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[203] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[204] kind=text, 現有引用=False

〔走位〕=5

### SL[205] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[206] kind=text, 現有引用=False

Randomize

### SL[207] kind=text, 現有引用=False

YC=INT(116*RND+66)

### SL[208] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[209] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Q",g_iSimulateModeInVBSBlock,1)

### SL[210] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[211] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("F",g_iSimulateModeInVBSBlock,1)

### SL[212] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[213] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("E",g_iSimulateModeInVBSBlock,1)

### SL[214] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[215] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("A",g_iSimulateModeInVBSBlock,1)

### SL[216] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[217] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("D",g_iSimulateModeInVBSBlock,1)

### SL[218] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[219] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("R",g_iSimulateModeInVBSBlock,1)

### SL[220] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[221] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[222] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[223] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(500)

### SL[224] kind=text, 現有引用=False

〔無綠色〕=〔無綠色〕+1

### SL[225] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(500)

### SL[226] kind=text, 現有引用=False

Sgn(〔無綠色〕>=3)

### SL[227] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[228] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Esc",g_iSimulateModeInVBSBlock,1)

### SL[229] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[230] kind=text, 現有引用=False

〔無綠色〕=0

### SL[231] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(4000)

### SL[232] kind=text, 現有引用=False

Sgn(〔功能〕=1)

### SL[233] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[234] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[235] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[236] kind=text, 現有引用=False

〔天選〕

### SL[237] kind=decoded-text, 現有引用=False

暫存槽(5)=傳回值

### SL[238] kind=text, 現有引用=False

DM_RET=DM.FINDCOLOR(160,1,260,25,暫存槽(5) & "-151515",0.9,0,INTX,INTY)

### SL[239] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[240] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[241] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔檢查活力條〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[242] kind=text, 現有引用=False

暫存槽(6)=傳回值

### SL[243] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[244] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1364,55,1476,119,"C:\users\mymacro\shgj1.bmp|C:\users\mymacro\shgj2.bmp|C:\users\mymacro\shgj3.bmp|C:\users\mymacro\shgj4.bmp","151515",0.9,0,INTX,INTY)

### SL[245] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[246] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[247] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔工具紅了〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[248] kind=text, 現有引用=False

暫存槽(7)=傳回值

### SL[249] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[250] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[251] kind=text, 現有引用=False

INTXX=0

### SL[252] kind=text, 現有引用=False

INTYY=0

### SL[253] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[254] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(658,208,1389,775,"C:\users\mymacro\chutou1.bmp|C:\users\mymacro\chutou2.bmp","151515",0.9,0,INTXX,INTYY)

### SL[255] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[256] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到锄头图标"))

### SL[257] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[258] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[259] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((400))

### SL[260] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("G",g_iSimulateModeInVBSBlock,1)

### SL[261] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[262] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("G",g_iSimulateModeInVBSBlock,1)

### SL[263] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((2000))

### SL[264] kind=text, 現有引用=False

INTXX=0

### SL[265] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[266] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(658,208,1389,775,"C:\users\mymacro\chutou1.bmp|C:\users\mymacro\chutou2.bmp","151515",0.9,0,INTXX,INTYY)

### SL[267] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[268] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到锄头图标"))

### SL[269] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[270] kind=decoded-text, 現有引用=False

Call DM.MOVETOEX(860,440,200,200)

### SL[271] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[272] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[273] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[274] kind=text, 現有引用=False

Randomize

### SL[275] kind=text, 現有引用=False

YC=INT(116*RND+66)

### SL[276] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[277] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Q",g_iSimulateModeInVBSBlock,1)

### SL[278] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[279] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("F",g_iSimulateModeInVBSBlock,1)

### SL[280] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[281] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("E",g_iSimulateModeInVBSBlock,1)

### SL[282] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[283] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("A",g_iSimulateModeInVBSBlock,1)

### SL[284] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[285] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("D",g_iSimulateModeInVBSBlock,1)

### SL[286] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[287] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("R",g_iSimulateModeInVBSBlock,1)

### SL[288] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[289] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[290] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[291] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[292] kind=text, 現有引用=False

〔礦物名字〕=0

### SL[293] kind=text, 現有引用=False

〔走位〕=0

### SL[294] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[295] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[296] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1,1,1920,977,"C:\users\mymacro\kwmingzi1.bmp|C:\users\mymacro\kwmingzi2.bmp|C:\users\mymacro\kwmingzi3.bmp|C:\users\mymacro\kwmingzi4.bmp|C:\users\mymacro\kwmingzi5.bmp|C:\users\mymacro\kwmingzi6.bmp|C:\users\mymacro\kwmingzi7.bmp|C:\users\mymacro\kwmingzi8.bmp|C:\users\mymacro\kwmingzi9.bmp|C:\users\mymacro\kwmingzi10.bmp","050505",0.9,0,INTXX,INTYY)

### SL[297] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[298] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[299] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到矿物名字"))

### SL[300] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[301] kind=decoded-text, 現有引用=False

Call DM.MOVETO(INTXX,INTYY)

### SL[302] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[303] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(2,g_iSimulateModeInVBSBlock,1)

### SL[304] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[305] kind=text, 現有引用=False

〔礦物名字〕=〔礦物名字〕+1

### SL[306] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[307] kind=text, 現有引用=False

Sgn(〔礦物名字〕>5)

### SL[308] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[309] kind=text, 現有引用=False

〔礦物名字〕=0

### SL[310] kind=text, 現有引用=False

〔走位〕=0

### SL[311] kind=decoded-text, 現有引用=False

Call DM.MOVETOEX(860,440,200,200)

### SL[312] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[313] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[314] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[315] kind=text, 現有引用=False

Randomize

### SL[316] kind=text, 現有引用=False

YC=INT(116*RND+66)

### SL[317] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[318] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Q",g_iSimulateModeInVBSBlock,1)

### SL[319] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[320] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("F",g_iSimulateModeInVBSBlock,1)

### SL[321] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[322] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("E",g_iSimulateModeInVBSBlock,1)

### SL[323] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[324] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("A",g_iSimulateModeInVBSBlock,1)

### SL[325] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[326] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("D",g_iSimulateModeInVBSBlock,1)

### SL[327] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[328] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("R",g_iSimulateModeInVBSBlock,1)

### SL[329] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[330] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[331] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[332] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((700))

### SL[333] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[334] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDCOLOR(1593,38,1891,296,"38B8EE-030303|117EB7-030303|2FAFDA-030303|2167BC-030303|0D5492-030303|115C86-030303",1,4,INTXX,INTYY)

### SL[335] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[336] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到小地图矿图标"))

### SL[337] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[338] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔計算走位〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[339] kind=text, 現有引用=False

暫存槽(8)=傳回值

### SL[340] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[341] kind=text, 現有引用=False

〔走位〕=〔走位〕+1

### SL[342] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[343] kind=text, 現有引用=False

Sgn(〔走位〕>10)

### SL[344] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[345] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Space",g_iSimulateModeInVBSBlock,1)

### SL[346] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[347] kind=decoded-text, 現有引用=False

Call DM.MOVETOEX(860,440,200,200)

### SL[348] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[349] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[350] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[351] kind=text, 現有引用=False

〔走位〕=5

### SL[352] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[353] kind=text, 現有引用=False

Randomize

### SL[354] kind=text, 現有引用=False

YC=INT(116*RND+66)

### SL[355] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[356] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Q",g_iSimulateModeInVBSBlock,1)

### SL[357] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[358] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("F",g_iSimulateModeInVBSBlock,1)

### SL[359] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[360] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("E",g_iSimulateModeInVBSBlock,1)

### SL[361] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[362] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("A",g_iSimulateModeInVBSBlock,1)

### SL[363] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[364] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("D",g_iSimulateModeInVBSBlock,1)

### SL[365] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[366] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("R",g_iSimulateModeInVBSBlock,1)

### SL[367] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[368] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[369] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[370] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(500)

### SL[371] kind=text, 現有引用=False

〔無綠色〕=〔無綠色〕+1

### SL[372] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(500)

### SL[373] kind=text, 現有引用=False

Sgn(〔無綠色〕>=3)

### SL[374] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[375] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Esc",g_iSimulateModeInVBSBlock,1)

### SL[376] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[377] kind=text, 現有引用=False

〔無綠色〕=0

### SL[378] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(4000)

### SL[379] kind=text, 現有引用=False

Sgn(〔功能〕=2)

### SL[380] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[381] kind=text, 現有引用=False

Sgn(vbTrue)

### SL[382] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[383] kind=text, 現有引用=False

〔天選〕

### SL[384] kind=decoded-text, 現有引用=False

暫存槽(9)=傳回值

### SL[385] kind=text, 現有引用=False

DM_RET=DM.FINDCOLOR(160,1,260,25,暫存槽(9) & "-151515",0.9,0,INTX,INTY)

### SL[386] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[387] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[388] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔檢查活力條〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[389] kind=text, 現有引用=False

暫存槽(10)=傳回值

### SL[390] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[391] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1364,55,1476,119,"C:\users\mymacro\shgj1.bmp|C:\users\mymacro\shgj2.bmp|C:\users\mymacro\shgj3.bmp|C:\users\mymacro\shgj4.bmp","151515",0.9,0,INTX,INTY)

### SL[392] kind=text, 現有引用=False

Sgn((INTX>0))

### SL[393] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[394] kind=text, 現有引用=False

Set 新呼叫框架=New 框架類別_〔工具紅了〕:Set 新呼叫框架.上層呼叫框架=目前呼叫框架:Set 目前呼叫框架=新呼叫框架

### SL[395] kind=text, 現有引用=False

暫存槽(11)=傳回值

### SL[396] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay(100)

### SL[397] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[398] kind=text, 現有引用=False

INTXX=0

### SL[399] kind=text, 現有引用=False

INTYY=0

### SL[400] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[401] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(658,208,1389,775,"C:\users\mymacro\chutou1.bmp|C:\users\mymacro\douya1.bmp|C:\users\mymacro\douya2.bmp|C:\users\mymacro\chutou2.bmp","151515",0.9,0,INTXX,INTYY)

### SL[402] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[403] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到双采图标"))

### SL[404] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[405] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("G",g_iSimulateModeInVBSBlock,1)

### SL[406] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[407] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("G",g_iSimulateModeInVBSBlock,1)

### SL[408] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((2000))

### SL[409] kind=text, 現有引用=False

INTXX=0

### SL[410] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((1000))

### SL[411] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(658,208,1389,775,"C:\users\mymacro\chutou1.bmp|C:\users\mymacro\douya1.bmp|C:\users\mymacro\douya2.bmp|C:\users\mymacro\chutou2.bmp","151515",0.9,0,INTXX,INTYY)

### SL[412] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[413] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到双采图标"))

### SL[414] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[415] kind=decoded-text, 現有引用=False

Call DM.MOVETOEX(860,440,200,200)

### SL[416] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[417] kind=decoded-text, 現有引用=False

Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)

### SL[418] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((200))

### SL[419] kind=text, 現有引用=False

Randomize

### SL[420] kind=text, 現有引用=False

YC=INT(116*RND+66)

### SL[421] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[422] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("Q",g_iSimulateModeInVBSBlock,1)

### SL[423] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[424] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("F",g_iSimulateModeInVBSBlock,1)

### SL[425] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[426] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("E",g_iSimulateModeInVBSBlock,1)

### SL[427] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[428] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("A",g_iSimulateModeInVBSBlock,1)

### SL[429] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[430] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("D",g_iSimulateModeInVBSBlock,1)

### SL[431] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[432] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("R",g_iSimulateModeInVBSBlock,1)

### SL[433] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[434] kind=decoded-text, 現有引用=False

Call QMLibrary.KeyPress("S",g_iSimulateModeInVBSBlock,1)

### SL[435] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((YC))

### SL[436] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((3000))

### SL[437] kind=text, 現有引用=False

〔雙采名字〕=0

### SL[438] kind=text, 現有引用=False

〔走位〕=0

### SL[439] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[440] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((100))

### SL[441] kind=decoded-text, 現有引用=False

DM_RET=DM.FINDPIC(1,1,1920,977,"C:\users\mymacro\kwmingzi1.bmp|C:\users\mymacro\mingzi1.bmp|C:\users\mymacro\mingzi2.bmp|C:\users\mymacro\mingzi4.bmp|C:\users\mymacro\kwmingzi2.bmp|C:\users\mymacro\kwmingzi3.bmp|C:\users\mymacro\kwmingzi4.bmp|C:\users\mymacro\mingzi3.bmp|C:\users\mymacro\kwmingzi5.bmp|C:\users\mymacro\kwmingzi6.bmp|C:\users\mymacro\kwmingzi7.bmp|C:\users\mymacro\kwmingzi8.bmp|C:\users\mymacro\kwmingzi9.bmp|C:\users\mymacro\kwmingzi10.bmp","050505",0.9,0,INTXX,INTYY)

### SL[442] kind=text, 現有引用=False

Sgn((INTXX>0))

### SL[443] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[444] kind=decoded-text, 現有引用=False

Call QMLibrary.TracePrint(("找到双采名字"))

### SL[445] kind=decoded-text, 現有引用=False

Call QMLibrary.Delay((50))

### SL[446] kind=decoded-text, 現有引用=False

Call DM.MOVETO(INTXX,INTYY)

