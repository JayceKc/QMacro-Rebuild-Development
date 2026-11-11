import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
OUT=ROOT/'analysis/gathering' if ROOT==PROJECT else ROOT/'outputs/gathering-recovery'


def main():
    load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    plan=load(PROJECT/'data/gathering-main-suffix.json');report=load(PROJECT/'verification/gathering-main-original-vs-rebuild.json');aliases=plan['name_roles']
    def numeric(n):
        if 'name' in n:return aliases.get(n['name'],n['name'])
        if 'const' in n:return str(n['const'])
        op=n['op'];args=[numeric(a) for a in n['args']]
        if op in ('SGN','ATN','INT'):return op+'('+args[0]+')'
        if op.startswith('UNARY'):return op[-1]+args[0]
        return '('+(' '+op+' ').join(args)+')'
    def expr(n):
        if 'numeric' in n:return numeric(n['numeric'])
        if 'const' in n:return json.dumps(n['const'],ensure_ascii=False)
        if 'root_slot' in n:return 'root_slot['+str(n['root_slot'])+']'
        if 'concat' in n:return ' & '.join(expr(v) for v in n['concat'])
        raise ValueError(n)
    lines=['# 採集主流程保留段 L507..688＋原跳過函式鏈','',
        '這是四個受控入口的逐筆偽碼，並非原L7入口已恢復。命中缺失L432會明確停止。原變數名稱見data/gathering-main-suffix.json的name_roles。','']
    for a in plan['root_actions']:
        k=a['kind'];text=None
        if k=='delay':text=f'等待 {a["milliseconds"]} ms'
        elif k=='dynamic_delay':text='等待 '+expr(a['value'])+' ms'
        elif k=='test':text='condition = '+expr(a['condition'])
        elif k=='if_zero':text=f'若 condition = 0，跳到 L{a["target"]}'
        elif k=='jump':text=f'跳到 L{a["target"]}'
        elif k=='call':text=f'呼叫 L{a["target"]}'
        elif k=='assign':text=a['role']+' = '+expr(a['value'])
        elif k=='frame_enter':text='保存parent並建立 '+a['name']+' 呼叫框架'
        elif k=='root_store_temp':text=f'root_slot[{a["slot"]}] = temporary（可能是Empty）'
        elif k=='read_global':text='temporary = 讀取共享值 '+a['role']+' [原鍵 '+a['global_key']+']'
        elif k=='randomize':text='初始化原亂數來源'
        elif k=='random_int':text=f'{a["role"]} = 受控整數 [{a["lower"]}, {a["lower"]+a["span"]-1}]'
        elif k in ('key_press','mouse_click','move_to','move_to_ex'):text=k+'('+', '.join(expr(v) for v in a['arguments'])+')'
        elif k=='trace':text='記錄 '+expr(a['value'])
        elif k in ('find_color','find_pic'):
            text=', '.join(a['out_roles'])+' = '+k+'(ROI='+str(a['rect'])+', '+expr(a['spec'])+', similarity='+str(a['similarity'])+', dir='+str(a['direction'])+')'
        elif k=='program_end':text='原op22只前進，下一個PC=1626超出原code末端，程式結束'
        else:raise ValueError(k)
        lines.append(f'L{a["record"]}: {text}  // op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}, field_3={a["field_3"]}')
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'採集_主流程保留段_逐筆偽碼.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
    native_paths=['original-gathering-walk.json','original-gathering-worker.json','original-gathering-routines.json','original-gathering-main.json']
    covered=set();case_count=0
    for name in native_paths:
        d=load(PROJECT/'verification'/name);assert d['ok'];case_count+=len(d['cases'])
        covered|={i for c in d['cases'] for i in c['records']}
    original=load(PROJECT/'programs/08.json');missing=set(original['missing_records']);valid=set(range(len(original['code'])))-missing
    combined=set(a['record'] for a in plan['actions'])|set(range(890,915));assert len(combined)==1116
    evidence={'source_program_sha256':plan['source_program_sha256'],'controlled_entries':plan['root_entries'],'retained_root_records':188,
        'root_records_exercised':len(report['covered_root_records']),'uncovered_root':[592],'original_prefix_missing':{'first':7,'last':506,'count':500},
        'missing_boundary_targets':[432],'joined_plan_records':1091,'all_event_port_records_with_worker':1116,'all_original_controlled_cases':case_count,
        'all_preserved_records_explicitly_traced':len(covered&valid),'covered_missing_boundaries':sorted(covered&missing),
        'preserved_not_explicitly_traced':sorted(valid-covered),'source_report_sha256':hashlib.sha256((PROJECT/'verification/gathering-main-original-vs-rebuild.json').read_bytes()).hexdigest(),
        'case_count':74,'external_events':6393,'field_3_semantics_verified':False,'full_module_restored':False}
    assert case_count==390 and evidence['all_preserved_records_explicitly_traced']==1104
    (OUT/'gathering-main-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    guide=['# 採集主流程後半段與子程序銜接','',
        '74組固定副本案例／6393個外部事件、完整PC路徑、停止位置、主迴圈次數、查詢數、根框架狀態、槽12..16與六個歷史座標皆一致。這是保留後半段的受控入口重播；原500筆前綴仍缺，沒有執行或補造它們。','',
        '## 從哪裡讀','',
        '- [主流程逐筆偽碼](採集_主流程保留段_逐筆偽碼.txt)，188筆包含原跳過子程序的尾鏈。',
        '- [子程序逐筆偽碼](採集_修理回家活力_逐筆偽碼.txt)與[走位說明](採集_計算走位.md)。',
        '- [銜接動作資料](../../data/gathering-main-suffix.json)、[74個受控輸入](../../data/gathering-main-cases.json)。',
        '- [原文副本觀測](../../verification/original-gathering-main.json)、[逐案比較](../../verification/gathering-main-original-vs-rebuild.json)。','',
        '## 原缺失與受控入口','',
        '模組08共1626個位置，L7..L506恰好500個位置缺失。L0..L6是宣告／進入分派。最早完整保留動作是L507；先前泛稱「前500」不能誤讀為L4..503。',
        '本批分別從L507、540、581、593進入，明示提供先前計數器、六個歷史座標、舊角度及設定。這些初值只是測試資料；目前無法證明原前綴在每個時刻會提供相同值。L592在四個入口的本批保留路徑中未執行；缺失前綴是否可直接跳入它仍未知。','',
        '## L507：既有分支的恢復尾段','',
        '右鍵後將fallback_attempts加1。新值嚴格大於5才清零fallback_attempts與walk_repeats，送MoveToEx(860,440,200,200)意圖，點擊並依序Q/F/E/A/D/R/S；每鍵間隔同一個recovery_delay=66..181。原碼不是大於等於5。L539直接跳580，580再跳591，591回到缺失L432；到此停止，不假裝完成外層迴圈。','',
        '## L540：雙採小地圖圖示','',
        'L541以DM在[1593,38,1891,296]找12項色碼清單，sim=1、dir=4，輸出寫INTXX/INTYY（target_x/y）。命中後經L546/547呼叫走位L689，返回值寫根槽12，walk_repeats加1。新值嚴格大於10時按Space，送MoveToEx及點擊，把walk_repeats設成5，再依序Q/F/E/A/D/R/S。最後也回缺失L432。',
        'L541未命中則直接跳580，沿同一條缺失邊界退出本次重播。SDK失敗的另一段L581..590每三次會按Esc；它同樣回L432。','',
        '## L593：採礦迴圈','',
        'gather_mode=3才進L596；此處只是在保留後半段判斷是否進採礦分支，不代表其他模式在整個原程式沒有動作。L687回L596，沒有回L593，因此已入採礦迴圈後，單改gather_mode不是此保留段的一條退出控制邊。','',
        '每輪先在L599讀SDK共享鍵，存根槽13，再以DM找色。SDK命中後的執行順序：','',
        '1. L605/606呼叫活力檢查L1344，返回寫根槽14。它可能直接停止整個腳本，未必回主流程。',
        '2. L609找shgj1..4.bmp（工具損壞圖示）；命中時L613/614呼叫修理L916，返回寫根槽15。修理的結束策略也可能停止腳本。',
        '3. L621找chutou1/2.bmp；命中時S、G、G，並重設target_x、mining_counter與walk_repeats。',
        '4. 否則L640找kwmingzi1..10.bmp；命中時移至礦物名稱並右鍵，同時輪替三次歷史座標。',
        '5. 名稱也找不到時，L667用六項小地圖色碼找礦圖示，sim=1、dir=4。命中時L672/673呼叫走位L689，返回寫根槽16。',
        '6. SDK未命中則L677..686增加sdk_miss_count，每三次按Esc並清零。正常輪末L687回596，等待下一輪。','',
        '### 三次相同名稱座標','',
        'L650..655先把(X2,Y2)移至(X3,Y3)、(X1,Y1)移至(X2,Y2)，本次座標放入(X1,Y1)。若三組都相同，L658移至(target_x+10,target_y+60)再右鍵，然後只將X2設0；原碼沒有清空整組歷史。74案包含從全0初值累積三輪，以及一開始已有相同歷史的情況。','',
        '### 根槽與子程序槽不同','',
        '主流程用的是全域陣列root_slot[12..16]；子程序用各自物件的slot。INTX/INTY與INTXX/INTYY也是兩組不同變數。新引擎將兩組找圖輸出分開，避免活力或修理的查詢覆蓋尚待走位的目標；原文副本亦逐案核對根槽與框架Nothing狀態。模型以根sentinel表達全域槽，不冒稱原Runner建立了該物件。','',
        '## 原本就存在的結束跳鏈','',
        '從L593判斷為假時，L594→688→889→915→1276→1343→1621→1625；L1625原op22前進至code末端1626而結束。這條路跳過所有子程序本體，也跳過L1622/1623的Form1訊息／介面等待區。不能因此說Form1沒有事件；該等待入口如何由原宿主調度仍需另外確認。','',
        '## 驗證界線','',
        '本批20案在指定主迴圈界線由fixture停止，28案到缺失L432，5案走真實尾鏈結束，20案由原ExitScript停止，1案重現走位中心重合的800a0006溢位。命中與未命中由受控影像觀測供應，DM_RET反轉亦有比較；沒有真的操作遊戲。',
        '74案執行的是固定副本中的原VBScript語句＋已核對控制碼的自有VM，沒有改寫本體語句、載原DM或執行原Runner整體。Field_3的0/1原值全部保留並逐筆比對，但其在原Runner的完整語義尚未證明；本次不能拿它宣稱原Runner全程行為已等同。亂數在原賦值後覆寫控制，MoveToEx只記錄參數，不證明其實際滑鼠軌跡。','',
        '補充：Field_3另有[分階段原CPU證據](../runner-records/記錄第四欄與保護資料.md)：正常快取文字及除錯前置不讀第四欄；拆分／合併則以bit0選取受保護pair。原74個副本報告沒有測這些原CPU內部，因此其Field_3完整語義旗標維持false。','',
        '與前五個子程序合計：390組受控案例、14851外部事件；1116筆已具名事件動作中，1104筆有明記的原文路徑覆蓋。另12筆為L592、9筆原停止後指令、G常駐迴圈外913/914。宣告／入口7筆與Form1等待區3筆另列，不用窄範圍測試宣稱全1626位置恢復。原500筆、SDK真值、真實並行／正式GUI和遊戲整體仍未完成。','']
    (OUT/'採集_主流程銜接.md').write_text('\n'.join(guide),encoding='utf8')
    print(json.dumps({'cases':74,'root_traced':187,'all_cases':case_count,'all_preserved_traced':len(covered&valid),'still_missing':500}))


