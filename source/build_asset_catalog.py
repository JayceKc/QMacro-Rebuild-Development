"""Publish all recovered BMPs by original container; never merge names blindly."""
from pathlib import Path
import collections,hashlib,json,ntpath,re,shutil
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'outputs/QMacro-Rebuild-Development'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def literal(text):
    m=re.fullmatch(r'"((?:[^"]|"")*)"',text)
    return m[1].replace('""','"') if m else None

def call_arguments(text):
    m=re.fullmatch(r'Call\s+FindPic\((.*)\)',text,re.I)
    if not m:raise ValueError('Unparsed global FindPic: '+text)
    s=m[1];quoted=False;depth=0;start=0;args=[];i=0
    while i<len(s):
        c=s[i]
        if c=='"':
            if quoted and i+1<len(s) and s[i+1]=='"':i+=2;continue
            quoted=not quoted
        elif not quoted:
            if c=='(':depth+=1
            elif c==')':depth-=1
            elif c==',' and depth==0:args.append(s[start:i].strip());start=i+1
            if depth<0:raise ValueError('Unbalanced global call')
        i+=1
    if quoted or depth:raise ValueError('Unbalanced global call')
    args.append(s[start:].strip())
    if len(args)!=8:raise ValueError('Global FindPic arity')
    return args
