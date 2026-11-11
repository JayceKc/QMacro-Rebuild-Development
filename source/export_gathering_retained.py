"""Index all 08 records across the main context, G worker, and Form1 host."""
import hashlib
import json

from export_cube_routines import PROJECT


HOST = {**dict.fromkeys(range(6),'declaration'),6:'entry_dispatch',
        1622:'runner_message',1623:'ui_pump',1624:'iteration_end'}


def build(raw, main, worker):
    code = raw['code']
    missing = set(raw['missing_records'])
    actions = {}
    for context, plan in (('main',main),('g_worker',worker)):
        for a in plan['actions']:
            at = a['record']
            if at in actions:
                raise ValueError(('Overlapping gathering contexts',at))
            actions[at] = dict(a,context=context)
    for at,kind in HOST.items():
        op,loc,operand,field = code[at]
        expected = {'declaration':30,'entry_dispatch':29,'runner_message':33,'ui_pump':35,'iteration_end':23}
        if op!=expected[kind] or at in actions:
            raise ValueError(('Unknown gathering host record',at,op))
        source = raw['strings'][operand] if op in (30,33,35) else None
        actions[at] = dict(record=at,opcode=op,location=loc,source_sl=operand if source is not None else None,
                           source=source,kind=kind,context='host')
    if set(actions)!=set(range(len(code)))-missing:
        raise ValueError('Gathering retained coverage differs')
    for at,a in actions.items():
        op,loc,operand,flags = code[at]
        if a['opcode']!=op or a['location']!=loc:
            raise ValueError(('Original gathering provenance differs',at))
        if a['source_sl'] is not None and (a['source_sl']!=operand or a['source']!=raw['strings'][operand]):
            raise ValueError(('Original gathering text differs',at))
        a.update(operand=operand,field_3=flags)
    if raw['callbacks'] or raw['worker_starts']:
        raise ValueError('Gathering callback or worker metadata changed')
    return dict(module=8,actions=[actions[at] for at in sorted(actions)],missing_records=sorted(missing),
                total_records=len(code),retained_records=len(actions),host_records=sorted(HOST),
                form_gate=1622,form_entry=1621,program_end=1625,root_entries=main['root_entries'],
                worker_entry=worker['entry'],full_module_restored=False)


def main():
    source = PROJECT/'programs/08.json'
    main_path = PROJECT/'data/gathering-main-suffix.json'
    worker_path = PROJECT/'data/gathering-worker.json'
    raw,main,worker = (json.loads(p.read_text('utf8')) for p in (source,main_path,worker_path))
    digest = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    plan = build(raw,main,worker)
    plan.update(source_program_sha256=digest(source),main_plan_sha256=digest(main_path),worker_plan_sha256=digest(worker_path))
    assert plan['source_program_sha256']==main['source_program_sha256']==worker['source_program_sha256']
    (PROJECT/'data/gathering-retained.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(plan['retained_records'],len(plan['missing_records']))


if __name__=='__main__':
    main()
