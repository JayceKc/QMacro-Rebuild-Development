"""Controlled cases for parent dispatch, isolated workers, and movement."""
import json

from export_battle_control import RANGES
from replay_shared_battle import PROJECT,load,replay,scalar_names

SKILL = 'VF1D6A1A9B9B5C2A84D6A65757378756D'
POTION_F1 = 'VF4DEB4D4A180C4BF9FC365757378756D'
POTION_1 = 'VF4DEB4D4C3A1C2BBFCA2B7DC7378756D'
F1_LEVEL = 'VFEBEB7DC7378756D'
ONE_LEVEL = 'VFEBED5ACC4AEC4A59FC365757378756D'
TOWER = 'VFF89AF887378756D'
TOWER_MODE = 'VFD8CD4CBA2D9A19C4D6A65757378756D'
PURPLE = 'V98B8D0C8A4B7B6A84D6A65757378756D'


def build_cases(module,plan,control):
    cases = []
    actions = plan['actions']+control['actions']
    routines = {r['name']:r for r in control['routines']}
    shared = {a['key']:0 for a in actions if a['kind'] in ('read_global','write_global')}
    for i,key in enumerate(sorted({w['shared_id_key'] for w in control['worker_wrappers'] if w['shared_id_key']})):
        shared[key]=4100+i
    shared['V8186B4D47378756D']='123456'
    values = {name:0 for name in sorted(set(scalar_names(actions)))}
    values.update(YC=100,DM_RET=0,INTX=911,INTY=522,INTXX=1720,INTYY=165,XX1=1743.0,YY1=168.0,
                  V88A365757378756D=3.1415926)

    def add(label,routine,*, options=None, local=None, found=True, misses=(), wrapper=False, limit=230):
        cases.append(dict(id=len(cases)+1,label=label,entry=routine['entry'],last=routine['last'],worker_wrapper=wrapper,
                          shared=shared|(options or {}),values=values|(local or {}),default_found=found,
                          miss_budget={str(at):-1 for at in misses},return_overrides={},random_upper=not found,max_body_steps=limit))

    for selector in range(7):
        add(f'skill-{selector}',routines['工作選擇'],local={SKILL:selector})
    for level in range(4):
        add(f'potion-{level}',routines['工作選擇'],local={POTION_F1:1,POTION_1:1,F1_LEVEL:level,ONE_LEVEL:level})
    for tower,purple in ((0,0),(3,1)):
        settings = {TOWER:tower,TOWER_MODE:1,PURPLE:purple}
        add(f'start-{tower}',routines['開始打怪'],options=settings)
        add(f'stop-{tower}',routines['停止打怪'],options=settings)
    for r in control['routines']:
        if r['name'] in ('開始打怪','停止打怪','工作選擇'):
            continue
        add(r['name']+'-hit',r)
        add(r['name']+'-miss',r,found=False)
        if r['name'] in ('走位','塔內走位'):
            for x,y in ((1760,165),(1720,180),(1760,180),(1743,165),(1743,180),(0,168)):
                add(f'{r["name"]}-{x}-{y}',r,local={'INTXX':x,'INTYY':y})
    for w in control['worker_wrappers']:
        entry=w['worker_entry']
        add(f'worker-wrapper-{entry}',{'entry':entry,'last':entry+2},wrapper=True,limit=150)
    return cases


def main():
    for module in RANGES:
        plan,control = load(f'data/battle-{module}.json'),load(f'data/battle-control-{module}.json')
        cases = build_cases(module,plan,control)
        results = [replay(plan,c,control) for c in cases]
        ranges = [[r['entry'],r['last']] for r in plan['routines']+control['routines']]
        out = dict(cases=cases,ranges=ranges,boundaries=control['boundaries'],synthetic_context=True)
        (PROJECT/f'data/battle-control-{module}-cases.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        starts = {e['record'] for result in results for e in result['events'] if e['kind']=='worker_start'}
        print(json.dumps({'module':module,'cases':len(cases),'starts':len(starts),
                          'unobserved_starts':sorted({w['start_record'] for w in control['worker_wrappers']}-starts),
                          'coverage':len({at for result in results for at in result['records']})}))


if __name__ == '__main__':
    main()
