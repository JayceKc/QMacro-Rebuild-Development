import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    cases=[]
    def add(entry=593,mode=3,fallback=0,repeats=0,sdk_miss=0,strategy=0,vitality=0,home=0,miss=None,flip=False,cycles=1,target=(1800,120),same_history=False,yc=66,jitter=-15):
        context={'gather_mode':mode,'repair_strategy':strategy,'vitality_finish_mode':vitality,'home_on_no_vitality':home,'home_on_no_durability':home,
                 'sdk_marker':'112233','worker_id':12345,'simulation_mode':0,'minimap_center_x':1743,'minimap_center_y':168,'walk_pi':3.1415926}
        initial={'fallback_attempts':fallback,'walk_repeats':repeats,'sdk_miss_count':sdk_miss,'walk_angle':None,
                 **{f'history_{axis}{n}':(2 if axis=='x' else 3) if same_history else 0 for axis in ('x','y') for n in range(1,4)}}
        cases.append({'id':len(cases),'entry':entry,'context':context,'initial':initial,'miss_budget':{str(k):v for k,v in (miss or {}).items()},
                      'inverted_return':flip,'max_main_cycles':cycles,'target_point':list(target),'random_values':{'recovery_delay':yc,'walk_jitter_x':jitter,'walk_jitter_y':jitter,'random_x':1233,'random_y':695},
                      'expected_overflow':target==(1743,168) and entry==540})
    for fallback in (-1,4,5,6):
        for yc in (66,181):add(entry=507,fallback=fallback,yc=yc)
    for target in ((1800,120),(1700,160)):
        for repeats in (9,10):
            for yc in (66,181):
                for jitter in (-15,-1):add(entry=540,target=target,repeats=repeats,yc=yc,jitter=jitter)
    add(entry=540,target=(1743,168))
    for n in (0,1,2,3):add(entry=581,sdk_miss=n)
    for mode in (-1,0,1,2,4):add(mode=mode)
    # Three alternatives after tool/vitality checks: hoe, mineral name, minimap.
    for route in ('hoe','name','minimap','none'):
        for strategy in (0,1):
            for flip in (False,True):
                miss={} if route=='hoe' else {621:4}
                if route in ('minimap','none'):miss[640]=4
                if route=='none':miss[667]=4
                add(strategy=strategy,miss=miss,flip=flip,cycles=2)
    for n in (1,3):add(miss={601:n},cycles=n+1)
    for strategy in (2,3,4,5,6):
        for home in (0,1):add(strategy=strategy,home=home)
    for mode,at in ((0,1397),(1,1419),(2,1468),(3,1517),(4,1560)):
        for home in (0,1):add(vitality=mode,home=home,miss={at:5})
    add(miss={621:4},cycles=3)
    add(miss={621:2},same_history=True,cycles=1)
    output={'cases':cases,'sdk_marker_is_synthetic_test_data':True,'prefix_dependent_values_are_explicit_test_inputs':True,'erased_prefix_executed':False,'full_module_restored':False}
    path=PROJECT/'data/gathering-main-cases.json';path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'cases':len(cases),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