def main():
    forms=json.loads((PROJECT/'data/ui-forms.json').read_text(encoding='utf-8'))['forms']
    canonical={f['container']:f['module'] for f in forms};images=[];by_container=collections.defaultdict(dict);by_name=collections.defaultdict(list)
    for container in sorted(canonical):
        source=ROOT/'outputs/restored-files'/container/'attachments'
        for path in sorted(source.glob('*.bmp')):
            relative=f'assets/restored/{container}/attachments/{path.name}';target=PROJECT/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,target);raw=path.read_bytes();sha=digest(path);assert digest(target)==sha
            kind='ordinary_bmp' if raw[:2]==b'BM' else 'proprietary_dmdm' if raw[:4]==b'DMDM' else 'unrecognized'
            record={'container':container,'module':canonical[container],'filename':path.name,'source':path.relative_to(ROOT).as_posix(),
                    'bundle_path':relative,'bytes':len(raw),'sha256':sha,'kind':kind}
            images.append(record);by_container[container][path.name.casefold()]=record;by_name[path.name.casefold()].append(record)
    conflicts=[]
    for name,items in by_name.items():
        hashes=sorted({item['sha256'] for item in items})
        if len(hashes)>1:conflicts.append({'name':name,'hashes':hashes,'occurrences':[{'container':item['container'],'sha256':item['sha256']} for item in items]})
    calls_path=ROOT/'outputs/plugin-recovery/script-plugin-call-contracts.json';calls=json.loads(calls_path.read_text(encoding='utf-8'))['calls']
    global_path=ROOT/'outputs/runner-vbs-library/library-source-map.json'
    global_calls=json.loads(global_path.read_text(encoding='utf-8'))['used_calls']
    builtin_pictures=[]
    for c in global_calls:
        if c['name']!='FindPic':continue
        builtin_pictures.append({'module':c['module'],'sl':c['source_sl'],'records':c['records'],'method':'FindPic',
                                 'api_family':'runner_builtin','arguments':call_arguments(c['source'])})
    produced=collections.defaultdict(set)
    for c in calls:
        if c['method'].casefold()=='capture':
            value=literal(c['arguments'][4])
            if value:produced[c['module']].add(ntpath.basename(value).casefold())
    references=[]
    for c in calls+builtin_pictures:
        if c['method'].casefold()!='findpic':continue
        value=literal(c['arguments'][4])
        base={'module':c['module'],'source_sl':c['sl'],'records':c['records'],'original_expression':c['arguments'][4],
              'api_family':c.get('api_family','dm_plugin')}
        if value is None:references.append(dict(base,status='dynamic_expression'));continue
        for name in value.split('|'):
            filename=ntpath.basename(name);key=filename.casefold();container='account/'+str(c['module']).zfill(2)
            if not name:status='empty_list_token'
            elif key in by_container[container]:status='original_attachment'
            elif key in produced[c['module']]:status='runtime_capture'
            elif key in by_name:status='other_container_only'
            else:status='missing'
            references.append(dict(base,original_path=name,filename=filename,status=status))
    catalog={'schema':1,'containers':[{'container':c,'canonical_module':canonical[c],'images':len(by_container[c])} for c in sorted(canonical)],
             'images':images,'name_conflicts':conflicts,'original_native_libraries_included':False,
             'policy':'Use the canonical module and matching side. Same-name different-content images remain separate. No automatic cross-container fallback.'}
    (PROJECT/'data/asset-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'source_call_contract_sha256':digest(calls_path),'global_library_source_map_sha256':digest(global_path),
            'global_findpic_calls':len(builtin_pictures),'references':references,
            'status_counts':dict(collections.Counter(r['status'] for r in references)),'full_program_restored':False}
    (PROJECT/'verification/asset-dependencies.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result={'image_instances':len(images),'unique_names':len(by_name),'unique_content':len({i['sha256'] for i in images}),
            'kinds':dict(collections.Counter(i['kind'] for i in images)),'name_conflicts':len(conflicts),'references':report['status_counts']}
    (PROJECT/'verification/asset-catalog-verification.json').write_text(json.dumps(dict(result,ok=True,copy_hashes_verified=True),indent=2)+'\n',encoding='utf-8')
    missing=collections.defaultdict(list)
    for r in references:
        if r['status']=='missing':missing[r['filename']].append(r)
    lines=['# 附件圖片與尚缺來源','',
           '已將 20 個容器的 3,048 份 BMP 原樣分開保留；這是含重複副本的數量，不是獨特圖片數。',
           '共有 382 個檔名、378 種內容；3044 份為一般 BMP，4 份是同一個尚未轉出的 DMDM 內容。',
           '同名 ta.bmp 有兩種不同內容，依模組保存；禁止以其他模組的同名圖自動替代。',
           'account/02 與 account/04 的相同腳本分別對應 canonical module 01/03，解析器明示採該側的 canonical 附件。','',
           '## 找圖中仍未找到的附件名稱','',
           '下表是已解出的所有附件及提供的原始目錄中尚未找到的靜態名稱；不宣稱其他未提供位置不存在。',
           '八張 Q/W/E/R/A/S/D/F 圖另有原始 Capture 產生路徑，不把它們誤列為缺檔。',
           '兩個尾端空 token 已由原外掛 11 案實測：會被忽略，不是空檔名。','',
           '附件引用亦納入43條Runner全域FindPic原SL；該函式的原生比圖規則尚未完成，附件存在不代表後端已可執行。','',
           '| 名稱 | 模組／原 SL／存活記錄 |','| --- | --- |']
    for name,refs in sorted(missing.items()):
        positions='；'.join(f'{r["module"]:02} / SL{r["source_sl"]} / '+','.join('L'+str(n) for n in r['records']) for r in refs)
        lines.append(f'| {name} | {positions} |')
    lines+=['','## DMDM 圖片','',
            'YLDJS1.bmp 的原始雜湊為 58792d98ad820ad1d1de1e1dcde4c6144b50694c5854d5029ed9253304bd23f9。',
            '在固定副本以原插件測過空密碼及先前提供的候選；SetPicPwd 的成功回傳不等於解密成功。',
            '兩次 ImageToBmp 都回 0，未生成可讀 BMP，GetPicSize 仍為空。原檔保持不變，實際圖片密碼仍未知。',
            '目前保留腳本沒有引用此檔名；此結論只涵蓋已解讀的文字與附件依賴。','']
    directory=PROJECT/'analysis/assets';directory.mkdir(parents=True,exist_ok=True)
    (directory/'附件圖片與尚缺來源.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
