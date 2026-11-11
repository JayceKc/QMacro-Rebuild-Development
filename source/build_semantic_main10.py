"""Append an explicitly reconstructed main; never overwrite missing original IR.

Statements and dataflow come from retained SL. New branch locations are our
reconstruction, not a claim to recover the erased numerical operands.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/initialization-recovery'
BASE=ROOT/'outputs/QMacro-Rebuild-Development/programs/10.json'
p=json.loads(BASE.read_text(encoding='utf-8'));base_count=len(p['code']);code=p['code'];sl=p['strings']
pretty=json.loads((ROOT/'outputs/qmacro-readable-analysis/10-自動按技能/字串_閱讀對照.json').read_text(encoding='utf-8-sig'))
rows=[]


def emit(op,operand=0,source=None,why='retained SL statement'):
    pc=len(code);code.append([op,0,operand,0]);rows.append({'record':pc,'op':op,'operand':operand,'source_sl':source,'basis':why});return pc
def text(i):return emit(30 if pretty[i]['kind']=='decoded-text' else 2,i,i)
def read(i,copy):emit(37,i,i);text(copy)
def put(temp,name,rhs):text(rhs);text(temp);emit(28,name,name)
def false(i):emit(4,i,i);return emit(6,0,i,'branch synthesized from retained Sgn and source dataflow')
def jump():return emit(16,0,None,'new structured control edge; original numerical operand erased')
def target(pc,end):
    code[pc][2]=end-pc
    next(r for r in rows if r['record']==pc)['operand']=end-pc
def begin(i):return false(i)
def finish(pc):target(pc,len(code))
def checkbox(prop,copy,condition,true_set,false_set):
    read(prop,copy);branch=begin(condition);put(*true_set);end=jump();finish(branch);put(*false_set);finish(end)


entry=len(code)
text(42)  # original Array(0..10)
read(44,45);text(46)
read(48,49);text(50)
read(52,53);put(54,55,56)
read(69,70);put(71,72,73)
read(75,76);outer=begin(77);exits=[]
for i in range(9):
    get=78+6*i;emit(27,get,get);text(get+1);branch=begin(get+2)
    put(get+3,get+4,get+5);exits.append(jump());finish(branch)
outer_end=jump();finish(outer);put(132,133,134);finish(outer_end)
for exit in exits:finish(exit)
text(135)
checkbox(136,137,138,(139,140,141),(142,143,144));text(145)
checkbox(146,147,148,(149,150,151),(152,153,154));text(155)
read(156,157);branch=begin(158);text(159);end=jump();finish(branch);text(160);finish(end)
config_end=len(code)
for i in (161,162,163,164):text(i)
worker_sites=[]


def spawn(frame,result,temp,name,rhs,callee,confidence):
    start=emit(24,2,frame,'reconstructed BeginThread template, matching retained worker sites')
    skip=jump();emit(2,frame,frame);emit(12,callee,frame,confidence);emit(23,0,None,'worker wrapper end')
    finish(skip);text(result);put(temp,name,rhs)
    worker_sites.append({'start_record':start,'wrapper_entry':start+2,'callee':callee,'frame_sl':frame,
                         'id_global_sl':name,'entry_mapping_status':confidence})


for i,callee in enumerate((959,1054,1136,1231)):
    k=165+9*i;branch=begin(k);text(k+1);text(k+2)
    spawn(k+3,k+4,k+5,k+6,k+7,callee,'controller identity supported by trace text and isolated original-body replay')
    text(k+8);finish(branch)
text(201)
for i,callee in enumerate((1538,1326,1379,1432,1485)):
    k=202+9*i;branch=begin(k);text(k+1);text(k+2)
    spawn(k+3,k+4,k+5,k+6,k+7,callee,'inferred identity: health-bar coordinates/body behavior; erased call operand not recovered')
    text(k+8);finish(branch)
text(247);branch=begin(248);text(249);text(250)
spawn(251,252,253,254,255,1551,'inferred identity from retained death-monitor body and trace')
text(256);finish(branch);text(257)
idle=len(code);branch=begin(258)
for i in range(259,265):text(i)
back=jump();target(back,idle);finish(branch);emit(23)
assert p['code'][:base_count]==json.loads(BASE.read_text(encoding='utf-8'))['code']
p['name']='自動按技能／明示重建初始化'
p.update({'base_program_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),
 'original_record_prefix_count':base_count,'original_record_prefix_unchanged':True,
 'reconstructed_entry':entry,'reconstructed_config_end':config_end,'reconstructed_idle_entry':idle,
 'reconstruction_source_map':rows,'reconstructed_worker_sites':worker_sites,
 'derivation_limits':['Original 329 missing records remain missing and unchanged.',
  'New main is semantically reconstructed; original conditional jump numbers were not recovered.',
  'Legacy DLL extraction/registration/version bootstrap SL16..41 intentionally replaced by owned backend initialization.',
  'MMVerifyCode/TianXuan SL58..61 remains unresolved; no fabricated color is supplied.',
  'Health-body/class identity mappings remain inference; new SDK readiness and live backend still required.'],
 'full_program_restored':False})
OUT.mkdir(exist_ok=True)
path=OUT/'10-semantic-main.json';path.write_text(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
lines=['# 自動按技能：明示重建的初始化入口','',
 '原有 1,644 筆指令不變，329 筆缺失仍保留；以下新增入口不是原始跳轉數字的復原。',
 '語句直接使用原 SL；分支及工作流程包裝依保留資料流與其他完整指令模板重建。','',
 f'新入口 L{entry}；設定結束 L{config_end}；主流程等待迴圈 L{idle}。','',
 '舊 DLL 註冊/SDK 初始化不會自動執行。MMVerifyCode 未解，不填入假色碼。','',
 '## 資料流','',
 'ComboBox1.ListIndex → 吃藥模式；ComboBox2.ListIndex → 技能釋放模式；ComboBox3.ListIndex → 共享按鍵速度。',
 'InputBox1.Text → 共享 GMS；CheckBox4.Value 與 GMS=1..9 控制共享「按G嗎」。',
 'CheckBox1/2.Value → 共享 F1/1 吃藥旗標；CheckBox3.Value → 復活選擇。',
 '選定技能工作流程、吃藥工作流程與可選死亡監控；ID 寫回原共享變數名稱。','',
 '## 新入口逐筆來源','', '| 新記錄 | 操作 | 原 SL | 保留文字／重建依據 |','| --- | --- | --- | --- |']
for r in rows:
    source=r['source_sl'];description=pretty[source]['readable'] if source is not None else r['basis']
    lines.append(f'| L{r["record"]} | {r["op"]} / {r["operand"]} | {source if source is not None else "—"} | {description.replace(chr(10)," ").replace("|","／")} |')
(OUT/'10-重建初始化.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'entry':entry,'config_end':config_end,'idle':idle,'new_records':len(rows),'total_records':len(code),
 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_missing_records_unchanged':len(p['missing_records'])}))
