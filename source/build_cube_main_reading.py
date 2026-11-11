"""Generate the preserved parent/helper reading files from the joined plan."""
import json
import re

from export_cube_main import JOINED
from export_cube_routines import ARRAY, FRAME, PROJECT, TEMP


def main():
    plan = json.loads((PROJECT / 'data/cube-main.json').read_text(encoding='utf8'))
    out = PROJECT / 'analysis/cube'
    out.mkdir(exist_ok=True, parents=True)
    calls = {c['record']: c for c in plan['joined_calls']}
    shared_names = {
        'V8186B4D47378756D': 'sdk_marker',
        'V8080D6BCC7B6BF904D6A65757378756D': 'run_counter',
        'V80C2DCADC7B6BF904D6A65757378756D': 'display_counter',
        'V9BBAD991CA85B8D1042E65757378756D': 'worker_id',
        'VF0ADACDECCD2BFD14D6A65757378756D': 'first_character',
    }
    symbols = sorted({a['key'] for a in plan['actions'] if 'key' in a})
    aliases = {key: shared_names.get(key, f'shared_{i:02d}') for i, key in enumerate(symbols, 1)}

    def readable(source):
        pieces = re.split(r'("(?:[^"]|"")*")', source)
        for i in range(0, len(pieces), 2):
            pieces[i] = pieces[i].replace(FRAME + '.' + ARRAY, 'frame.slots').replace(TEMP, 'temporary')
        return ''.join(pieces)

    def describe(a):
        at, kind = a['record'], a['kind']
        if kind == 'if_zero':
            return f'若條件為零則跳 L{a["target"]}，否則前往 L{at + 1}'
        if kind == 'jump':
            return f'跳往 L{a["target"]}'
        if kind == 'call':
            c = calls[at]
            return f'呼叫 L{c["target"]}，返回 L{c["return_pc"]} 時將暫存值寫入父槽 {c["return_slot"]}'
        if kind == 'frame_enter':
            return f'保存父框架並建立空白子框架 {a["class_name"]}'
        if kind == 'frame_restore_intent':
            return '讀取子框架的回傳欄位至 temporary，然後還原父框架'
        if kind == 'return':
            return '返回呼叫堆疊中的下一個位置'
        if kind in ('read_global', 'write_global'):
            key = a['key']
            lhs, rhs = ('temporary', aliases[key]) if kind == 'read_global' else (aliases[key], 'temporary')
            return f'{lhs} = {rhs} [共享原鍵 {key}]'
        if kind == 'ui_write':
            return f'{a["path"]} = CStr(temporary)'
        if kind == 'test':
            return 'condition = ' + readable(a['source'])
        return readable(a['source'])

    for first, last, name in JOINED[:3]:
        lines = [f'# {name} L{first}..L{last}', '', '每行標示原操作碼、位置、文字索引與第四欄。共享別名為重建名稱，檔名與原文字常數依原資料保留。', '']
        for a in plan['actions']:
            if first <= a['record'] <= last:
                lines.append(f'L{a["record"]} {describe(a)}  // op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}, field_3={a["field_3"]}')
        (out / f'{first}-{name}_逐筆偽碼.txt').write_text('\n'.join(lines) + '\n', encoding='utf8')

    guide = '''# 魔方上層流程與子程序銜接

這份事件模型從保留入口 L1677 串接五個子程序，共 3,977 筆。這一輪新增上層 1,687 筆、「找按鈕」122 筆和 ALT+Q 檢查 33 筆，並沿用先前比對過的三段共 2,135 筆。

- L1677 至 L3363 的上層控制流包含 143 個條件、41 次子程序呼叫位置、3 個介面寫入和 4 個執行緒控制位置。 [逐筆偽碼](1677-魔方上層保留流程_逐筆偽碼.txt)
- 「找按鈕」在 L3377 和 L3425 呼叫 L6657，完成後接回原來的判斷。 [找按鈕逐筆偽碼](3365-找按鈕_逐筆偽碼.txt) [ALT+Q 檢查逐筆偽碼](6657-檢查新舊ALTQ_逐筆偽碼.txt)
- 完整指令資料附有 43 組呼叫位置、原框架類別宣告和回傳槽。 [動作資料](../../data/cube-main.json) [自有事件模型](../../source/qmacro_cube_main.py)

## 入口與循環

L1678 至 L1682 記錄原 DM 建立、錯誤顯示設定與實體滑鼠模式要求，並要求宿主提供滑鼠模式設定的回傳值。L1685 的固定 True 進入等待循環。L1690 以共享 SDK 色碼辨識畫面，後續按放大鏡、圖示與顏色等觀測選擇分支。L3360 回到 L1685，會重新讀共享值。從這個入口可由子程序的 ExitScript 停止，末端 L3363 的返回則位於固定條件排除的出口。

原保留指令中未找到指向 L1677 的 op12 呼叫或 op24 啟動位置。重播以 L1677 和明示的父框架、初始共享值開始。原入口前綴與父框架來源仍待辨識。

## 父框架與返回位置

每個呼叫前一筆先建立子框架並保存父框架。op12 再把呼叫後一筆推入返回堆疊。子程序的還原語句讀取回傳欄位、恢復父物件，op13 才回到呼叫後一筆，把暫存回傳值寫入父槽。新建子框架的回傳欄位初值為 Empty，這批保留語句沒有對該欄位賦值。

L1755 呼叫換角色後回到 L1756，父槽 5 接收 Empty。若 L1760 呼叫完成後操作並到達 L6746 的 ExitScript，執行會停在 L6746，L1761 的父槽寫回也不會發生。接周任務則從 L2159 進入，正常回傳至 L2160 的父槽 47。

雙層案例從 L2241 呼叫「找按鈕」，再由 L3377 呼叫 ALT+Q 檢查。L6689 返回 L3378 時恢復「找按鈕」的框架，L3486 返回 L2242 才恢復上層框架。測試用父槽 255 的標記確認它在這兩次還原後仍可讀取。

## 介面、共享值與工作控制

L2352 和 L2357 分別更新兩個共享計數器，L2359 重新讀第二個計數器，再由 L2363 將字串寫入 `Form1.InputBox2.Text`。另外兩條對應路徑在 L2694/L2699/L2705 及 L3003/L3008/L3014。`display_counter` 是依資料流推定的別名。

L2169 的工作控制操作是 2，L3326、L3345、L3356 的操作是 1。各處皆先從共享鍵讀取工作 ID。事件模型保留這些 ID 與操作參數，實際執行緒的暫停與恢復需在整合宿主中另行核對。

## 驗證範圍

31 組固定副本案例對照 5,151 個事件，涵蓋 1,098 筆指令、7 個呼叫位置及全部 3 個介面寫入位置。70 次返回前的框架恢復均核對實際父物件身分和 Empty 回傳值。兩個找按鈕入口、第二次 ALT+Q 及其按鍵按下與放開順序均有案例。 [比對報告](../../verification/cube-main-original-vs-rebuild.json)

副本以明示的合成初值和父框架進入 L1677。原 VBScript 在 Windows 引擎執行，L1678 建立 DM 的語句接到記錄替身，工作控制採未匹配的測試 ID。案例核對呼叫參數、跳轉、共享值、父槽和介面文字。其餘呼叫位置、實際工作並行和正式遊戲後端仍待驗證。先前 191 組比對涵蓋三個獨立子程序入口。 [三段原文比對範圍](魔方_可讀流程.md)
'''
    (out / '魔方_上層銜接.md').write_text(guide, encoding='utf8')
    print(json.dumps({'new_readable_records': 1842, 'joined_records': len(plan['actions'])}))


if __name__ == '__main__':
    main()
