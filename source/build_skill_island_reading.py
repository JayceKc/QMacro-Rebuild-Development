"""Render the 09/10 retained record maps and source-backed entry notes."""
from build_shared_battle_reading import describe
from replay_shared_battle import PROJECT,load


def main():
    host = load('verification/skill-island-host-original-vs-rebuild.json')
    for module,title in (('09','渴望島'),('10','自動按技能')):
        plan = load(f'data/skill-island-retained-{module}.json')
        report = load(f'verification/skill-island-{module}-original-vs-rebuild.json')
        out = PROJECT/'analysis'/('island' if module=='09' else 'skill')
        out.mkdir(exist_ok=True,parents=True)
        index = f'{module}-全部保留記錄偽碼.txt'
        actions = {a['record']:a for a in plan['actions']}
        entries = {r['entry']:r['name'] for r in plan['routines']}
        rows = [f'# {title}的原始記錄索引','']
        for at in range(plan['total_records']):
            if at in entries:
                rows.extend(['',f'## {entries[at]} L{at}',''])
            if at not in actions:
                rows.append(f'L{at} 原記錄缺失')
                continue
            a = actions[at]
            rows.append(f'L{at} {describe(a)}  // op={a["opcode"]}, loc={a["location"]}, SL={a["source_sl"]}, field_3={a["field_3"]}')
        (out/index).write_text('\n'.join(rows)+'\n',encoding='utf8')
        guide = [
            f'# {title}的保留記錄與介面','',
            f'索引收錄 {len(actions):,} 筆可讀記錄，並標示 {len(plan["boundaries"])} 筆缺失位置。原入口由 L0 執行宣告及派送後停在 L{host["default_boundaries"][module]}。子程序名稱依原記錄文字及流程推定。','',
            f'{report["cases"]} 組子程序副本案例核對 {report["external_events"]:,} 個事件，觀測 {report["records_covered"]:,} 筆原記錄。另三組 Form1 案例核對等待、關閉及原結束跳轉。','',
            '| 子程序 | 入口 | 返回 |','| --- | --- | --- |'
        ]
        guide.extend(f'| {r["name"]} | L{r["entry"]} | L{r["last"]} |' for r in plan['routines'])
        if module=='09':
            guide += ['', '第一次戰鬥先查金色目標與血條，再依模式選擇技能工作。技能與找怪是獨立的工作入口，以下均保留原父流程接續和 ID 存放方式。','',
                      '| 啟動 | 工作入口 | 主體 | 父流程接續 | ID 變數 |','| --- | --- | --- | --- | --- |']
            guide.extend(f'| L{w["start_record"]} | L{w["worker_entry"]} | L{w["body_entry"]} | L{w["parent_continue"]} | `{w["local_id_name"]}` |'
                         for w in plan['worker_wrappers'])
        else:
            guide += ['', '死亡與復活在 L1603 讀取 Runner 游標，兩個座標分別回寫 MX、MY。副本核對了 (314,256) 與 (1820,950)，並比較後續移動參數。','',
                      'CHANGE.FORM1.INPUTBOX1 位於 L66–L73。L67 取文字，L69 取最右一個 UTF-16 單位，L71 寫回文字，L73 返回 L1641。原副本的兩個案例結果是 123 → 3、45 → 5。']
        guide += ['', '保留流程和推定初始化分開交付。測試使用明示畫面觀測、工作 ID 和游標值，實際 SDK、並行與完整入口仍待驗證。','',
                  f'[逐筆索引]({index}) [原文路徑比對](../../verification/skill-island-{module}-original-vs-rebuild.json) [介面比對](../../verification/skill-island-host-original-vs-rebuild.json)']
        (out/'保留記錄與介面.md').write_text('\n'.join(guide)+'\n',encoding='utf8')


if __name__=='__main__':
    main()
