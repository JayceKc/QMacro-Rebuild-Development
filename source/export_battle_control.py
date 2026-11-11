"""Retain the linked coordinator, worker wrappers, and movement families."""
import hashlib
import json

from export_cube_routines import PROJECT,translate

RANGES = {
    '01': ((1591,1689,'開始打怪'),(1691,1738,'停止打怪'),(7706,7877,'走位'),(7879,8042,'塔內走位'),
           (8044,8320,'找怪'),(8322,8661,'工作選擇'),(11586,11698,'紫門拾取'),(12617,13349,'圖四找怪'),(13351,13567,'402跳躍')),
    '03': ((839,877,'開始打怪'),(879,900,'停止打怪'),(2746,2843,'找怪'),(2845,3082,'工作選擇')),
    '06': ((1443,1537,'開始打怪'),(1539,1588,'停止打怪'),(7543,7714,'走位'),(7716,7879,'塔內走位'),
           (7881,8157,'找怪'),(8159,8481,'工作選擇'),(8483,8597,'紫門拾取'),(9228,9960,'圖四找怪'),(9962,10178,'402跳躍')),
}


def build(module,raw,base,additional_ranges=()):
    ranges = RANGES[module]+tuple(additional_ranges)
    plan = translate(raw,ranges,range(len(raw['code'])))
    actions = {a['record']:a for a in plan['actions']}
    combined = set(actions)|{a['record'] for a in base['actions']}
    if len(combined)!=len(actions)+len(base['actions']):
        raise ValueError('Overlapping battle plans')
    boundaries = {}
    workers = []
    for a in actions.values():
        at,kind = a['record'],a['kind']
        target = a.get('target')
        if target is not None and target not in combined:
            if kind!='call' or target in raw['missing_records']:
                raise ValueError(('Unexpected control boundary',a))
            boundaries[target]='untranslated_call'
        if kind!='worker_start':
            continue
        skip, setup, call, end, store = (actions[i] for i in (at+1,target,target+1,target+2,target+3))
        if (skip['kind'],skip['target'],setup['kind'],call['kind'],end['kind'],store['kind'],store['value']) != (
            'jump',target+3,'frame_enter','call','iteration_end','assign_slot',{'temporary':True}):
            raise ValueError(('Unreviewed worker wrapper',at))
        continuation = actions[target+4]
        shared_key = None
        local_name = None
        if continuation['kind']=='assign_slot':
            temp, write = actions[target+5],actions[target+6]
            if continuation['value']!={'slot':store['slot']} or temp['kind']!='assign_temporary' or temp['value']!={'slot':continuation['slot']} or write['kind']!='write_global':
                raise ValueError(('Unreviewed worker ID writeback',at))
            shared_key=write['key']
        elif continuation['kind']=='assign' and continuation['value']=={'slot':store['slot']}:
            local_name=continuation['name']
        else:
            raise ValueError(('Unreviewed worker ID continuation',at))
        workers.append(dict(start_record=at,worker_entry=target,body_entry=call['target'],body_translated=call['target'] in combined,
                            parent_continue=store['record'],parent_slot=store['slot'],shared_id_key=shared_key,local_id_name=local_name))
    plan.update(module=int(module),name='戰鬥啟停、工作選擇與找怪走位',worker_wrappers=workers,boundaries=boundaries,
                original_worker_timing_verified=False,full_module_restored=False)
    return plan


def main():
    for module in RANGES:
        source = PROJECT/f'programs/{module}.json'
        base = PROJECT/f'data/battle-{module}.json'
        plan = build(module,json.loads(source.read_text('utf8')),json.loads(base.read_text('utf8')))
        plan['source_program_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
        plan['base_plan_sha256']=hashlib.sha256(base.read_bytes()).hexdigest()
        (PROJECT/f'data/battle-control-{module}.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'module':module,'new_records':len(plan['actions']),'workers':len(plan['worker_wrappers']),'untranslated_targets':sorted(plan['boundaries'])}))


if __name__ == '__main__':
    main()
