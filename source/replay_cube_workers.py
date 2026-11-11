"""Deterministic fixtures for the cube coordinator and isolated worker bodies."""
import json

from replay_cube_main import PROJECT, load, scalar_names
from qmacro_cube_workers import CubeWorkerMachine

MODE = 'V87ADD284A491C3BE4D6A65757378756D'
SKILL = 'VF1D6A1A9B9B5C2A84D6A65757378756D'
POTION = 'VFEBEB7DC7378756D'


def build_cases(plan):
    cases = []

    def add(label, entry, *, mode=0, skill=0, potion=0, misses=(), limit=250, stop_after=None):
        shared = {a['key']: 0 for a in plan['actions'] if a['kind'] in ('read_global','write_global')}
        shared.update({MODE:mode, 'V8186B4D47378756D':'123456'})
        values = {n:0 for n in sorted(set(scalar_names(plan['actions']))) if not n.startswith('CUBE_ROOT_SLOT_')}
        values.update({SKILL:skill, POTION:potion})
        cases.append(dict(id=len(cases)+1,label=label,entry=entry,shared=shared,values=values,
                          frame_slots={},root_slots={},miss_budget={str(at):-1 for at in misses},
                          default_found=True,inverted_return=False,max_body_steps=limit,stop_after=stop_after))

    add('retained-root-normal-attack-start',717,stop_after=725)
    for mode, skill, potion in ((0,0,0),(1,1,1),(2,2,2),(3,3,3),(0,2,4)):
        add(f'coordinator-{mode}-{skill}-{potion}',4635,mode=mode,skill=skill,potion=potion,limit=300)
    add('sdk-missing-before-worker-start',4635,misses=(4641,),limit=100)
    add('alternate-skill-enable-marker',4635,misses=(4693,),limit=200)
    add('dungeon-controller',1495,limit=200)
    for wrapper in plan['worker_wrappers']:
        add(f'worker-{wrapper["worker_entry"]}-hit',wrapper['worker_entry'])
        target = wrapper['body_entry']
        if target in (6481,6517,6553,6589):
            query = next(a['record'] for a in plan['actions'] if target<=a['record']<target+35 and a['kind']=='find_color')
            add(f'worker-{wrapper["worker_entry"]}-three-misses',wrapper['worker_entry'],misses=(query,))
    return cases


def replay(plan, child, spec):
    shared = dict(spec['shared'])
    machine = CubeWorkerMachine(plan,child,spec['entry'],lambda key,at:shared[key],spec['values'],
                                spec['frame_slots'],spec['root_slots'])
    records, events = [], []
    for _ in range(spec['max_body_steps']):
        if machine.done:
            break
        event = machine.step()
        at, kind = event['record'], event['kind']
        records.append(at)
        events.append(event)
        if kind == 'write_global':
            shared[event['key']] = event['value']
        if kind == 'worker_start':
            event['worker_id'] = 10000 + at
            machine.supply_worker_id(event['worker_id'])
        if kind == 'dm_real_mouse_intent':
            machine.supply_dm_return(1)
        if kind in ('find_color','find_pic'):
            found = str(at) not in spec['miss_budget']
            x,y = (event['rect'][0]+1,event['rect'][1]+2) if found else (-1,-1)
            ret = (1 if found else 0) if kind=='find_color' else (0 if found else -1)
            machine.supply_query(x,y,ret)
            events.append(dict(kind='query_reply',record=at,x=x,y=y,return_value=ret))
        if kind == 'random_int':
            machine.supply_random(event['lower'])
        if at == spec['stop_after']:
            break
    return dict(id=spec['id'],records=records,events=events,reason=machine.reason or 'fixture_stop',
                next_record=machine.pc,final_shared=shared,root_slots=machine.root_slots,
                frames=len(machine.frames),returns=machine.returns)


def main():
    plan, child = load('data/cube-workers.json'), load('data/cube-routines.json')
    cases = build_cases(plan)
    results = [replay(plan,child,spec) for spec in cases]
    (PROJECT/'data/cube-worker-cases.json').write_text(json.dumps({'cases':cases,'synthetic_prefix_values':True},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases),'records_covered':len({at for r in results for at in r['records']}),
                      'spawn_sites':sorted({e['record'] for r in results for e in r['events'] if e['kind']=='worker_start'})}))


if __name__ == '__main__':
    main()
