"""Readable module05 entry evidence, intact routine control flow and limits."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT/'outputs/QMacro-Rebuild-Development';OUT=ROOT/'outputs/fishing-recovery'


def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    p=load(PROJECT/'programs/05.json');pretty=load(ROOT/'outputs/qmacro-readable-analysis/05-釣魚/字串_閱讀對照.json')
    structure=load(ROOT/'outputs/QMacro-Rebuild/modules/05-釣魚/結構.json');alignment=load(OUT/'prefix-alignment.json')
    completion=load(OUT/'repair-completion-paths.json');ui=load(PROJECT/'data/ui-forms.json')
    form=next(f for f in ui['forms'] if f['module']==5)
    lines=['# 釣魚：入口線索、兩個完整主體與尚缺控制流','',
           '本模組原929筆，L4..L503共500筆被保護記錄仍缺失，沒有被本分析覆寫。主體末段L504..L539及兩個子程序保留。',
           '本文件把保留文字和存活控制流接成閱讀路徑；不提供假裝能直接啟動的完整QMS。','',
           '## 入口與初始化','',
           '- L0..L2定義根及兩個呼叫框架類別，L3為入口控制。原主要初始化在缺失區。',
           '- SL3..7先延遲、讀游標並點擊；SL8取MMVerifyCode。SL11及SL19分別檢查空值和4AD733，之後都有長延遲迴圈字串，原跳轉未恢復。',
           '- SL28..48是舊COM/DLL註冊、解附件、DM版本7.2450及滑鼠模式初始化；完整原文只當資料，不在主機執行。獨立後端不使用假SDK碼。',
           '- SL49..92讀介面及初始化計數。下表對應保留控制項與SL；不是已恢復的原記錄位址。','',
           '| 控制項 | 畫面文字／選項 | SL |','| --- | --- | --- |']
    controls={c['name']:c for c in form['controls']}
    for name,sl in (('ComboBox1',51),('ComboBox2',55),('CheckBox1',59),('CheckBox2',65),('CheckBox3',71),('CheckBox4',77),('CheckBox5',83)):
        c=controls[name];text='；'.join(c['items']) if c['items'] else c['text']
        lines.append(f'| {name} | {text.replace(chr(10)," ").replace("|","／")} | {sl} |')
    lines+=['','CheckBox2的畫面標示先回莊園再F8，但SL129/143與SL287/313在F10、F8兩個分支都檢查同一旗標；閱讀行為以來源為準。','',
            '## 一輪釣魚的保留來源','',
            '以下為來源分段，括號中的巢狀關係仍未由缺失跳轉證明；不能將清單順序直接當可執行控制流。','',
            '1. SL94..107：在(956,466)..(963,499)以DM找19個魚咬鉤色樣，判INTX>=0；CS加一，>=266有延遲及歸零。',
            '2. SL108..113：E兩次、等8秒、釣魚計數加一。SL114..119含80次優先停止。',
            '3. SL120..208：80次完成動作，0停、1F10、2F8、3F6，另有退出遊戲點擊及SYS.ExitOS意圖。SL164重複判模式3，與後段SL347的模式4不同；此處原跳轉仍缺，保留疑點。',
            '4. SL212..227：檢查工具耐久色和shgj1..4圖；建立工具紅了框架後原呼叫目標缺失，以唯一剩餘主體L541推定，未冒稱原呼叫數字已解。',
            '5. SL230..249：SDK標記、四個Runner全域FindColorEx綠色樣及DM活力色樣。內建找色與DM的BGR、容差、右下邊界不同。',
            '6. SL251..255：B鍵、等待，依慢速修理旗標額外等待。',
            '7. SL257..414：依完成動作進入活力查詢的不同等待支路。共通文字會在找到色時氣息歸零，否則加一，>=5才觸發後續動作；L504..L524為模式5支路的存活末段。',
            '8. L526..L538（SL416..427）：CS歸零、可選S撒餌、移回MX/MY、E及等待4秒。L539明確絕對跳回L115；L115仍是缺失位置，不能宣稱主迴圈閉合已恢復。','',
            '## 缺失位置對齊的強度','',
            f'以完整來源群組模板、UI資料流模板和SL配置順序建立約束模型，共406組位置。模型仍有{alignment["alignment_paths"]}條路徑，只有{alignment["model_forced_records"]}個位置在此模型下只有一種對齊。',
            '「模型唯一」不是解密成功：SL順序、模板完備性及UI模板都是明示假設；單獨跳轉的原操作碼及運算元未知。prefix-alignment.json保留全部可行局部候選，不能任挑一條當原碼。','',
            '## 兩個保留子程序','',
            'L879的返回莊園名稱由原框架建立＋L786/L804的原call879直接對應。L541工具紅了名稱以剩餘框架和修理行為配對，明標推定。','',
            '### L541..L877 工具紅了／修理（名稱配對推定）','',
            '修理模式0：L542條件成立走Alt/P寵物介面、隨機移動區域、按下/放開/點擊等修理序列。模式1：L607成立進F2莊園、找入口、銀幣與修理按鈕等多個迴圈；模式2：L769成立走完成動作。',
            'Randomize與INT(RND)原碼保留，不把自有測試隨機序列當成VBScript RNG等同。',
            'L826與L864都判完成=4；前者真分支退出遊戲並停止，假分支才到後者。設定不變時後者仍為假，因此L868 SYS.ExitOS到不了；選模式5會回傳而沒有完成動作。',
            'repair-completion-paths.json以原L769..L877控制流、修理=2、回莊園未勾、穩定完成值0..5核對六條路徑；沒有執行輸入、COM或關機。不能擴大成整段修理或真遊戲測試已通過。','',
            '### L879..L923 返回莊園','',
            '先F2並等待，以三張zhuangy圖片找入口。沒找到時延遲並回L880；找到時把座標加(15,15)，點選後操作(1454,853)，等12秒。',
            '接著L912迴圈找(160,1)..(260,25)的SDK標記；找到則等4秒離開，沒找到回L912。L922恢復呼叫框架，L923回傳；該主體沒有賦值回傳欄位，保留Empty語義。','',
            '## 精確條件、迴圈與呼叫','']
    structured_path=OUT/'prefix-structured-alignment.json'
    if structured_path.exists():
        structured=load(structured_path)
        lines += ['補充：prefix-structured-alignment.json加入五個介面1/0分支及版本成功/失敗的If/Else假設。六個完整原Else形狀支持該配置，但不能證明被保護的位置也相同。',
                  f'在額外假設下，唯一對齊位置由146增為{structured["model_unique_records"]}，路徑仍有{structured["alignment_paths"]}條。新表把其他無字串節點明標source_free_unknown，沒有把16當作已恢復的原操作碼。','']
    for routine in structure['routines']:
        lines += [f'### L{routine["entry"]}..L{routine["last"]}','',
                  '| 條件分支記錄 | 原條件 | 成立 | 不成立 |','| --- | --- | --- | --- |']
        for c in routine['conditions']:
            cond=p['code'][c['at']-1];assert cond[0]==4
            lines.append(f'| L{c["at"]} | SL{cond[2]} {pretty[cond[2]]["readable"].replace("|","／")} | L{c["true"]} | L{c["false"]} |')
        lines+=['','迴圈：'+ '；'.join(f'L{x["at"]} → L{x["target"]}' for x in routine['loops']),
                '呼叫：'+('；'.join(f'L{x["at"]} → L{x["target"]}' for x in routine['calls']) or '無保留的子程序呼叫'),'']
    lines+=['## 可讀狀態機與原文比對','',
            'qmacro_fishing.py提供FishingMachine；data/fishing-routines.json將原337+45筆全部轉為具名動作，沒有eval原文、CreateObject、實際輸入、等待或關機。',
            'read_context需明示提供修理／完成／慢速／回家設定、模擬模式、先前游標與SDK標記；不預設SDK色碼。找圖找色結果及兩個INT(RND)座標都須明示回覆，資料未到就停在等待狀態。',
            'source/replay_fishing_cases.py可離線重播77組合成案例。原保留主體亦在固定副本用相同77設定執行，原文不改；DM/SYS由記錄物件接收，RNG在原賦值完成後覆寫成案例指定值。',
            '77條記錄路徑及5243個外部事件逐項一致，Root框架恢復Nothing、未賦值回傳欄位為Empty。這不是原RNG序列、實際延遲、遊戲辨識或主程式前500指令已驗證。',
            '這批走到365個原位置，17個位置未走到，均是第一次ExitScript(0)之後的延遲／再次停止／結構跳轉；全部原指令仍保留於資料。未走到不能冒稱受控執行已覆蓋。',
            '其中一組刻意在L864前改完成值5→4，確認動態變化時會產生L868關機意圖；固定設定的不可達結論只限先前明示假設，不能直接刪除原分支。',
            '逐案報告見verification/original-fishing-vm-test.json、fishing-owned-replay.json與fishing-original-vs-rebuild.json。','',
            '## 執行緒、介面事件、外掛與剩餘依賴','',
            '保留的worker_starts及callbacks表都是空；不因此推論缺失位置不可能有其他啟動控制。介面屬性讀取是入口設定，尚未連接正式GUI執行宿主。',
            'DM負責FindColor/FindPic/MoveTo等；Runner負責全域FindColorEx/GetCursorPos、按鍵、延遲、滑鼠事件及ExitScript；SYS.ExitOS只當原意圖記錄。',
            'SL212/215的DM色碼尾端有空token。原插件92組合成像素案例證明空token會變成黑色000000候選（含正常相似度容差），不是忽略。Python與C#已按此規則修正；空字串同理，None/缺SDK則不會被冒作空色碼。',
            'SDK標記值、前500跳轉與實際釣魚辨識/時序未證。本文不把缺失原圖補畫成已還原，也不把供應影像比對當真遊戲運作。','',
            '## 主流程逐SL原意閱讀','',
            '此處按SL配置順序列出原意，不重排成未證實的If/Else巢狀。兩個完整主體請對照readable/05-釣魚/函式-L00541.qms.txt及函式-L00879.qms.txt。','','```text']
    lines += [f'SL{i}: {pretty[i]["readable"]}' for i in range(3,428)]
    lines+=['```','']
    (OUT/'釣魚_可讀流程.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    evidence={'module':5,'full_entry_to_end_recovered':False,'source_program_sha256':hashlib.sha256((PROJECT/'programs/05.json').read_bytes()).hexdigest(),
              'prefix_alignment_sha256':hashlib.sha256((OUT/'prefix-alignment.json').read_bytes()).hexdigest(),
              'completion_path_sha256':hashlib.sha256((OUT/'repair-completion-paths.json').read_bytes()).hexdigest(),
              'retained_routines':[{'entry':r['entry'],'last':r['last'],'conditions':len(r['conditions']),'loops':r['loops'],'calls':r['calls']} for r in structure['routines']],
              'original_missing_unchanged':500,'source_window_readable_sl':[3,427],'guide_generation_executes_original_code':False}
    plan_path=PROJECT/'data/fishing-routines.json'
    if plan_path.exists():
        plan=load(plan_path);evidence.update(owned_action_records=382,original_body_guest_replay_verified=plan.get('original_body_guest_replay_verified',False),
                                          controlled_cases=77,original_records_visited=365,external_events_compared=5243,
                                          source_plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),full_module_restored=False)
    (OUT/'fishing-current-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'module':5,'retained_routines':2,'conditions':31,'completion_cfg_cases':6,'full_module_restored':False}))


def write_retained():
    plan_path=PROJECT/'data/fishing-retained.json'
    evidence_path=PROJECT/'verification/fishing-suffix-original-vs-rebuild.json'
    if not plan_path.exists() or not evidence_path.exists():
        return
    plan,evidence=load(plan_path),load(evidence_path)
    rows=['# 模組 05 保留記錄','']
    actions={a['record']:a for a in plan['actions']}
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
        rows.append(f'L{at} {source}  // op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}, field_3={a["field_3"]}')
    (OUT/'釣魚_全部保留記錄.txt').write_text('\n'.join(rows)+'\n',encoding='utf8')
    guide = [
        '# 釣魚主流程尾段與保留記錄','',
        '429 筆可讀記錄已接入事件模型。新增部分是 L504–L539 主流程尾段與 11 筆宣告、派送、略過及介面末端。預設入口從 L0 開始，逐筆執行宣告，於缺失的 L4 停下。L4–L503 共 500 筆維持原缺失位置。','',
        '從尾段 L504 測試時，明示供應原計數器、是否補餌、已保存游標及畫面觀測。命中以座標判定，並核對外掛回傳值反轉時仍走同一路徑。下表的名稱依原操作推定。','',
        '| 路徑 | 原始記錄 | 停止位置 |','| --- | --- | --- |',
        '| 找色命中 | L504 判斷，L508 清除失敗計數，L527 清除本輪計數，L529 依設定選擇按 S，L535 移回保存游標，L537 按 E | L539 回跳到缺失 L115 |',
        '| 未命中且累計少於 5 | L511 增加失敗計數，L513 比對門檻 | L523 回跳到缺失 L501 |',
        '| 未命中且累計達 5 | L517 發出 SYS.ExitOS(1) 意圖，L519 發出停止 | L519 |','',
        f'隔離副本的 {evidence["suffix_cases"]} 組尾段案例核對 {evidence["suffix_events"]} 個事件，覆蓋尾段 36 筆中的 {len(evidence["suffix_observed_records"])} 筆。L520、L521 位於停止要求之後，L525 被相對跳轉略過。另有 {evidence["form_cases"]} 組 Form1 案例核對等待、關閉與結束。輸入、關機和等待由測試物件記錄。','',
        '修理 L541–L877 與回家 L879–L923 沿用已比對的兩個子程序。各入口、迴圈、變數與 SDK 依賴見原導讀。保留記錄的工作啟動及回呼表為空，缺失區段的內容仍待追查。','',
        '[逐筆索引](釣魚_全部保留記錄.txt) [原文比對](../../verification/fishing-suffix-original-vs-rebuild.json)'
    ]
    (OUT/'釣魚_主流程尾段.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


if __name__=='__main__':
    main()
    write_retained()
