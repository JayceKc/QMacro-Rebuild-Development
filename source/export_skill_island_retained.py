"""Translate preserved 09 and 10 records while keeping inferred entries separate."""
import hashlib
import json
import re

from export_battle_recovery import CANDIDATES
from export_battle_retained import host_action
from export_cube_routines import ARRAY, FRAME, PROJECT, translate


NAMES = {
    '09': ('找怪輪詢','隨機技能一','隨機技能二','隨機技能三','隨機技能四',
           '使用Z','不使用Z','更多Z','第四技能模式','第一次戰鬥'),
    '10': ('隨機技能一','隨機技能二','隨機技能三','隨機技能四','使用Z','不使用Z','更多Z','使用X',
           '吃藥門檻一','吃藥門檻二','吃藥門檻三','吃藥門檻四','技能操作','死亡與復活'),
}


def routine_ranges(module, raw):
    code = raw['code']
    missing = set(raw['missing_records'])
    pairs = [(at+1,at+arg-1) for at,(op,_,arg,_) in enumerate(code)
             if at not in missing and op==16 and arg>0 and at+arg<len(code) and code[at+arg-1][0]==13]
    if len(pairs)!=len(NAMES[module]):
        raise ValueError(('Unexpected retained routine count',module,pairs))
    return [(first,last,name) for (first,last),name in zip(pairs,NAMES[module])]


def seed(raw, at, kind):
    op,loc,operand,flags = raw['code'][at]
    source = raw['strings'][operand] if op in (2,30,33,35,37,38) else None
    return dict(record=at,opcode=op,location=loc,operand=operand,field_3=flags,kind=kind,
                source=source,source_sl=operand if source is not None else None)


def translate_extra(raw, at):
    op = raw['code'][at][0]
    row = seed(raw,at,'host')
    source = row['source']
    if op==30 and source=='Call GetCursorPos(MX,MY)':
        return dict(row,kind='builtin_cursor',out_names=['MX','MY'])
    if at in (66,72,73):
        return host_action(dict(row,kind='form_callback'))
    if op in (37,38) and source=='Form1.InputBox1.Text':
        return dict(row,kind='ui_read' if op==37 else 'ui_write',path=source)
    if at==69 and source==f'{FRAME}.{ARRAY}(2)=RIGHT({FRAME}.{ARRAY}(1),1)':
        return dict(row,kind='assign_right_text',slot=2,input_slot=1,count=1)
    raise ValueError(('Unreviewed skill host operation',at,op,source))


def build(module, raw):
    code = raw['code']
    missing = set(raw['missing_records'])
    ranges = routine_ranges(module,raw)
    actions = {}
    for first,last,name in ranges:
        spans = ((first,1602),(1604,last)) if module=='10' and first==1551 else ((first,last),)
        for start,end in spans:
            body = translate(raw,((start,end,name),),range(len(code)))
            actions.update((a['record'],a) for a in body['actions'])
    if module=='10':
        for at in (66,67,69,71,72,73,1603):
            actions[at] = translate_extra(raw,at)
        body = translate(raw,((68,68,'回呼存值'),(70,70,'回呼寫值')),range(len(code)))
        actions.update((a['record'],a) for a in body['actions'])
    header = next(i for i,row in enumerate(code) if row[0]==29)
    for at in range(len(code)):
        if at in missing or at in actions:
            continue
        op,_,arg,_ = code[at]
        row = seed(raw,at,'declaration_or_dispatch' if at<=header else 'host')
        if op==16:
            row['target'] = at+arg
        action = host_action(row)
        actions[at] = action
    workers = []
    for worker in raw['worker_starts']:
        at,entry = worker['record'],worker['entry']
        skip,setup,call,end,store,keep = (actions[i] for i in (at+1,entry,entry+1,entry+2,entry+3,entry+4))
        actual = (skip['kind'],skip['target'],setup['kind'],call['kind'],end['kind'],store['kind'],store['value'],keep['kind'],keep['value'])
        expected = ('jump',entry+3,'frame_enter','call','iteration_end','assign_slot',{'temporary':True},'assign',{'slot':store['slot']})
        if actual!=expected:
            raise ValueError(('Unreviewed worker shape',module,at))
        workers.append(dict(start_record=at,worker_entry=entry,body_entry=call['target'],
                            parent_continue=store['record'],parent_slot=store['slot'],local_id_name=keep['name']))
    for a in actions.values():
        if 'target' in a and a['target'] not in actions and a['target'] not in missing:
            raise ValueError(('Unreviewed retained target',module,a['record'],a['target']))
    assert set(actions)==set(range(len(code)))-missing
    routine_domain = {at for start,end,_ in ranges for at in range(start,end+1)}
    host = sorted(set(actions)-routine_domain)
    return dict(module=int(module),total_records=len(code),actions=[actions[i] for i in sorted(actions)],
                routines=[dict(entry=start,last=end,name=name) for start,end,name in ranges],host_records=host,
                boundaries=dict.fromkeys(sorted(missing),'missing_original_record'),worker_wrappers=workers,
                form_gate=next(a['record'] for a in actions.values() if a['kind']=='runner_message'),
                callbacks=raw['callbacks'],full_module_restored=False)


def main():
    for module in NAMES:
        source = (PROJECT/f'programs/{module}.json').read_bytes()
        plan = build(module,json.loads(source))
        plan['source_program_sha256'] = hashlib.sha256(source).hexdigest()
        (CANDIDATES/f'skill-island-retained-{module}.json').write_text(
            json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,len(plan['actions']),len(plan['boundaries']),len(plan['worker_wrappers']))


if __name__=='__main__':
    main()