def write_retained():
    plan_path=PROJECT/'data/gathering-retained.json'
    report_path=PROJECT/'verification/gathering-host-original-vs-rebuild.json'
    if not plan_path.exists() or not report_path.exists():
        return
    plan=json.loads(plan_path.read_text('utf8'))
    report=json.loads(report_path.read_text('utf8'))
    actions={a['record']:a for a in plan['actions']}
    rows=['# 模組 08 保留記錄','']
    for at in range(plan['total_records']):
        if at not in actions:
            rows.append(f'L{at} 原記錄缺失')
            continue
        a=actions[at]
        source=a['source']
        if source:
            source=source.replace('\r\n',' / ').replace('\n',' / ')
        elif 'target' in a:
            source=f'跳往 L{a["target"]}'
        else:
            source=a['kind']
        rows.append(f'L{at} {source}  // context={a["context"]}, op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}, field_3={a["field_3"]}')
    (OUT/'採集_全部保留記錄.txt').write_text('\n'.join(rows)+'\n',encoding='utf8')
    guide = [
        '# 採集預設入口、介面與保留記錄','',
        '已索引全部 1,126 筆可讀記錄。主流程和其子程序有 1,091 筆，L890–L914 的 G 輪詢主體有 25 筆，宣告與介面新增 10 筆。各自保留原 L 編號、操作碼、位置欄、字串索引與第四欄。','',
        '| 入口 | 對應行為 |','| --- | --- |',
        '| L0 | L0–L5 載入宣告，L6 走預設派送。隔離副本在缺失的 L7 停下 |',
        '| L507、L540、L581、L593 | 採集保留的主流程入口，以明示初值核對。已有案例會回到缺失的 L432 |',
        '| L890 | G 輪詢主體。現存記錄未保留建立它的啟動位置 |',
        '| L1621 | 按原相對跳轉略過等待區，進到 L1625、再到末端 L1626 |',
        '| L1622、L1623 | Form1 等待訊息，接著等待事件。關閉後 L1624 結束本輪，或在允許繼續時前進 |','',
        f'隔離副本比對預設派送及 {report["form_cases"]} 組介面尾段，共 {report["form_steps"]} 個尾段步驟。介面狀態由測試物件提供。原 L7–L506 共 500 筆仍缺，G 工作啟動位置、正式介面及實際並行仍待還原。','',
        '[完整逐筆索引](採集_全部保留記錄.txt) [主流程與迴圈](採集_主流程銜接.md) [原文比對](../../verification/gathering-host-original-vs-rebuild.json)'
    ]
    (OUT/'採集_保留記錄與介面.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


if __name__=='__main__':
    main()
    write_retained()
