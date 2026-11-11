"""Readable version-specific listings and a comparison index."""
import re

from export_cube_routines import ARRAY, FRAME, TEMP
from export_battle_recovery import RECOVERY_RANGES
from export_battle_restart import RESTART_RANGES
from export_battle_routes import MAP_SCAN_CHECKPOINTS, ROUTE_RANGES
from export_battle_scan import ROOT_SUFFIX, SCAN_RANGES
from export_battle_tail import TAIL_RANGES
from export_shared_battle import CORE_STARTS
from replay_shared_battle import PROJECT,load


def readable(source):
    parts = re.split(r'("(?:[^"]|"")*")',source)
    for i in range(0,len(parts),2):
        parts[i] = parts[i].replace(FRAME+'.'+ARRAY,'frame.slots').replace(TEMP,'temporary')
    return ''.join(parts)


def describe(action):
    kind, at = action['kind'],action['record']
    if kind=='jump':
        return f'跳往 L{action["target"]}'
    if kind=='if_zero':
        return f'條件為零則跳 L{action["target"]}，否則 L{at+1}'
    if kind=='call':
        return f'呼叫 L{action["target"]}，返回 L{at+1}'
    if kind=='return':
        return '返回呼叫者'
    if kind=='worker_start':
        return f'要求啟動 L{action["target"]} 的工作，將工作 ID 放入 temporary'
    if kind=='iteration_end':
        return '到達工作本輪的結束位置'
    if kind=='read_global':
        return f'temporary = 讀取共享鍵 {action["key"]}'
    if kind=='write_global':
        return f'寫入共享鍵 {action["key"]} = temporary'
    if kind=='frame_enter':
        return f'建立子框架 {action["class_name"]} 並保留父框架'
    if kind=='frame_restore_intent':
        return '取回傳值至 temporary 並恢復父框架'
    if kind=='entry_dispatch':
        return '預設入口順序前進，已指定入口時由 Runner 派送'
    if kind=='runner_message':
        return '等待 Form1 的 Runner 訊息'
    if kind=='ui_pump':
        return 'Form1 開啟時等待事件。回呼返回本位置。關閉時前進'
    if kind=='final_record':
        return '前進到程式末端'
    return ('condition = ' if kind=='test' else '')+readable(action['source'])


def write_listing(path, title, plan):
    by = {a['record']:a for a in plan['actions']}
    lines = [f'# {title}','']
    for routine in plan['routines']:
        start, end = routine['entry'], routine['last']
        lines.extend([f'## {routine["name"]} L{start}..L{end}',''])
        for at in range(start,end+1):
            action = by[at]
            provenance = f'op={action["opcode"]}, loc={action["location"]}, SL={action["source_sl"]}, field_3={action["field_3"]}'
            lines.append(f'L{at} {describe(action)}  // {provenance}')
        lines.append('')
    path.write_text('\n'.join(lines)+'\n',encoding='utf8')


