"""Controlled retained entry, skip chain, UI waits and capture fixtures."""
import json

from qmacro_cube_retained import CubeRetainedMachine
from replay_cube_main import PROJECT, load, scalar_names


def build_cases(tail, workers):
    cases = []

    def add(label, entry, *, options=None, misses=(), limit=250, stop_after=None, message_step=0, close_step=0):
        actions = tail['actions'] + workers['actions']
        shared = {a['key']:0 for a in actions if a['kind'] in ('read_global','write_global')}
        shared.update({'V8186B4D47378756D':'123456','V9DB8B1BECAAE756D':1,'VFAAFD9C9B7A43C294D6A65757378756D':4102,
                       'V98B8DCA33A3C756D':4103,'VFEBEB7DC3A3C756D':4104})
        shared.update(options or {})
        values = {name:0 for name in sorted(set(scalar_names(actions))) if not name.startswith('CUBE_ROOT_SLOT_')}
        cases.append(dict(id=len(cases)+1,label=label,entry=entry,shared=shared,values=values,
                          root_slots={'11':4321} if entry==531 else {},miss_budget={str(at):-1 for at in misses},
                          default_found=True,inverted_return=False,max_body_steps=limit,stop_after=stop_after,
                          message_step=message_step,close_step=close_step))

    add('normal-entry-missing-prefix',0)
    for mode in range(4):
        for option in (0,1):
            add(f'entry-suffix-mode-{mode}-{option}',531,misses=(563,),options={'V87ADD284A491C3BE4D6A65757378756D':mode,
                                                               'V9BD1D187A1C3CCB54D6A65757378756D':option})
    add('entry-suffix-sdk-miss',531,misses=(559,),limit=120)
    add('entry-suffix-color-present-retries',531,limit=120)
    add('entry-suffix-no-skill',531,misses=(563,),options={'V9DB8B1BECAAE756D':0})
    add('retained-skip-chain',854)
    add('message-then-ui-close',6816,message_step=2,close_step=6)
    add('message-stays-unavailable',6816,message_step=100,close_step=100,limit=12)
    add('capture-eight-skill-images',6444,misses=(6448,),stop_after=6478)
    add('capture-waits-while-marker-present',6444,limit=100)
    for entry in (3488,3510,3538):
        add(f'periodic-key-{entry}',entry,limit=90)
    return cases


def replay(tail,main,workers,child,spec):
    shared = dict(spec['shared'])
    machine = CubeRetainedMachine(tail,main,workers,child,spec['entry'],lambda key,at:shared[key],spec['values'],
                                 {int(k):v for k,v in spec['root_slots'].items()})
    records, events, waits = [], [], []
    for step in range(spec['max_body_steps']):
        if machine.done:
            break
        machine.runner_message_ready = step>=spec['message_step']
        machine.ui_open = step<spec['close_step']
        event = machine.step()
        at, kind = event['record'], event['kind']
        records.append(at)
        events.append(event)
        if kind in ('waiting_ui','waiting_message'):
            waits.append(dict(record=at,kind=kind))
        elif kind=='write_global':
            shared[event['key']] = event['value']
        elif kind in ('find_color','find_pic'):
            found = str(at) not in spec['miss_budget']
            x,y = (event['rect'][0]+1,event['rect'][1]+2) if found else (-1,-1)
            ret = (1 if found else 0) if kind=='find_color' else (0 if found else -1)
            machine.supply_query(x,y,ret)
            events.append(dict(kind='query_reply',record=at,x=x,y=y,return_value=ret))
        elif kind=='capture_intent':
            machine.supply_capture_return(1)
        elif kind=='random_int':
            machine.supply_random(event['lower'])
        if at==spec['stop_after']:
            break
    return dict(id=spec['id'],records=records,events=events,waits=waits,reason=machine.reason or 'fixture_stop',
                next_record=machine.pc,final_shared=shared,root_slots=machine.root_slots)


def main():
    tail,main_plan,workers,child = (load('data/'+name+'.json') for name in ('cube-retained-tail','cube-main','cube-workers','cube-routines'))
    cases = build_cases(tail,workers)
    results = [replay(tail,main_plan,workers,child,spec) for spec in cases]
    (PROJECT/'data/cube-retained-cases.json').write_text(json.dumps({'cases':cases,'synthetic_prefix_values':True},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases),'results':[(s['label'],r['reason'],r['next_record']) for s,r in zip(cases,results)]}))


if __name__ == '__main__':
    main()
