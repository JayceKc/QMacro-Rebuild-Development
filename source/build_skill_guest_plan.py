from pathlib import Path
import csv,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
program=json.loads((ROOT/'outputs/QMacro-Rebuild-Development/programs/10.json').read_text(encoding='utf-8'))
code=program['code'];sl=program['strings'];rows=list(csv.DictReader((ROOT/'outputs/qmacro-readable-analysis/10-自動按技能/指令索引.csv').open(encoding='utf-8-sig')))
classes={}
key=bytes.fromhex('4d6a65757378756d')
for op,location,index,field in code:
    if op==29:break
    if op!=30:continue
    match=re.match(r'Class (\w+_V([0-9A-F]+)):',sl[index],re.I)
    if match:
        data=bytes.fromhex(match[2]);name=bytes(c^key[i%len(key)] for i,c in enumerate(data)).rstrip(b'\x00').decode('gb18030')
        classes[name]=match[1]
plan={'program_sha256':hashlib.sha256((ROOT/'outputs/QMacro-Rebuild-Development/programs/10.json').read_bytes()).hexdigest(),
      'orders':[{'entry':entry,'call_record':next(i for i,r in enumerate(code) if r[0]==12 and r[2]==entry),'expected_order':order}
                for entry,order in ((355,'QASWEDRF'),(506,'SFQDAERW'),(657,'WFRADQES'),(808,'RWFSADEQ'))],
      'controllers':[{'entry':entry,'loop':entry+4,'class_name':classes[name],'name':name,
                      'special_key':special,'counter_threshold':threshold}
                     for name,entry,special,threshold in (('使用Z技能',959,'Z',3),('不使用Z技能',1054,'',0),('更多Z技能',1136,'Z',1),('使用X技能',1231,'X',3))],
      'g_key':sl[code[427][2]],'g_delay_key':sl[code[435][2]],'speed_key':sl[code[966][2]],
      'classes':classes}
path=ROOT/'work/skill-vm-plan.json';path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'controllers':plan['controllers'],'classes':classes},ensure_ascii=True))