def write_control(out):
    guide = ['# 模組 01、03、06 的戰鬥啟停與找怪走位','',
             '子程序與區段名稱依現存行為命名。逐筆偽碼保留原操作碼、位置欄、文字索引及第四欄。','',
             '| 模組 | 新增指令 | 啟動位置 | 原文案例 | 事件 | 觀測指令 |',
             '| --- | ---: | ---: | ---: | ---: | ---: |']
    maps = []
    for module in CORE_STARTS:
        plan = load(f'data/battle-control-{module}.json')
        report = load(f'verification/battle-control-{module}-original-vs-rebuild.json')
        guide.append(f'| [{module}]({module}-戰鬥啟停逐筆偽碼.txt) | {len(plan["actions"])} | {len(plan["worker_wrappers"])} | {report["cases"]} | {report["external_events"]} | {report["records_covered"]} |')
        write_listing(out/f'{module}-戰鬥啟停逐筆偽碼.txt',f'模組 {module} 的戰鬥啟停與找怪走位',plan)
        maps.extend(['', f'### 模組 {module}', '',
                     '| 啟動 | 工作入口 | 呼叫主體 | 父框架接續 | 保存 ID |',
                     '| --- | --- | --- | --- | --- |'])
        for worker in plan['worker_wrappers']:
            saved = worker['local_id_name'] or worker['shared_id_key']
            scope = '區域' if worker['local_id_name'] else '共享'
            body = f'L{worker["body_entry"]}'
            if not worker['body_translated']:
                body += '（待接）'
            maps.append(f'| L{worker["start_record"]} | L{worker["worker_entry"]} | {body} | L{worker["parent_continue"]} | 槽 {worker["parent_slot"]} → {scope} `{saved}` |')
    guide += ['', '## 入口與執行順序','',
              '01 從 L1591 開始戰鬥、L1691 停止。03 從 L839 開始、L879 停止。06 從 L1443 開始、L1539 停止。技能與吃藥選擇分別位於 L8322、L2845、L8159，依各版設定分派到工作入口。01 的 L1625 與 06 的 L1472 保留各自的塔場條件。03 的 L864 將重新啟動工作 ID 存為區域變數。','',
              '啟動後，父流程越過工作入口，從原槽取回工作 ID。工作入口先建子框架，再呼叫主體並進入本輪結束位置。停止流程保留原 ID 與模式。模式 0、1、2 分別記錄停止、暫停、恢復意圖。','',
              '## 走位與找圖','',
              '走位查詢用 INTXX、INTYY 接收目標座標，保留一般查詢的 INTX、INTY。三版合計核對 50 次雙組座標回傳。逐筆檔保留每一版的查詢範圍、命中條件、角度運算、移動、重試與回跳。','',
              '## 核對範圍','',
              '160 組固定副本案例核對 8,382 個事件，包含新增範圍全部 65 個工作啟動位置。原指令在 Windows VBScript 中使用合成共享值、查詢回傳與工作 ID。事件只由記錄物件接收。實際工作排程、遊戲輸入與各版完整入口仍待驗證。','',
              '本批比對的八個呼叫邊界是 01 的 L742、L838、L6783、L11725，03 的 L417、L5885，06 的 L6620、L8621。後續計畫已接入這八處。 [重新啟動與擷取](重新啟動與擷取.md)','',
              '## 工作入口與 ID 對照'] + maps
    (out/'工作啟停與找怪走位.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


def write_restart(out):
    guide = ['# 覺醒、死亡處理、塔場與重新啟動','',
             '以下名稱依保留文字與流程命名。逐筆偽碼保留原記錄位置、操作碼、文字索引及第四欄。','',
             '| 模組 | 重啟入口 | 擷取入口 | 原文案例 | 比對事件 | 新段觀測指令 |',
             '| --- | --- | --- | ---: | ---: | ---: |']
    for module in CORE_STARTS:
        plan = load(f'data/battle-restart-{module}.json')
        report = load(f'verification/battle-restart-{module}-original-vs-rebuild.json')
        restart,capture = RESTART_RANGES[module]
        guide.append(f'| [{module}]({module}-復原與重啟逐筆偽碼.txt) | L{restart[0]} | L{capture[0]} | {report["cases"]} | {report["external_events"]} | {len(report["covered_new_records"])} |')
        entries = {a for a,_,_ in RECOVERY_RANGES[module]+RESTART_RANGES[module]}
        plan['routines'] = [routine for routine in plan['routines'] if routine['entry'] in entries]
        write_listing(out/f'{module}-復原與重啟逐筆偽碼.txt',f'模組 {module} 的復原與重新啟動',plan)
    guide += ['', '三版都先進入擷取子程序。呼叫框架放入 0、0、1920、1080、目錄及副檔名，再以年、月、日、時、分、秒直接串接檔名。單位數維持原式，不補零。案例以兩組明示時鐘核對 `C:\\方舟混沌\\202612345.bmp` 及 `C:\\方舟混沌\\2026119162033.bmp`。','',
              '擷取後，01 和 06 依序要求停止八個工作，03 要求停止四個。各版移動至 (40,20) 並點擊，接著以 Runner 內建找色查詢 31D74A。01 和 06 首次未命中時再查 33D74A。各自所有查詢均未命中時送出 Esc。路徑最後會移動至 (958,975)、點擊並要求 `ExitScript(1)`。','',
              '新增 423 筆指令，16 組固定副本測試覆蓋其中 414 筆並核對 1,814 個事件。每版各有 3 筆位於退出要求後，這些記錄仍留在逐筆檔。VBScript 以固定時鐘求值，截圖、輸入及退出要求由記錄物件接收。實際檔案寫入與重新建立根工作生命週期仍待驗證。','',
              '覺醒、死亡與塔場的五個入口另有 28 組案例，核對 2,774 個事件，觀測 2,229 筆新增指令中的 685 筆。 [對照原記錄](覺醒死亡與塔場.md)']
    (out/'重新啟動與擷取.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


def write_routes(out):
    guide = ['# 圖二、紫金門、圖三與換角色','',
             '逐筆檔保留原操作碼、位置欄、文字索引及第四欄。子程序名稱依原追蹤文字與圖檔推定。','',
             '| 模組 | 新增指令 | 原文案例 | 事件 | 新段觀測指令 |',
             '| --- | ---: | ---: | ---: | ---: |']
    entries = []
    for module in CORE_STARTS:
        plan = load(f'data/battle-routes-{module}.json')
        report = load(f'verification/battle-routes-{module}-original-vs-rebuild.json')
        names = {start for start,_,_ in ROUTE_RANGES[module]}
        plan['routines'] = [r for r in plan['routines'] if r['entry'] in names]
        write_listing(out/f'{module}-地圖與換角色逐筆偽碼.txt',f'模組 {module} 的地圖與換角色',plan)
        guide.append(f'| [{module}]({module}-地圖與換角色逐筆偽碼.txt) | {report["new_records"]} | {report["cases"]} | {report["external_events"]} | {len(report["covered_new_records"])} |')
        entries.extend(['',f'### 模組 {module}','',
                        '| 子程序 | 跳過定義 | 入口 | 返回 |',
                        '| --- | --- | --- | --- |'])
        for start,last,name in ROUTE_RANGES[module]:
            entries.append(f'| {name} | L{start-1} → L{last+1} | L{start} | L{last} |')
        entries.extend(['', f'[原文比對](../../verification/battle-routes-{module}-original-vs-rebuild.json)'])
    guide += ['', '## 圖二與分開驗證的掃描入口','']
    for module,(checkpoint,target) in MAP_SCAN_CHECKPOINTS.items():
        guide.append(f'{module} 的 L{checkpoint-1} 直接跳到 L{target}。測試另從 L{checkpoint} 進入被略過的掃描，逐項核對座標回傳。這些案例以明示框架開始。')
        guide.append('')
    guide += ['辨識 216、212 時，第二張圖的座標分別寫入 INTX16／INTY16、INTX12／INTY12。後續 212 色碼查詢寫入 INTX122／INTY122。原找圖座標、寫回與後續條件都保留。','',
              '## 換角色與工作','',
              '01 的 L8795、03 的 L3260 先處理畫面入口，再依前一角色與目標角色選擇完成後的操作及各角色點擊路徑。每版各有 30 個角色分支。03 L5395 建立工作，L5397 建框架後從 L5398 呼叫重啟 L5885；父流程從 L5400 接回 ID 並寫入區域變數。01 L11335 呼叫 L11961 的三次周獎勵流程。','',
              '## 子程序位置',''] + entries
    (out/'地圖流程與換角色.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


def write_tail(out):
    guide = ['# 進本、道具欄、圖四與技能圖','',
             '三版新增 19 個可呼叫子程序。名稱依原追蹤文字、圖片和流程推定。逐筆檔保留原記錄位置、操作碼、文字索引及第四欄。','',
             '| 模組 | 新增指令 | 原文案例 | 比對事件 | 新段觀測指令 |',
             '| --- | ---: | ---: | ---: | ---: |']
    entries = []
    for module,ranges in TAIL_RANGES.items():
        plan = load(f'data/battle-tail-{module}.json')
        report = load(f'verification/battle-tail-{module}-original-vs-rebuild.json')
        entries_set = {start for start,_,_ in ranges}
        plan['routines'] = [r for r in plan['routines'] if r['entry'] in entries_set]
        write_listing(out/f'{module}-進本與技能擷取逐筆偽碼.txt',f'模組 {module} 的進本與技能擷取',plan)
        guide.append(f'| [{module}]({module}-進本與技能擷取逐筆偽碼.txt) | {report["new_records"]} | {report["cases"]} | {report["external_events"]} | {len(report["covered_new_records"])} |')
        entries.extend(['',f'### 模組 {module}','',
                        '| 子程序 | 入口 | 返回 |',
                        '| --- | --- | --- |'])
        for start,last,name in ranges:
            entries.append(f'| {name} | L{start} | L{last} |')
        entries.extend(['',f'[原文比對](../../verification/battle-tail-{module}-original-vs-rebuild.json)'])
    guide += ['', '## 進本與道具欄','',
              '按鈕進本先辨識畫面，再讀取選到的版本。版本 3 和 4 的 XX、YY 原式使用不同常數起點與寬度。原文先執行 RND，再核對區間並供應上下緣，供後續移動與點擊比對。兩組區間從 01 L1042、03 L550、06 L896 分別測試，這些位置以明示的版本狀態開始。完整進本入口另有自己的測試。','',
              '道具欄選擇值 0 直接返回，值 1 至 4 分別走原道具欄操作。01、06 保留「再來一次」及圖四主體，03 保留播放計時、剩餘次數檢查與進本畫面確認。','',
              '## 技能圖與死亡工作','',
              '01 L11701–L11715、06 L8600–L8614 各發出八次 DM.Capture，分別對應 Q、W、E、R、A、S、D、F。測試保留各自矩形、原路徑拼法、延遲與 DM_RET；擷取由記錄物件接收。01 L11719 另寫回技能擷取完成的共享鍵。','',
              '06 L841 啟動工作，L843 建工作框架，接著呼叫塔場 L6620。父流程越過工作入口後保存返回的 ID。此批保留死亡與覺醒子程序的各自條件，實際並行時序仍待核對。','',
              '## 子程序位置',''] + entries
    (out/'進本道具欄與技能圖.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


def write_scan(out):
    guide = ['# 找圖計數、主流程尾段與介面記錄','',
             '| 模組 | 找圖計數入口 | 返回 | 已接指令 | 剩餘可讀記錄 | 缺失記錄 |',
             '| --- | --- | --- | ---: | ---: | ---: |']
    for module,((entry,last,_),) in SCAN_RANGES.items():
        plan = load(f'data/battle-scan-{module}.json')
        audit = load(f'data/battle-remaining-{module}.json')
        plan['routines'] = [r for r in plan['routines'] if r['entry']==entry]
        write_listing(out/f'{module}-找圖計數逐筆偽碼.txt',f'模組 {module} 的逐行找圖計數',plan)
        guide.append(f'| [{module}]({module}-找圖計數逐筆偽碼.txt) | L{entry} | L{last} | {audit["linked"]} | {len(audit["records"])} | {audit["missing"]} |')
    guide += ['', '## 找圖計數','',
              '三版以具名欄位保存原矩形和目前掃描矩形。Runner 全域 FindPic 把座標寫入兩個 ByRef 臨時變數，再轉存 X、Y。命中符合原列條件時，N 加一，左邊界改為 X+1，上邊界改為 Y。當目前左邊界已移動而本輪未計數時，將左邊界恢復並從 H+1 換列。其餘情況將 N 寫入框架回傳欄並返回。','',
              '三版各 3 組固定副本案例，核對 36 次查詢、矩形更新、ByRef 座標及回傳數量 0、3、2。每版觀測 30 筆中的 29 筆；絕對回跳之後的相對跳轉仍列在逐筆偽碼。現存記錄中未找到直接進入這三個入口的呼叫或跳轉，測試以原類別建立明示框架。','',
              '## 主流程與介面','',
              '01 L562–L740 是保留的主流程尾段，第一筆讀取根槽 17，L740 跳回缺失位置 L433。06 L570–L571 保留 100 毫秒等待及回跳到缺失位置 L421。兩段已另以明示初始狀態做副本比對。 [主流程保留尾段](主流程保留尾段.md)','',
              'Form1 的等待訊息及事件泵各在 01 L13569/L13570、03 L6421/L6422、06 L10253/L10254。06 的 CLICK.FORM1.BUTTON1 保留於 L73–L86，含資料夾清除要求和訊息；前批已有記錄物件測試。本批按原記錄盤點了介面與分隔跳轉，尚未把三版尾端接成同一個介面執行流程。','',
              '[01 剩餘記錄](../../data/battle-remaining-01.json) [03 剩餘記錄](../../data/battle-remaining-03.json) [06 剩餘記錄](../../data/battle-remaining-06.json)']
    (out/'找圖計數與剩餘記錄.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


def write_root(out):
    guide = ['# 主流程保留尾段','',
             '| 模組 | 入口與末筆 | 跳回缺失位置 | 副本案例 | 比對事件 | 尾段觀測指令 |',
             '| --- | --- | --- | ---: | ---: | ---: |']
    for module,(entry,last,target) in ROOT_SUFFIX.items():
        stem = f'battle-root-{module}'
        plan = load(f'data/{stem}.json')
        report = load(f'verification/{stem}-original-vs-rebuild.json')
        plan['routines'] = [r for r in plan['routines'] if r['entry']==entry]
        write_listing(out/f'{module}-主流程尾段逐筆偽碼.txt',f'模組 {module} 的主流程尾段',plan)
        guide.append(f'| [{module}]({module}-主流程尾段逐筆偽碼.txt) | L{entry}–L{last} | L{target} | {report["cases"]} | {report["external_events"]} | {len(report["covered_new_records"])} |')
    guide += ['', '01 的 L562 讀取根槽 17，副本以明示值 3 開始。已核對戰鬥啟動、圖三、換角前置、換角、辨識、重新進本及回到戰鬥流程，再由 L740 跳到 L433。另兩組案例分別重現換角守衛持續命中、找色持續未命中的循環，於 1,200 步上限停止。','',
              '06 的 L570 發出 100 毫秒等待，L571 直接跳到 L421。兩版比對使用根流程進入，子程序按原呼叫建立框架。01 另核對根槽 17 至 51 的最終值，包括仍為 Empty 的槽位。','',
              'L433、L421 都落在缺失區。副本在讀到缺失指令前停下，入口之前的真實狀態仍待還原。遊戲畫面、輸入與工作排程由測試觀測和記錄物件提供。','',
              '[01 原文比對](../../verification/battle-root-01-original-vs-rebuild.json) [06 原文比對](../../verification/battle-root-06-original-vs-rebuild.json)']
    (out/'主流程保留尾段.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


def write_retained(out):
    form = load('verification/battle-form-original-vs-rebuild.json')
    guide = ['# 三版保留指令、預設入口與 Form1','',
             '將每版現存指令依原順序排成完整索引。子程序名稱和宿主動作是依原記錄解讀的名稱，缺失位置維持原編號。','',
             '| 模組 | 可讀記錄 | 缺失 | 預設入口首次缺失 | Form1 訊息與事件泵 |',
             '| --- | ---: | ---: | --- | --- |']
    for module in CORE_STARTS:
        base = load(f'data/battle-{module}.json')
        retained = load(f'data/battle-retained-{module}.json')
        actions = {a['record']:a for a in base['actions']+retained['actions']}
        routine_names = {r['entry']:r['name'] for r in base['routines']+retained['routines']}
        label = f'{module}-全部保留記錄偽碼.txt'
        gate = retained['form_gate']
        guide.append(f'| [{module}]({label}) | {len(actions)} | {len(retained["boundaries"])} | L{form["default_entry_boundaries"][module]} | L{gate}、L{gate+1} |')
        rows = [f'# 模組 {module} 的保留記錄索引','']
        for at in range(retained['total_records']):
            if at in routine_names:
                rows.extend(['',f'## {routine_names[at]} L{at}',''])
            action = actions.get(at)
            if action is None:
                rows.append(f'L{at} 原記錄缺失')
                continue
            provenance = f'op={action["opcode"]}, loc={action["location"]}, SL={action["source_sl"]}, field_3={action["field_3"]}'
            rows.append(f'L{at} {describe(action)}  // {provenance}')
        (out/label).write_text('\n'.join(rows)+'\n',encoding='utf8')
    guide += ['', '預設入口在隔離副本逐筆走完原宣告，再分別停於 L62、L40、L56。01 和 06 的保留尾段另由已知狀態開始，回跳至缺失的 L433、L421。這兩類測試使用不同入口。','',
              'Form1 的九組案例比對 63 個步驟，包括等待訊息、等待事件、關閉後停止本輪，以及允許繼續時經原相對跳轉走到結束。06 的按鈕回呼位於 L73–L86，兩次點擊均回到 L10254。記錄替身共收到十次資料夾清除要求、兩次通知，FILE 只載入一次。','',
              '已為三版的每個可讀位置安排對應動作。覆蓋包含宣告、定義略過、介面與各批已接子程序。這份逐筆索引還有 1,328 個缺失位置，實際介面宿主、各分支覆蓋與並行時序仍待還原。 [原文比對](../../verification/battle-form-original-vs-rebuild.json)']
    (out/'保留指令與介面入口.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


def main():
    out = PROJECT/'analysis/shared-battle'
    out.mkdir(exist_ok=True,parents=True)
    guide = ['# 模組 01、03、06 的戰鬥與副本子程序','',
             '三版共有 6,405 筆保留指令已轉成事件模型。每版保留原位置、操作碼、文字索引和第四欄。子程序標題依保留文字或行為命名。','',
             '| 模組 | 指令 | 子程序 | 原文案例 | 比對事件 | 不同觀測指令 |','| --- | ---: | ---: | ---: | ---: | ---: |']
    for module in CORE_STARTS:
        plan = load(f'data/battle-{module}.json')
        report = load(f'verification/battle-{module}-original-vs-rebuild.json')
        guide.append(f'| [{module}]({module}-逐筆偽碼.txt) | {len(plan["actions"])} | {len(plan["routines"])} | {report["cases"]} | {report["external_events"]} | {report["records_covered"]} |')
        write_listing(out/f'{module}-逐筆偽碼.txt',f'模組 {module} 的戰鬥與副本流程',plan)
    guide += ['', '## 共用與各版差異','',
              '以 01 為基準，50 組同名比較中有 38 組一致。比對保留原文字、操作碼及第四欄，校正指令位置，將子程序呼叫目標對應到同名子程序。三版的四組技能與七種技能模式屬於一致的子程序。', '',
              '03 的四段數字 1 吃藥、過門、退出副本、找按鈕和伺服器檢查有差異。06 的退出副本、修理、找按鈕與找對話有差異。各版分別保留原找色範圍、延遲、子呼叫和迴圈。 [逐組比較](../../data/battle-family-comparison.json)','',
              '## 找圖比較與隨機座標','',
              '`V…=DM_RET=DM.FINDPIC(…)` 將既有 DM_RET 和本次找圖回傳值比較，再把布林值存入左側變數。INTX、INTY 仍接收本次查詢座標，DM_RET 保留原值。01 的 L3664、03 的 L2468 及 06 的 L3486 都觀測到 True 和 False。','',
              '03 的 L2389、L2407 使用 `INT(10*RND+INTY)`。副本先核對原式生成值落在原區間，再供應區間端點比較後續滑鼠座標。','',
              '## 驗證範圍','',
              '165 組固定副本案例核對 13,844 個事件，觀測 4,330 筆不同保留指令。原文字由 Windows VBScript 執行，從明示的子程序入口、合成共享值和觀測開始。外掛與輸入由記錄物件接收。三版完整入口、其餘子程序、分支及實際時序仍待還原。 [01 比對](../../verification/battle-01-original-vs-rebuild.json) [03 比對](../../verification/battle-03-original-vs-rebuild.json) [06 比對](../../verification/battle-06-original-vs-rebuild.json)']
    (out/'戰鬥與副本流程.md').write_text('\n'.join(guide)+'\n',encoding='utf8')
    write_control(out)
    write_restart(out)
    write_routes(out)
    write_tail(out)
    write_scan(out)
    write_root(out)
    write_retained(out)


if __name__ == '__main__':
    main()
