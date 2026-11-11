"""Readable reconstruction and explicit control edges for all intact bodies."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'data/gathering-routines.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
OUT=ROOT/'analysis/gathering' if PROJECT==ROOT else ROOT/'outputs/gathering-recovery'


def main():
    load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    plan=load(PROJECT/'data/gathering-routines.json');worker=load(PROJECT/'data/gathering-worker.json')
    check=load(PROJECT/'verification/gathering-routines-original-vs-rebuild.json');wc=load(PROJECT/'verification/gathering-worker-original-vs-rebuild.json')
    owned=load(PROJECT/'verification/gathering-routines-owned.json');aliases=plan['name_roles'];actions={a['record']:a for a in plan['actions']}
    def numeric(n):
        if 'const' in n:return str(n['const'])
        if 'name' in n:return aliases.get(n['name'],n['name'])
        op=n['op'];args=[numeric(a) for a in n['args']]
        if op in ('SGN','ATN','INT'):return op+'('+args[0]+')'
        if op.startswith('UNARY'):return op[-1]+args[0]
        return '('+(' '+op+' ').join(args)+')'
    def expr(n):
        if 'numeric' in n:return numeric(n['numeric'])
        if 'const' in n:return json.dumps(n['const'],ensure_ascii=False)
        if 'slot' in n:return 'current_frame.slot['+str(n['slot'])+']'
        if 'concat' in n:return ' & '.join(expr(a) for a in n['concat'])
        raise ValueError(n)
    def describe(a):
        k=a['kind']
        if k=='delay':return f'等待 {a["milliseconds"]} ms'
        if k=='test':return 'condition = '+expr(a['condition'])
        if k=='if_zero':return f'若 condition = 0，跳到 L{a["target"]}'
        if k=='jump':return f'跳到 L{a["target"]}'
        if k=='call':return f'呼叫 返回莊園 L{a["target"]}'
        if k=='return':return '返回呼叫端'
        if k=='assign':return a['role']+' = '+expr(a['value'])
        if k in ('key_press','key_down','key_up','mouse_click','move_to','thread_control'):return k+'('+', '.join(expr(x) for x in a['arguments'])+')'
        if k=='read_global':return f'temporary = 讀取共享值 {a["role"]} [原鍵 {a["global_key"]}]'
        if k=='store_temp':return f'current_frame.slot[{a["slot"]}] = temporary'
        if k=='frame_enter':return '建立 返回莊園 呼叫框架，保存 parent'
        if k=='frame_restore':return 'temporary = current_frame.return_value（未賦值時 Empty）；恢復 parent，釋放暫存框架'
        if k=='exit_script':return '結束腳本 ExitScript(0)'
        if k=='trace':return '記錄 '+expr(a['value'])
        if k=='randomize':return '初始化原亂數來源（事件重播不偽造時鐘）'
        if k=='random_int':return f'{a["role"]} = 受控整數 [{a["lower"]}, {a["lower"]+a["span"]-1}]'
        if k in ('find_color','find_pic','builtin_color'):
            value=expr(a['spec']);extra=(', delta='+expr(a['delta'])) if k=='find_pic' else ''
            return f'query_x, query_y = {k}(ROI={a["rect"]}, {value}{extra}, similarity={a["similarity"]}, direction={a["direction"]})'
        raise ValueError(k)
    OUT.mkdir(parents=True,exist_ok=True)
    pseudo=['# 模組08三個保留主體：名稱為語義重建；L/SL可回查原記錄。','# 等待、按鍵、讀圖均為事件；本檔不執行原文或遊戲操作。','']
    for routine in plan['routines']:
        pseudo+=['',f'procedure {routine["name"]}  // L{routine["entry"]}..L{routine["last"]}']
        for i in range(routine['entry'],routine['last']+1):
            a=actions[i];pseudo.append(f'L{i}: {describe(a)}  // op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}')
    (OUT/'採集_修理回家活力_逐筆偽碼.txt').write_text('\n'.join(pseudo)+'\n',encoding='utf8')
    branches=[{'record':a['record'],'condition_record':a['record']-1,'false_target':a['target'],'true_target':a['record']+1} for a in actions.values() if a['kind']=='if_zero']
    loops=[{'record':a['record'],'target':a['target']} for a in actions.values() if a['kind']=='jump' and a['target']<a['record']]
    calls=[{'record':a['record'],'target':a['target']} for a in actions.values() if a['kind']=='call']
    reachable=set();pending=[r['entry'] for r in plan['routines']]
    while pending:
        i=pending.pop()
        if i in reachable or i not in actions:continue
        reachable.add(i);a=actions[i];kind=a['kind']
        if kind in ('exit_script','return'):continue
        if kind=='jump':pending.append(a['target'])
        elif kind=='if_zero':pending.extend((a['target'],i+1))
        elif kind=='call':pending.extend((a['target'],i+1))
        else:pending.append(i+1)
    unreachable=sorted(set(actions)-reachable)
    assert unreachable==owned['uncovered_records'],unreachable
    evidence={'source_program_sha256':plan['source_program_sha256'],'routines':plan['routines'],'conditional_branches':branches,'back_edges':loops,'calls':calls,
              'controlled_original_cases':check['cases'],'external_events':check['external_events'],'records_covered':check['records_covered'],
              'exit_aware_cfg_unreachable':unreachable,'worker_controlled_original_cases':wc['cases'],'worker_events':wc['external_events'],
              'worker_normal_unreachable':[913,914],'worker_start_unknown':True,'full_module_restored':False}
    (OUT/'gathering-routines-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# 採集：修理、回家、活力與常駐 G 流程','',
           f'三個主體共703筆原記錄，{check["cases"]}組固定副本原文案例／{check["external_events"]}個事件一致；覆蓋{check["records_covered"]}筆。另有25筆G工作，41組案例／439事件一致，正常可達23筆。',
           '本頁與逐筆偽碼解讀的是完整保留子程序。前500筆仍缺，原時間、真實並行與遊戲端到端未完成。測試SDK字串112233是合成輸入，未找回真正MMVerifyCode。','',
           '## 閱讀入口','',
           '- [三個子程序逐筆偽碼](採集_修理回家活力_逐筆偽碼.txt)：每行附L、原操作碼、location與SL。',
           '- [條件、迴圈、子程序與覆蓋清單](gathering-routines-evidence.json)。',
           '- [三個主體的完整動作資料](../../data/gathering-routines.json)、[G工作完整動作資料](../../data/gathering-worker.json)。',
           '- [原703筆副本觀測](../../verification/original-gathering-routines.json)、[逐案比較](../../verification/gathering-routines-original-vs-rebuild.json)。','',
           '## 入口與介面設定','',
           '| 重建名稱 | 入口 | 直接保留的呼叫證據 |','| --- | --- | --- |',
           '| 工具紅了（語義名） | L916..1275 | L613建立類別、L614呼叫916 |',
           '| 返回莊園 | L1277..1342 | L1155/1156、1184/1185、1438/1439、1487/1488 |',
           '| 檢查活力（語義名） | L1344..1620 | L605建立類別、L606呼叫1344 |',
           '| 常駐採礦G（推定名） | L890..914 | 啟動點在缺失前綴中；未證實其原工作身分 |','',
           '這四個主體沒有保存的介面事件回呼或新執行緒建立指令。它們讀設定或控制已有工作；不能因此說整個模組沒有回呼／新工作。保留字串SL36/38對應ComboBox2與repair_strategy、SL40/42對應ComboBox3與vitality_finish_mode、SL48/51對應CheckBox3與home_on_no_vitality、SL54/57對應CheckBox2與home_on_no_durability。前綴指令已缺，以上介面讀取順序的控制邊仍未驗證。','',
           '## 工具紅了：L916..1275','',
           '先讀共享工作值，在L919送ThreadControl(id,1)。策略0走Alt/P、隨機座標（X=1233..1252、Y=695..709）與點擊流程；策略1走找圖修理、SDK等待及銀幣顏色確認，遇到未命中會依原回邊重試。所有重複Alt/P、ctrl/alt按下和放開均保留，不自行刪除。','',
           '| repair_strategy | 原分支 | 結束行為 |','| --- | --- | --- |',
           '| 0 | L921起 | 完成點擊流程後走L1269恢復 |',
           '| 1 | L982起 | 找圖／顏色確認與循環後走L1269恢復 |',
           '| 2 | L1141 | ExitScript(0) |',
           '| 3 | L1149 | 可選回家，ctrl/alt切換，F10兩次，停止 |',
           '| 4 | L1178 | 可選回家，ctrl/alt切換，F8兩次，停止 |',
           '| 5 | L1207 | ctrl/alt切換，F6兩次，停止 |',
           '| 6 | L1229 | 退出遊戲的滑鼠／Enter／End／F12操作意圖，停止 |',
           '| 其他 | 各等號皆不成立 | 走恢復與返回 |','',
           'L1270重新讀取同一個共享工作鍵，再於L1272送ThreadControl(id,2)。原碼未保存最初ID；受控更新案例確實從12345的暫停變成54321的恢復。這是原行為，不改成自動恢復最初ID。策略2..6的停止路徑不會走到恢復尾段。','',
           '## 返回莊園：L1277..1342','',
           '清零sdk_miss_count，循環按F2並找zhuangy1/2.bmp。找得到時，按原右鍵／點擊順序選擇莊園與確認；找不到時檢查SDK色碼（容差050505）。連續未命中三次會按Esc並清零計數，然後重試。完成選擇後還會以151515容差等待SDK色碼，再恢復呼叫框架並返回Empty。','',
           '## 檢查活力：L1344..1620','',
           '先確認SDK色碼，再用Runner內建FindColorEx依序找40752B、35DF86、31B972、3F722A，ROI[875,917,896,932]右下包含。四者皆未命中會按B再循環；SDK連續三次未命中另有Esc與計數重設。這裡使用內建BGR／包含邊界規則，不套DM找色規則。',
           '之後依vitality_finish_mode在DM ROI[898,917,902,931]檢查12項色碼清單。任一次命中就清零並返回；連續五次未命中才執行下表。','',
           '| 模式 | 五次未命中後 |','| --- | --- |',
           '| 0 | 停止腳本 |',
           '| 1 | 暫停讀回的工作值，可選回家，F10兩次，停止 |',
           '| 2 | 暫停讀回的工作值，可選回家，F8兩次，停止 |',
           '| 3 | 暫停讀回的工作值，F6兩次，停止 |',
           '| 4 | 暫停讀回的工作值，退出遊戲操作意圖，停止 |',
           '| -1、5等非介面值 | 不進以上分支，經L1617返回；另兩案已比對 |','',
           'L1432、1481、1530、1573雖分別使用框架槽1、3、5、6，讀的是同一共享鍵；這些槽號不能當成已證明有四個不同工作。測試使用不匹配任何真實工作的ID，只驗證呼叫值與順序，未驗證實際工作暫停／恢復。','',
           '## 常駐G：L890..914','',
           '等待100ms→建立DM物件意圖→關閉DM錯誤提示→等待100ms。每輪等待500ms，重新讀SDK色碼，先以DM查[160,1,260,25]。INTX>0才繼續等待50ms並查kuangG1..4.bmp，ROI[938,606,983,652]。INTX>=0時依序G、50ms、G、70ms、G、100ms，之後L912回894。',
           '條件讀的是INTX，未使用DM_RET決定分支。R894為Sgn(vbTrue)，故正常執行不會到913/914的清理與返回。41個案例包含兩輪更新SDK、命中／未命中、回傳碼反轉及23個位置前的受控停止；這證明記錄路徑，不證明Runner實際取消通知／清理協定。',
           '只有此G案例將L891原CreateObject一行改綁記錄物件；原始行與替換行均保留在source_rewrite事件。三個703筆主體不改寫原語句。所有測試都不載原外掛、不送鍵盤、不真的等待。','',
           '## 尚未覆蓋與限制','',
           f'703筆中未執行：{unreachable}。以ExitScript為終止點、條件雙向保留的控制圖得到相同九筆不可達記錄；它們位於首次停止後。這項證據只涵蓋本頁三個主體，不包含缺失前綴可能的動態入口。',
           'SDK真值、500筆前綴、正式GUI事件、原並行／停止時序、全部辨識圖及遊戲端到端仍未完成。亂數在原賦值執行後覆寫為固定值；不能當成原RNG相同。','',
           '## 原條件與迴圈','',
           '| 條件記錄 | 可讀條件 | 真分支 | 假分支 |','| --- | --- | --- | --- |']
    for b in branches:lines.append(f'| L{b["condition_record"]} | {expr(actions[b["condition_record"]]["condition"])} | L{b["true_target"]} | L{b["false_target"]} |')
    lines+=['','回邊：'+', '.join(f'L{x["record"]}→L{x["target"]}' for x in loops)+'。','']
    (OUT/'採集_修理回家活力與G工作.md').write_text('\n'.join(lines),encoding='utf8')
    print(json.dumps({'routines':3,'records':703,'branches':len(branches),'loops':len(loops),'calls':len(calls),'unreachable':unreachable}))


if __name__=='__main__':main()
