"""Reconstruct module09 source dataflow, preserving its erased prefix verbatim.

All 92 SL entries cover exactly 104 original source-location slots under the
known templates. Relative branch operands remain explicitly inferred.
"""
from pathlib import Path
import collections,hashlib,json
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT/'outputs/QMacro-Rebuild-Development';OUT=ROOT/'outputs/initialization-recovery'
BASE=PROJECT/'programs/09.json';p=json.loads(BASE.read_text(encoding='utf-8'));original=json.loads(BASE.read_text(encoding='utf-8'))
pretty=json.loads((ROOT/'outputs/qmacro-readable-analysis/09-渴望島/字串_閱讀對照.json').read_text(encoding='utf-8-sig'))
base=len(p['code']);code=p['code'];rows=[];reference=12
def emit(op,sl=None,operand=None,basis='retained source; owned text opcode, original 2/30 choice not recovered'):
    global reference
    slot=reference;assert slot in original['missing_records'];reference+=1
    assert slot<=115
    location=original['code'][slot][1];at=len(code);value=sl if sl is not None else operand if operand is not None else 0
    code.append([op,location,value,0]);rows.append({'record':at,'reference_slot':slot,'op':op,'source_sl':sl,'location':location,'basis':basis});return at
def text(sl):return emit(30 if pretty[sl]['kind']=='decoded-text' else 2,sl,basis='text opcode inferred from retained SL encoding; all28022 preserved text records agree')
def branch(sl):
    emit(4,sl,basis='retained Sgn condition');return emit(6,operand=0,basis='inferred structured conditional target')
def jump():return emit(16,operand=0,basis='inferred structured skip, loop-back or break')
def target(pc,reference_slot):code[pc][2]=base+reference_slot-12-pc

for sl in range(11,25):text(sl)
version=branch(25);text(26);version_skip=jump();text(27);target(version,30);target(version_skip,31)
for sl in range(28,34):text(sl)
emit(37,34,basis='UI property read template');text(35);text(36)
for sl in range(37,52):text(sl)
emit(2,52,basis='retained call-frame creation; sole remaining class/body pairing inferred by elimination')
emit(12,operand=936,basis='inferred first-battle entry936, original call operand absent');text(53)
text(54);text(55);text(56);outer=branch(57);text(58);text(59);gold=branch(60)
text(61);text(62);text(63);text(64);health=branch(65)
for sl in range(66,75):text(sl)
inner=branch(75);text(76);text(77);elite=branch(78);text(79);elite_skip=jump()
for sl in range(80,87):text(sl)
# UI setter allocates RHS after the LHS helper in the SL pool, but executes RHS first.
text(89);text(87);emit(38,88,basis='UI setter template: SL89 RHS, SL87 temp, SL88 Text write; not a numeric comparison')
for sl in range(90,100):text(sl)
leave=jump();text(100);inner_back=jump();text(101);outer_back=jump();text(102)
assert reference==116 and len(rows)==104
assert collections.Counter(r['source_sl'] for r in rows if r['source_sl'] is not None)==collections.Counter(range(11,103))
target(outer,115);target(gold,114);target(health,114);target(inner,113);target(elite,90);target(elite_skip,112);target(leave,113);target(inner_back,82);target(outer_back,61)
# Owned terminal marker replaces falling through all original routine-skip nodes.
end=len(code);code.append([22,0,0,0])
entry=base+35-12
assert code[:base]==original['code'] and p['missing_records']==original['missing_records']
p.update(name='渴望島／明示重建入口',original_record_prefix_count=base,original_record_prefix_unchanged=True,
         base_program_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),reconstructed_entry=entry,
         reconstructed_outer_loop=base+61-12,reconstructed_inner_loop=base+82-12,reconstructed_end=end,
         reconstruction_source_map=rows,
         inferred_branch_alternatives=[{'reference_slot':66,'default_target':114,'alternative_target':70,
          'default_reason':'Gold and HP nested as in preserved first-battle routine; closing structure inferred, not recovered.',
          'alternative_reason':'If Gold branch closes before HP query, its false path goes to HP query instead.'},
          {'reference_slot':72,'default_target':114,'alternative_target':113,
           'default_reason':'HP body includes post-inner-loop delay; original closing target absent.'}],
         legacy_bootstrap_reference_slots=[12,34],
         derivation_limits=['Original104 erased records are unchanged and not recovered.',
           '104-slot/source coverage does not prove inferred branch operands; text2/30 selection uses the retained encoding contract, not recovered record bytes.',
           'Default entry skips legacy regsvr32, DLL extraction/registration, version check and native mouse configuration; an owned backend must be supplied.',
           'First-battle worker creation is tested with recording-only worker starts, not full real-time scheduling.',
           'Appended terminal is an owned lifecycle boundary; the separate original UI pump is not instantiated here.'],
         full_program_restored=False)
OUT.mkdir(exist_ok=True);file=OUT/'09-semantic-main.json';file.write_text(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
lines=['# 渴望島：104 個缺失位置的語義重建','',
       '原1038筆指令及104筆缺失標記不變。以下新增104筆有來源的重建指令，另加一個自有終止標記。',
       '92條保留SL各使用一次，條件／Else／Loop／Break／Call模板完整覆蓋104個原位置；這不是原記錄與跳轉數字的解密。',
       '文字2/30操作依SL編碼推定；已核對八組28022筆保留文字記錄，沒有不符。',
       f'預設新入口 L{entry}；外迴圈 L{p["reconstructed_outer_loop"]}；內迴圈 L{p["reconstructed_inner_loop"]}。','',
       '## 推定與替代','',
       '原來的註冊及版本初始化保留為資料，但預設入口略過。DM必須由明確的自有後端提供。',
       '第一次戰鬥映到L936，是由唯一剩餘類別／主體及行為推定；原主體24個受控案例已在副本通過。',
       '金色與血條判定預設為巢狀，與保留的第一次戰鬥相同；金色條件也可能在血條查詢前結束。',
       '原slot66、slot72的替代目標保留在JSON，必須以其他證據繼續核對，不把候選誤稱原跳轉。',
       'InputBox2依編譯模板寫入擊殺計數；SL分配次序87/88/89，執行次序89/87/38(88)。','',
       '## 原位置與新指令','', '| 新記錄 | 原缺失位置 | 原位置ID | 操作 | SL | 可讀語句 |','| --- | --- | --- | --- | --- | --- |']
for r in rows:
    readable=pretty[r['source_sl']]['readable'] if r['source_sl'] is not None else r['basis']
    lines.append(f'| L{r["record"]} | L{r["reference_slot"]} | {r["location"]} | {r["op"]} | {r["source_sl"] if r["source_sl"] is not None else "推定控制"} | {readable.replace(chr(10)," ").replace("|","／")} |')
(OUT/'09-重建初始化.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'source_slots':len(rows),'source_strings':92,'entry':entry,'outer':p['reconstructed_outer_loop'],'inner':p['reconstructed_inner_loop'],'original_missing_unchanged':104,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}))
if __name__=='__main__':pass
