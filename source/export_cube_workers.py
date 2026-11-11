"""Translate the retained cube worker coordinator and its called bodies."""
import hashlib
import json

from export_cube_routines import PROJECT, translate

WORKER_RANGES = (
    (717, 856, '保留入口尾段與普攻啟動'), (1495, 1675, '副本辨識與工作控制'),
    (3572, 3692, '找怪'), (3694, 3773, '中間過圖'),
    (3775, 3914, '技能組一'), (3916, 4055, '技能組二'),
    (4057, 4196, '技能組三'), (4198, 4337, '技能組四'),
    (4339, 4414, '使用Z技能'), (4416, 4479, '不使用Z技能'),
    (4481, 4556, '更多Z技能'), (4558, 4633, '使用X技能'),
    (4635, 5018, '戰鬥工作協調'),
    (6481, 6515, '吃藥11%'), (6517, 6551, '吃藥40%'),
    (6553, 6587, '吃藥70%'), (6589, 6623, '吃藥6%'),
    (6625, 6636, '不吃藥'), (6638, 6655, '普攻'), (6691, 6738, '不跟隨找怪'),
)
EXTERNAL_TARGETS = {451: 'missing_original_record', 1494: 'untranslated_continuation'}


def build(raw):
    plan = translate(raw, WORKER_RANGES, EXTERNAL_TARGETS)
    by = {a['record']: a for a in plan['actions']}
    workers = []
    for a in plan['actions']:
        if a['kind'] != 'worker_start':
            continue
        at, entry = a['record'], a['target']
        skip, setup, call, end, save = (by[i] for i in (at+1, entry, entry+1, entry+2, entry+3))
        slot_kind = 'assign_root_slot' if at == 717 else 'assign_slot'
        slot_expr = 'root_slot' if at == 717 else 'slot'
        if (skip['kind'], skip['target'], setup['kind'], call['kind'], end['kind'], save['kind'], save['value']) != (
            'jump', entry+3, 'frame_enter', 'call', 'iteration_end', slot_kind, {'temporary': True}):
            raise ValueError(('Unreviewed worker wrapper', at))
        store, temporary, write = (by[i] for i in (entry+4,entry+5,entry+6))
        if store['kind'] != slot_kind or store['value'] != {slot_expr:save['slot']} or temporary['kind'] != 'assign_temporary' or temporary['value'] != {slot_expr:store['slot']} or write['kind'] != 'write_global':
            raise ValueError(('Unreviewed worker ID data flow', at))
        workers.append(dict(start_record=at, worker_entry=entry, body_entry=call['target'],
                            worker_iteration_end=end['record'], parent_continue=save['record'],
                            parent_id_slot=save['slot'], parent_slot_scope=slot_expr,
                            shared_id_write=write['record'], shared_id_key=write['key']))
    if len(workers) != 15:
        raise ValueError('Worker entry inventory differs')
    for caller in plan['callers']:
        caller['return_pc'] = caller.pop('return_store_record')
        caller['return_opcode'] = raw['code'][caller['return_pc']][0]
    plan.update(name='魔方工作啟動與保留主體', worker_wrappers=workers, external_targets=EXTERNAL_TARGETS,
                full_module_restored=False, original_thread_timing_verified=False)
    return plan


def main():
    path = PROJECT/'programs/07.json'
    plan = build(json.loads(path.read_text('utf8')))
    plan['source_program_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (PROJECT/'data/cube-workers.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':len(plan['actions']), 'workers':len(plan['worker_wrappers'])}))


if __name__ == '__main__':
    main()
