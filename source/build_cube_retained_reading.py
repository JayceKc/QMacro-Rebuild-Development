"""Write the remaining record listing and the scope of the linked cube model."""
from replay_cube_retained import PROJECT,load


def main():
    out = PROJECT/'analysis/cube'
    tail = load('data/cube-retained-tail.json')
    reports = [load(f'verification/cube-{part}original-vs-rebuild.json') for part in ('','main-','workers-','retained-')]
    report = reports[-1]
    covered = set().union(*(set(part['covered_records']) for part in reports))
    lines = ['# 魔方剩餘保留指令','']
    for a in tail['actions']:
        at, kind = a['record'],a['kind']
        if kind=='jump':
            body = f'跳往 L{a["target"]}'
        elif kind=='if_zero':
            body = f'條件為零則跳 L{a["target"]}，否則前往 L{at+1}'
        elif kind=='return':
            body = '回到呼叫堆疊記錄的位置'
        elif kind=='entry_dispatch':
            body = '前往已指定的工作入口。一般腳本啟動依序進入 L31'
        elif kind=='runner_message':
            body = '等待宿主提供 Form1 訊息'
        elif kind=='ui_pump':
            body = '等待 Form1 關閉或已保存的介面事件。此模組的保留資料沒有回呼項目'
        elif kind=='iteration_end':
            body = '本次迭代邊界 op23'
        elif kind=='final_record':
            body = '前進至 L6820，隨後到達記錄末端'
        else:
            body = a['source']
        lines.append(f'L{at} {body}  // op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}, field_3={a["field_3"]}')
    (out/'魔方_入口尾端逐筆偽碼.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
    guide = f'''# 魔方保留入口、等待與技能截圖

剩餘 367 筆已接入連結模型。現有 6,320 筆保留指令全部對應原始位置、操作碼、文字索引與第四欄。L31 至 L530 共 500 筆仍缺。四批固定副本合計 {sum(p['cases'] for p in reports)} 組，實際觀測到 {len(covered):,} 筆不同保留指令。 [剩餘指令偽碼](魔方_入口尾端逐筆偽碼.txt) [事件模型](../../source/qmacro_cube_retained.py)

## 保留入口 L531

一般入口先執行 L0 的根陣列和物件宣告、L1 至 L29 的類別宣告，經 L30 進入缺失的 L31。副本確認缺失會停止執行。L531 可以在明示根槽 11 的情況下受控重播。它先把槽值寫入共享鍵 `V8BBFDCD03A3C756D`，再辨識畫面與讀取技能、找怪、吃藥等工作 ID。

L554 起等畫面。L559 未命中會回到等待，L563 命中也會重試。符合後續分支時，保留 mode 0、1 或 2 的工作控制要求。L659 跳至 L852，L853 再回到缺失的 L451。測試以 4321 作為根槽 11 的明示值，原入口如何產生該值仍待還原。

## 跳轉、定期按鍵與介面等待

受控入口 L854 經 L856 及一連串原始跳轉繞過子程序，最後由 L6815 跳 L6819，再前進至記錄末端 L6820。另從 L6816 驗證等訊息、L6817 等 Form1 關閉、L6818 到達迭代邊界的路徑。保留回呼表為空，這批測試由宿主供應訊息和視窗狀態。

L3488、L3510、L3538 是三段定期按鍵流程，使用固定 True 條件重複延遲並送出鍵名 `5`。保留的外層跳轉會略過這些主體，副本從各自入口受控重播。

## 技能圖動態來源

L6444 起找 `chenm1.bmp` 至 `chenm3.bmp`。L6448 命中時繼續等待，未命中時才離開迴圈。L6457 至 L6471 依序要求擷取 Q、W、E、R、A、S、D、F 八張圖，原矩形和路徑均保留。L6475 將共享鍵 `V86C8B5B7CFC4B1B14D6A65757378756D` 寫為 1。測試以記錄物件接收擷取呼叫，實際技能圖仍取決於遊戲畫面。

## 本批驗證

{report['cases']} 組固定副本比對 {report['external_events']} 個事件、{report['wait_polls']} 次等待檢查及 {report['records_covered']} 筆不同保留指令。逐筆跳轉、根槽、共享值和停止位置相符。L31 與 L451 的缺失邊界、三個定期按鍵入口及八個擷取位置均有案例。完整入口、未覆蓋分支和工作並行仍待還原。 [比對報告](../../verification/cube-retained-original-vs-rebuild.json)
'''
    (out/'魔方_保留入口與尾端.md').write_text(guide,encoding='utf8')


if __name__ == '__main__':
    main()
