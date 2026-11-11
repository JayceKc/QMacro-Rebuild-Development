"""Recover the original embedded VBScript library as inert text, never execute it."""
from pathlib import Path
import collections,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/runner-vbs-library';OUT.mkdir(exist_ok=True)
def main():
    image=ROOT/'work/qmacro-host-image-current/runner.image-pages.bin';data=image.read_bytes()
    at=data.index(b'Function GetCursorPos(');start=data.rfind(b'\0',0,at)+1;end=data.index(b'\0',at);raw=data[start:end]
    text=raw.decode('gb18030',errors='strict').replace('\r\r\n','\n').replace('\r\n','\n')
    assert text.startswith('Public QMLibrary\n') and 'Function FindColorEx(' in text
    (OUT/'runtime-library.original.bin').write_bytes(raw)
    (OUT/'runtime-library.original.vbs.txt').write_text(text,encoding='utf-8')
    functions=[]
    for m in re.finditer(r'(?im)^[ \t]*(Function|Sub)\s+([A-Za-z_][A-Za-z_0-9]*)[^\n]*\n',text):
        tail=re.search(r'(?im)^[ \t]*end\s+'+m[1]+r'\b[^\n]*(?:\n|$)',text[m.end():]);assert tail,m[2]
        source=text[m.start():m.end()+tail.end()];name=m[2]
        functions.append({'name':name,'kind':m[1],'line':text[:m.start()].count('\n')+1,
                          'source':source,'qmlibrary_calls':sorted(set(re.findall(r'QMLibrary\.([A-Za-z_][A-Za-z_0-9]*)',source,re.I)))})
    selected=[next(f for f in functions if f['name']==n) for n in ('GetCursorPos','FindColorEx','FindPic')]
    subset='\n'.join(f['source'] for f in selected)
    (OUT/'used-global-functions.vbs.txt').write_text(subset,encoding='utf-8')
    usage=[]
    for path in sorted((ROOT/'outputs/QMacro-Rebuild-Development/programs').glob('[0-9][0-9].json')):
        p=json.loads(path.read_text(encoding='utf-8'));refs=collections.defaultdict(list)
        for i,(op,l,arg,f) in enumerate(p['code']):
            if op in (2,30):refs[arg].append(i)
        for index,source in enumerate(p['strings']):
            for fn in functions:
                if re.search(r'(?<![A-Za-z_0-9.])'+fn['name']+r'\s*\(',source,re.I):
                    usage.append({'module':p['module'],'source_sl':index,'name':fn['name'],'records':refs[index],'source':source})
    report={'image_sha256':hashlib.sha256(data).hexdigest(),'source_va':hex(start+0x400000),'source_end_va':hex(end+0x400000),
            'source_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_encoding':'gb18030 strict; original bytes retained',
            'function_count':len(functions),'functions':functions,'used_subset':selected,'used_calls':usage,
            'normalization':'CRCRLF/CRLF to LF for the readable copy only.',
            'usage_scan':'Parenthesized, unqualified names from the 86-function library in preserved SL strings; not a proof against dynamic calls or missing records.',
            'initialization_present_in_full_text':True,'original_code_executed':False,
            'limits':['The full source includes native COM initialization and is delivered as inert .txt, not automatically executed.',
                      'Three used global wrappers are retained as source; this extraction does not execute them. Native QMLibrary.FindColor differs from dm.FindColor.',
                      'User-authored original comments are not inferred from stock-library comments.']}
    (OUT/'library-source-map.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    prefix_at=0x7b57b0-0x400000;prefix=data[prefix_at:data.index(b'\0',prefix_at)]
    fallback_at=0x7b133c-0x400000;fallback=data[fallback_at:data.index(b'\0',fallback_at)]
    assert prefix==b'Attachment:\\' and len(prefix)==12 and fallback==b'.\\QMScript\\'
    (OUT/'builtin-file-path-evidence.json').write_text(json.dumps({
        'image_sha256':report['image_sha256'],'attachment_prefix_va':'0x7b57b0','attachment_prefix_ascii':prefix.decode('ascii'),
        'attachment_prefix_hex':prefix.hex(),'attachment_prefix_bytes':len(prefix),
        'wrapper_va':'0x65f9d0','prefix_length_argument_va':'0x65fa06','comparison_call_va':'0x65fa21',
        'relative_fallback_va':'0x7b133c','relative_fallback_ascii':fallback.decode('ascii'),
        'native_dispatch_helper_va':'0x631b40','case_sensitivity_verified':False,
        'attachment_extract_cleanup_replayed':False,'original_code_executed':False},indent=2)+'\n',encoding='utf8')
    lines=['# Runner 原始 VBScript 函式庫','',
           f'從既有映像 {report["source_va"]}..{report["source_end_va"]} 提取 {len(raw)} bytes，{len(functions)} 個函式／子程序；含原註解。',
           '原位元組與來源SHA另存；可讀副本只做編碼及換行轉換。完整文字含COM初始化，不會在本機直接執行。','',
           '## 目前腳本使用的三個全域函式','']
    for fn in selected:lines+=['### '+fn['name'],'','```vbscript',fn['source'].rstrip(),'```','']
    lines+=['FindColorEx呼叫的是Runner內建QMLibrary.FindColor，不是dm.FindColor；不能沿用已量測DM的矩形與容差規則。',
            '座標以x*8192+y編碼；原包裝用CInt除法與Mod還原，CInt的四捨六入五成雙語義也需保留。',
            'GetCursorPos只設定ByRef輸出，原函式回傳值未賦值（Empty）；FindColorEx和FindPic則回傳原封裝整數。',
            '全域FindPic仍需另核對原生比圖規則；不能直接套用DM比圖後宣稱等同。','',
            '## 八組腳本的全域呼叫缺口','',
            '| 函式 | 保留SL出現次數 |','| --- | ---: |']
    lines += [f'| {name} | {sum(u["name"]==name for u in usage)} |' for name in ('GetCursorPos','FindColorEx','FindPic')]
    lines += ['', '數字計算不同SL項目，記錄引用另見library-source-map.json；不是執行次數。',
              '掃描範圍是86函式中帶括號且未加物件前綴的保留SL引用；不涵蓋缺失記錄或未知動態呼叫。',
              '原庫LeftDown/LeftUp分別呼叫QMLibrary.MouseClick 3/6，因此這組數字是左鍵按下／放開，不是兩次點擊。','']
    lines += ['## 已核對的內建找色','',
              '原生入口0x65dbc0→0x6312e0；採六碼BGR，右下邊界包含。相似度先轉Single，再截斷100×(1-sim32)。',
              'sim32大於double 0.99時走完全相等；其餘為RGB三通道絕對差之和嚴格小於容差。這和DM的逐通道容差不同。',
              '類型0逐行；類型1由中心逐層方殼，上下交錯後左右交錯。Python及C#的80個供應像素案例一致，另有9個完整中心移除順序。',
              '未找到回-8193，包裝後座標為(-1,-1)。不同語法、範圍及型別轉換尚未全面重播，重建遇未支援輸入會報錯。','',
              '## 內建找圖的像素階段','',
              '原入口0x65f9d0→0x631b40；0x631d94到0x6323f5的供應32位元列資料算術已移植，Python與C#各對照220組CPU案例。',
              '每像素RGB差總和達24才算不符；依五組稀疏位置累計不符數，容許值來自截斷w×h×(1-sim32)的分數。',
              '五組座標依序為(x0,y0,步4)、(x2,y2,步4)、(偶x,奇y,步2)、(奇x,偶y,步2)、(奇x,奇y,步2)。部分偶偶位置從未檢查。',
              '預設四角同色就以該色透明，均色圖片也如此。候選原點使用嚴格小於captureSize-templateSize，故圖片剛好同大時找不到，最後可容納位置亦略過。',
              '這些行為依原指令保留，未自行修成一般模板比對。另以0x67cb4a列索引與0x67ce88轉換算術核對10個正負高度／padding案例及377種一般BMP，與Python/C#解碼器的RGB完全相同，32位元高位元組全為0。',
              '0x630f58..0x630fb9的擷取標頭算術確認32bpp、負高度（上到下）；沒有執行GDI擷取或配置API。',
              'C#的BuiltinVisionService接上供應影像／審核附件解析器／游標提供者，含右下邊界轉換、取消與錯誤傳遞；未自動接管正式遊戲或開啟桌面擷取。',
              '原檔名前綴常數0x7b57b0是12bytes的Attachment:加反斜線，不是memory前綴；它的抽取、清理及相對QMScript路徑分支仍未重播。',
              '檔案載入、資源生命週期、原游標讀取失敗規則及正式遊戲行為未因此驗證；DMDM仍未轉出。','']
    (OUT/'原始函式庫解讀.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('source_va','source_bytes','function_count','raw_sha256')}))
if __name__=='__main__':main()
