"""Readable record listing and dispatch map for the cube workers."""
import json
import re

from export_cube_routines import ARRAY, FRAME, PROJECT, TEMP
from replay_cube_main import load


def main():
    plan = load('data/cube-workers.json')
    report = load('verification/cube-workers-original-vs-rebuild.json')
    out = PROJECT/'analysis/cube'
    by = {a['record']:a for a in plan['actions']}

    def readable(source):
        pieces = re.split(r'("(?:[^"]|"")*")',source)
        for i in range(0,len(pieces),2):
            pieces[i] = pieces[i].replace(FRAME+'.'+ARRAY,'frame.slots').replace(ARRAY,'root_slots').replace(TEMP,'temporary')
        return ''.join(pieces)

    def describe(a):
        kind = a['kind']
        if kind == 'if_zero':
            return f'條件為零則跳 L{a["target"]}，否則前往下一筆'
        if kind == 'jump':
            return f'跳往 L{a["target"]}'
        if kind == 'call':
            return f'呼叫 L{a["target"]}，返回 L{a["record"]+1}'
        if kind == 'worker_start':
            return f'要求啟動工作 L{a["target"]}，將回傳 ID 放入 temporary'
        if kind == 'iteration_end':
            return '原 op23 迭代邊界'
        if kind == 'return':
            return '返回呼叫者'
        if kind == 'read_global':
            return f'temporary = 讀共享鍵 {a["key"]}'
        if kind == 'write_global':
            return f'寫共享鍵 {a["key"]} = temporary'
        return ('condition = ' if kind=='test' else '')+readable(a['source'])

    lines = ['# 魔方工作與保留主體逐筆偽碼','']
    for routine in plan['routines']:
        lines.extend((f'## {routine["name"]} L{routine["entry"]}..L{routine["last"]}',''))
        for at in range(routine['entry'],routine['last']+1):
            a = by[at]
            lines.append(f'L{at} {describe(a)}  // op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}, field_3={a["field_3"]}')
        lines.append('')
    (out/'魔方_工作逐筆偽碼.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')

    guide = ['# 魔方工作啟動與各工作主體','',
             f'新增 {len(by):,} 筆保留指令的事件模型，包含戰鬥工作協調、副本辨識、找怪、技能、過圖、吃藥及普攻。和上層銜接模型合計 5,953 筆互不重複的保留指令。 [逐筆偽碼](魔方_工作逐筆偽碼.txt) [動作與工作資料](../../data/cube-workers.json)','',
             '## 父程序如何保存工作 ID','',
             'op24 的目標等於目前記錄加原 operand。啟動回傳值進 temporary，父程序下一筆跳過工作包裝，依序存槽、複製至另一槽，再寫共享鍵。L717 使用腳本根陣列，L4635 協調流程使用父物件的槽。兩者各自保存。','',
             '工作從自己的入口建立呼叫框架，再呼叫主體。返回後到 op23 迭代邊界。模型由宿主明示提供 ID 與觀測，工作可獨立重播。父程序的跳過路徑與工作入口分開。','',
             '| 啟動 | 工作入口 | 主體 | 迭代邊界 | 父程序繼續 | 共享 ID 寫入 |','| --- | --- | --- | --- | --- | --- |']
    for w in plan['worker_wrappers']:
        guide.append('| '+' | '.join('L'+str(w[k]) for k in ('start_record','worker_entry','body_entry','worker_iteration_end','parent_continue','shared_id_write'))+' |')
    guide.extend(['','## 選擇條件與迴圈','',
                  '戰鬥協調先經 L4636 等待迴圈辨識 SDK 與畫面，再依 L4713 之後的模式讀取選擇找怪工作。技能啟動另外受辨識狀態與模式條件限制。L4796、L4811、L4826、L4841 讀本地技能選擇，對應 Z、不用 Z、更多 Z 與 X。L4856 啟動中間過圖。L4868 至 L4928 依本地吃藥選擇決定不吃或四種門檻。原共享鍵與本地變數可在逐筆資料回查。','',
                  'L4943 起反覆辨識畫面。L4960、L4964、L4968 各讀相應共享 ID 後送出 mode 1 工作控制。L1495 的副本辨識流程另有 mode 2 與 mode 1 要求。這些參數由模型保留為事件。','',
                  '四段吃藥先設定 X1、Y1、X2、Y2，再用其值找色。L6492 的範圍為 652、959、656、972。命中清零，連續三次未命中才發出鍵盤操作。L6504 的記錄文字提到 F1，L6506、6508、6510 實際傳入的鍵名為 `1`，模型依原參數保存。','',
                  '## 驗證範圍','',
                  f'{report["cases"]} 組固定副本案例對照 {report["external_events"]:,} 個事件、{report["shared_writes"]} 次共享寫入和 {report["records_covered"]} 筆不同指令。全部 15 個啟動位置及其工作入口都有案例。副本在 Windows VBScript 引擎執行原文，外掛建立接到記錄物件，工作啟動回傳合成 ID。每組在指定位置或步數結束擷取，實際並行、時間與工作生命週期仍待驗證。 [比對報告](../../verification/cube-workers-original-vs-rebuild.json)','',
                  'L853 的原跳轉可回缺失位置 L451。L856 跳 L1494，該位置屬另一段待銜接的保留控制流。模型保留這兩個邊界及其區別。'])
    (out/'魔方_工作協調.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


if __name__ == '__main__':
    main()
