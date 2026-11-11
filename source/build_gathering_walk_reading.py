from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT/'outputs/QMacro-Rebuild-Development';OUT=ROOT/'outputs/gathering-recovery'


def main():
    plan=json.loads((PROJECT/'data/gathering-walk.json').read_text(encoding='utf8'))
    comparison=json.loads((PROJECT/'verification/gathering-walk-original-vs-rebuild.json').read_text(encoding='utf8'))
    pretty=json.loads((ROOT/'outputs/qmacro-readable-analysis/08-挖礦採花/字串_閱讀對照.json').read_text(encoding='utf-8-sig'))
    code=json.loads((PROJECT/'programs/08.json').read_text(encoding='utf8'))['code']
    rows=[(742,'0≤角度≤10',[(1291,197),(1311,775),(1432,478)]),(758,'350<角度≤360',[(1291,197),(1311,775),(1432,478)]),
          (774,'10<角度≤80',[(997,56),(1426,488),(1348,169)]),(790,'80<角度≤100',[(542,273),(1350,281),(964,181)]),
          (806,'100<角度≤170',[(962,200),(562,491),(643,206)]),(822,'170<角度≤190',[(591,218),(595,791),(442,463)]),
          (838,'190<角度≤260',[(474,476),(921,870),(600,751)]),(854,'260<角度≤280',[(597,698),(1417,714),(1024,902)]),
          (870,'280<角度≤350',[(1518,470),(1068,850),(1531,729)])]
    lines=['# 採集：計算走位 L689..L888','',
           '這是採集模組五個保留主體中的一個，不是整套採集入口已恢復。前500缺失、G鍵工作、修理、活力與返回莊園仍要分別追查。','',
           '## 入口、變數與回傳','',
           '原呼叫點L547、L673均call L689，前一筆保留的框架建立可直接對應「計算走位」類別。',
           'INTXX/INTYY為找到的目標小地圖座標，XX1/YY1為中心；原SL初始化文字給XX1=1743、YY1=168、派=3.1415926。這些保留文字不等於初始化的缺失跳轉已還原。',
           '內部弧度與算角度的原變數仍在JSON；qmacro_gathering_walk.py用angle_name、pi_name對應，沒有偽稱英文名稱是原作者名稱。',
           '根據原L887，未賦值的類別回傳欄位為Empty，父框架恢復後L888返回。','',
           '## 條件與角度','',
           'L690檢查目標任一座標為0；L695檢查任一為負。成立時經原絕對跳轉L693/L698去L886，沒有送出走位；先前角度也沒有被清零。',
           '有效目標先各產生一個INT(15*RND-15)，因此X/Y微移範圍都是-15..-1，並非正負對稱。',
           'L706/710先處理同X的上方90度、下方270度。其餘L714算ATN((YY1-INTYY)/(XX1-INTXX))，L716依原近似派換成度，再依四象限與同Y左右軸校正。',
           '不可換用math.pi或atan2後宣稱原碼等同：角度邊界與錯誤行為可能變化。',
           '目標恰好是中心時，兩個同X軸條件皆不成立，L714為ATN(0/0)。副本實際回報VBScript scode=800a0006「溢位」，不是成功返回，也沒有滑鼠事件。若原角度原先為271，出錯後仍為271；原未賦值則仍Empty。','',
           '## 方向分區與三次右鍵','',
           '角度0為右、90上、180左、270下。每個下列固定點都加同一組負X/Y微移，再按右鍵一次；三個點各操作一次。',
           'MouseClick(2)的右鍵意義可回查Runner原庫RightClick包裝碼。它不是按下／放開兩個不同事件。','',
           '| 原條件記錄 | 角度區間 | 固定三點（未加微移） |','| --- | --- | --- |']
    lines += [f'| L{at} / SL{code[at][2]} | {interval} | '+ ' → '.join(f'({x},{y})' for x,y in points)+' |' for at,interval,points in rows]
    lines+=['','此主體本身沒有迴圈、執行緒啟動或介面回呼；原Call/Return與絕對Goto、相對If/Else跳轉仍在資料保留。','',
            '## 程式碼與原文核對','',
            'data/gathering-walk.json是全部200筆具名動作，qmacro_gathering_walk.py是封閉數值語法與事件狀態機；不使用eval/exec，也不送操作或實際等待。',
            '只支援這段已觀測的數值運算、ATN/INT/Sgn、比較及And/Or子集，不是完整VBScript替代品；原RNG結果須由外部明示供應，不能當成重現原隨機序列。',
            f'固定副本原文146例，{comparison["external_events"]}個外部事件、所有記錄路徑及角度一致；200個位置全部在案例聯集中走到。角度比較容差為絕對1e-10或相對1e-12，不偽稱逐位元浮點相同。',
            '測試含零／負座標、舊角度、中心重合、各軸和方向邊界附近的整數點，以及四組負微移端點。原Randomize/INT先正常執行，之後在L701/L704覆成控制值；原主體文字未改。',
            '目標、中心、派及模擬模式都是明示案例輸入；這不證明前500初始化或遊戲找圖、路線、實際時序已通過。DM和鼠標只由記錄物件接收，沒有載原插件或送遊戲操作。',
            '逐案證據：verification/original-gathering-walk.json、gathering-walk-owned.json、gathering-walk-original-vs-rebuild.json。','',
            '## 原記錄逐筆閱讀','', '```text']
    for a in plan['actions']:
        text=pretty[a['source_sl']]['readable'] if a['source_sl'] is not None else a['kind']+(' → L'+str(a['target']) if 'target' in a else '')
        lines.append(f'L{a["record"]} op{a["opcode"]} SL{a["source_sl"]}: {text}')
    lines+=['```','']
    OUT.mkdir(exist_ok=True);(OUT/'採集_計算走位.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (OUT/'gathering-walk-evidence.json').write_text(json.dumps({'entry':689,'last':888,'controlled_cases':146,'original_records_covered':200,
        'external_events':3150,'coincident_error_scode':'800a0006','source_program_sha256':plan['source_program_sha256'],
        'comparison_sha256':hashlib.sha256((PROJECT/'verification/gathering-walk-original-vs-rebuild.json').read_bytes()).hexdigest(),
        'full_module_restored':False},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'entry':689,'records':200,'controlled_cases':146,'full_module_restored':False}))


if __name__=='__main__':main()
