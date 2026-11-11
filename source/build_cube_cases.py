"""Explicit synthetic inputs for preserved cube bodies, never guessed prefix values."""
import copy,json
from export_cube_routines import PROJECT

MODE='V8080D6BCA5D6CF9E4D6A65757378756D';NEXT='V9FC0A2A5CEBFBCC64D6A65757378756D'
COUNTER='V8080D6BCC7B6BF904D6A65757378756D';LAST='VF0ADACDECE99BF954D6A65757378756D'
SDK='V8186B4D47378756D'


def build(plan):
    cases=[]
    def add(entry,label,**changes):
        shared={MODE:0,NEXT:1,COUNTER:0,LAST:24,SDK:'123456','VF0ADACDECCD2BFD14D6A65757378756D':1,
                'V86C8D9CDC7B6756D':0,'V9BB6D6D67378756D':1,'VF4C1DE94BBB6BB9C4D6A65757378756D':1,'V9BD1D187A1C3CCB54D6A65757378756D':1}
        values={'g_iSimulateModeInVBSBlock':0,'V9D82B7DFBEB3C69B4D6A65757378756D':0}
        shared.update(changes.pop('shared',{}));values.update(changes.pop('values',{}))
        c={'id':len(cases)+1,'label':label,'entry':entry,'shared':shared,'values':values,'frame_slots':{},
           'updates':{},'default_found':True,'miss_budget':{'5153':-1},'inverted_return':False,'random_upper':False,'max_body_steps':6000}
        c.update(changes);cases.append(c)
    for mode in range(4):
        for counter in range(4):
            for found in (False,True):add(857,f'weekly-mode{mode}-counter{counter}-found{found}',shared={'V86C8D9CDC7B6756D':mode,COUNTER:counter},default_found=found)
    pics=[a['record'] for a in plan['actions'] if 857<=a['record']<=1493 and a['kind']=='find_pic']
    for at in pics:
        for upper in (False,True):add(857,f'weekly-one-miss{at}-upper{upper}',miss_budget={str(at):-1},random_upper=upper)
    for character in range(1,25):
        for policy in ('hit','miss','upper'):
            budgets={'5153':-1}
            if policy=='miss':budgets.update({str(a['record']):-1 for a in plan['actions'] if 5020<=a['record']<=6442 and a['kind']=='find_pic'})
            add(5020,f'character{character}-{policy}',shared={NEXT:character},miss_budget=budgets,random_upper=policy=='upper',inverted_return=policy=='upper')
    for mode in (-1,0,1,2,3,4):
        add(6740,f'finish-mode{mode}',shared={MODE:mode})
        add(5020,f'beyond-last-mode{mode}',shared={NEXT:25,MODE:mode},values={'V9D82B7DFBEB3C69B4D6A65757378756D':1})
    add(6740,'finish-dynamic-elseif',shared={MODE:99},updates={'6748':{MODE:99},'6759':{MODE:99},'6799':{MODE:3}})
    for at in (5159,5163,5167,5173,6426):add(5020,f'wait-retry-at{at}',miss_budget={'5153':-1,str(at):1})
    add(5020,'wait-first-loop-no-detection',default_found=False,miss_budget={},max_body_steps=200)
    add(5020,'wait-final-loop-no-sdk',miss_budget={'5153':-1,'6426':-1},max_body_steps=700)
    for kind in range(5):
        for counter in (0,2,3):add(857,f'weekly-kind{kind}-counter{counter}',shared={'V9BB6D6D67378756D':kind,COUNTER:counter})
    for enabled in (0,1):add(857,f'weekly-tail-option{enabled}',shared={'V9BD1D187A1C3CCB54D6A65757378756D':enabled})
    for kind in (2,3):
        for at in pics:add(857,f'weekly-kind{kind}-one-miss{at}',shared={'V9BB6D6D67378756D':kind},miss_budget={str(at):-1},random_upper=True)
    add(5020,'wait-sdk-matched-still-retry',miss_budget={'5153':0},max_body_steps=200)
    add(857,'weekly-counter-changed-between-elseif-reads',shared={COUNTER:3},updates={'908':{COUNTER:0}})
    add(857,'weekly-gate-false',shared={'V9BB6D6D67378756D':0,'VF4C1DE94BBB6BB9C4D6A65757378756D':0})
    add(857,'weekly-tail-disabled',shared={'VF4C1DE94BBB6BB9C4D6A65757378756D':0})
    add(5020,'beyond-last-mode1-no-exit-click',shared={NEXT:25,MODE:1})
    add(5020,'character25-no-selection-branch',shared={NEXT:25,LAST:25})
    return cases


def main():
    plan=json.loads((PROJECT/'data/cube-routines.json').read_text('utf8'));cases=build(plan)
    (PROJECT/'data/cube-cases.json').write_text(json.dumps({'cases':cases,'sdk_is_synthetic':True,'prefix_initial_values_are_explicit_fixture_data':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases)}))


if __name__=='__main__':main()
