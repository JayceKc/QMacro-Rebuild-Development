"""Static provenance guide for the preserved monitor. No VBScript evaluation."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/revival-recovery';OUT.mkdir(exist_ok=True)
path=ROOT/'outputs/QMacro-Rebuild-Development/programs/10.json'
p=json.loads(path.read_text(encoding='utf-8'))
queries=[1565,1569,1575,1579,1585,1589,1595,1599]
rows=[]
for n,pc in enumerate(queries,1):
    cond=pc+1;branch=pc+2
    assert p['code'][cond][0]==4 and p['code'][branch][0]==6
    target=branch+p['code'][branch][2];assert target==1635
    rows.append({'stage':n,'query_record':pc,'query_source_sl':p['code'][pc][2],
        'source':p['strings'][p['code'][pc][2]],'condition_record':cond,
        'condition_source':p['strings'][p['code'][cond][2]],'failure_jump_record':branch,
        'failure_target':target,'next_loop_target':1635+p['code'][1635][2]})
assert not any(i in p['missing_records'] for i in range(1551,1639))
data={'program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'entry':1551,'loop':1560,
      'body_end':1638,'all_88_original_records_present':True,'stages':rows,
      'sdk_marker_recovered':False,'class_entry_mapping_inferred':True,
      'runtime_test_status':'18 controlled original-body guest cases passed; 596 owned translation events match','original_script_executed_by_this_generator':False}
(OUT/'revival-source-map.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 死亡監控與復活：可回查解讀','',
 '入口 L1551；主迴圈 L1560；主體結束 L1638。88 筆原記錄均保留，沒有補入缺失指令。',
 '「監控死亡」類別與此入口配對仍標為推定；此文件只解讀保留主體，不冒充原始初始化跳轉已解。','',
 '## 八階段判定','',
 '每次檢查都只以 INTX >= 0 決定是否繼續；不使用 FindColor／FindPic 的整數回傳值。',
 '任一階段失敗都跳到 L1635，再回到 L1560，沒有進入下方滑鼠與工作控制區段。','',
 '| 階段 | 查詢記錄 | 條件記錄 | 失敗跳轉 | 保留呼叫 |','| --- | --- | --- | --- | --- |']
for r in rows:lines.append(f'| {r["stage"]} | L{r["query_record"]} / SL{r["query_source_sl"]} | L{r["condition_record"]} | L{r["failure_jump_record"]} → L1635 → L1560 | `{r["source"].replace("|","／")}` |')
lines+=['','## 可讀偽碼','', '以下名稱為重建名稱；括號內編號可回查 programs/10.json。','', '```text',
 '建立辨識物件，設定滑鼠模式 (L1552..1558)',
 '等待 5 秒 (L1559)',
 '迴圈 (L1560):',
 '    等待 3 秒 (L1562)',
 '    用共享 SDK 標記查色，成功才繼續 (L1563..1567)',
 '    等待 1 秒，找 si.bmp，成功才繼續 (L1568..1571)',
 '    等待 1 秒，再查 SDK 標記 (L1572..1577)',
 '    等待 1 秒，查 FFD200-050505 黃色 (L1578..1581)',
 '    等待 1 秒，再查 SDK 標記 (L1582..1587)',
 '    等待 1.5 秒，再找 si.bmp，容差改為 050505 (L1588..1591)',
 '    等待 1.5 秒，再查 SDK 標記 (L1592..1597)',
 '    等待 1.5 秒，再查黃色 (L1598..1601)',
 '    儲存原游標位置 (L1603)',
 '    暫停共享變數指定的兩個工作 ID (L1606..1612)',
 '    移到 (1377,345)，按左鍵；再移到同點，按左鍵 (L1616..1623)',
 '    移回原游標位置 (L1625)',
 '    恢復同名共享變數目前指定的兩個工作 ID (L1627..1633)',
 '    等待 5 秒，回到迴圈 (L1634..1635)',
 '    任一畫面條件失敗：直接回到迴圈，略過上述操作',
 '```','',
 '## 執行緒、事件與外部依賴','',
 '- 此主體沒有介面事件；啟動入口由主程式建立工作。新重建初始化依 CheckBox3 決定是否啟動，但原缺失的啟動運算元仍未恢復。',
 '- ThreadControl 的 ID 由共享變數在暫停／恢復前各自讀取，不能假設其他工作從未修改它們。',
 '- GetCursorPos、EnableRealMouse、MoveTo、FindColor、FindPic、共享變數、ThreadControl、MouseClick 皆需要明確後端。',
 '- SDK 標記的實際色碼尚未取得；查詢原樣要求「共享標記 + -151515」。不把測試色碼寫成正式預設值。',
 '- 原 si.bmp 路徑、座標與容差保留在來源；真實遊戲判定與原外掛滑鼠模式尚未驗證。',
 '- 18 組原文測試已在副本通過，與重建的 596 個事件一致；使用受控結果及只記錄的滑鼠替身，仍非遊戲實際復活證據。','']
(OUT/'復活流程解讀.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'entry':1551,'records':88,'stages':8,'failure_target':1635,'script_executed':False}))
