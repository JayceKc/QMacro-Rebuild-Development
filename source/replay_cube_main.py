"""Build explicit fixtures and replay the linked model without native effects."""
import copy
import json

from export_cube_routines import PROJECT
from qmacro_cube_main import CubeMainMachine


def load(name):
    return json.loads((PROJECT / name).read_text(encoding='utf8'))


def scalar_names(node):
    if isinstance(node, dict):
        if set(node) == {'name'} and not node['name'].startswith('CUBE_SLOT_'):
            yield node['name']
        for value in node.values():
            yield from scalar_names(value)
    elif isinstance(node, list):
        for value in node:
            yield from scalar_names(value)


def build_cases(plan):
    cases = []
    first = 'VF0ADACDECCD2BFD14D6A65757378756D'
    switch = 'V89BBD3BD7378756D'
    completion = 'V8080D6BCA5D6CF9E4D6A65757378756D'
    weekly = 'VF4C1DE94BBB6BB9C4D6A65757378756D'

    def add(label, misses=(), stop_after=None, limit=900, overrides=None, upper=False, inverted=False):
        shared = {a['key']: 0 for a in plan['actions'] if a['kind'] in ('read_global', 'write_global')}
        shared.update({first: 1, 'VF0ADACDECE99BF954D6A65757378756D': 24,
                       'V9FC0A2A5CEBFBCC64D6A65757378756D': 1,
                       'V9BBAD991CA85B8D1042E65757378756D': 4567, 'V8186B4D47378756D': '123456'})
        shared.update(overrides or {})
        cases.append(dict(id=len(cases)+1, label=label, shared=shared,
                          values={name: 0 for name in sorted(set(scalar_names(plan['actions'])))},
                          frame_slots={'5': 777, '255': 913}, miss_budget={str(x): -1 for x in (*misses, 5153)},
                          default_found=True, inverted_return=inverted, random_upper=upper,
                          max_body_steps=limit, stop_after=stop_after))

    add('nested-altq-return', stop_after=2242)
    for at in (3370, 6658, 6665, 6670):
        add(f'nested-observation-miss-{at}', misses=(at,), stop_after=2242)
    for character in (1, 10, 24):
        add(f'character-{character}-then-weekly', misses=(1743,), stop_after=2169,
            overrides={switch: 1, weekly: 1, 'V9FC0A2A5CEBFBCC64D6A65757378756D': character}, upper=True)
    for mode in (0, 1, 2, 3, 4):
        add(f'completion-mode-{mode}', misses=(1743,), overrides={first: 0, switch: 1, completion: mode})
    add('ui-normal', misses=(1694,), stop_after=2363)
    add('ui-other-mode', misses=(1694,), stop_after=2705, overrides={'V87ADD284A491C3BE4D6A65757378756D': 2})
    add('ui-other-mode-fallback', misses=(1694, 2676), stop_after=3014,
        overrides={'V87ADD284A491C3BE4D6A65757378756D': 2, 'V80C2DCADC7B6BF904D6A65757378756D': 19})
    add('sdk-miss-repeat', misses=(1690,), limit=150)
    for at in (1699, 1704, 1709, 1720, 1726, 2154, 2340, 2344, 2658, 2662):
        add(f'parent-observation-miss-{at}', misses=(at,), limit=500, overrides={weekly: 1}, inverted=True)
    add('retry-altq-key-down-up', misses=(3380,), stop_after=2242)
    add('retry-altq-both-buttons-missing', misses=(3380, 3428), stop_after=2242)
    add('alternate-button-parent', misses=(2236,), stop_after=2251)
    add('alternate-parent-retries-altq', misses=(2236,3380), stop_after=2251)
    return cases


def replay(plan, child, spec):
    shared = copy.deepcopy(spec['shared'])
    machine = CubeMainMachine(plan, child, lambda key, at: shared[key], spec['values'],
                              {int(k): v for k, v in spec['frame_slots'].items()})
    records, events, accesses, restores = [], [], [], []
    query_counts = {}
    for _ in range(spec['max_body_steps']):
        if machine.done:
            break
        event = machine.step()
        at, kind = event['record'], event['kind']
        records.append(at)
        events.append(event)
        if kind == 'write_global':
            shared[event['key']] = event['value']
        if kind in ('read_global', 'write_global'):
            accesses.append(event)
        if kind == 'dm_real_mouse_intent':
            machine.supply_dm_return(1)
        if kind in ('find_pic', 'find_color'):
            query_counts[at] = query_counts.get(at, 0) + 1
            budget = spec['miss_budget'].get(str(at))
            found = spec['default_found'] if budget is None else budget >= 0 and query_counts[at] > budget
            x, y = (event['rect'][0]+1, event['rect'][1]+2) if found else (-1,-1)
            ret = (1 if found else 0) if kind == 'find_color' else (0 if found else -1)
            if spec['inverted_return']:
                ret = 1 if ret == 0 else 0
            machine.supply_query(x, y, ret)
            events.append(dict(kind='query_reply', record=at, x=x, y=y, return_value=ret))
        if kind == 'random_int':
            machine.supply_random(event['lower'] + (event['span']-1 if spec['random_upper'] else 0))
        if kind == 'frame_restore_intent':
            restores.append(dict(record=at, depth=event['depth'], return_empty=event['value'] is None))
        if at == spec['stop_after']:
            break
    return dict(id=spec['id'], records=records, reason=machine.reason or 'fixture_stop', next_record=machine.pc,
                shared_accesses=accesses, final_shared=shared, events=events, restores=restores,
                root_slots={str(i): machine.frames[0]['slots'].get(i) for i in (5,47,54,55,255)},
                frame_depth=len(machine.frames))


def main():
    plan, child = load('data/cube-main.json'), load('data/cube-routines.json')
    specs = build_cases(plan)
    path = PROJECT / 'data/cube-main-cases.json'
    path.write_text(json.dumps({'cases': specs, 'synthetic_prefix_values': True}, indent=2)+'\n', encoding='utf8')
    results = [replay(plan, child, spec) for spec in specs]
    print(json.dumps({'cases': len(results), 'steps': sum(len(r['records']) for r in results),
                      'ui_records': sorted({e['record'] for r in results for e in r['events'] if e['kind']=='ui_write'}),
                      'restores': sum(len(r['restores']) for r in results)}))


if __name__ == '__main__':
    main()
