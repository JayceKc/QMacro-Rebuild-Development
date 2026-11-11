from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/05.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    cases=[]
    def add(entry=541,repair=1,mode=0,slow=0,home=0,fail=0,flip=False,rx=1233,ry=715,updates=None):
        cases.append({'id':len(cases),'entry':entry,'context':{'repair_mode':repair,'completion_mode':mode,'slow_repair':slow,
                      'return_home':home,'sdk_marker':'112233','saved_cursor_x':731,'saved_cursor_y':419,'simulation_mode':0},
                      'first_failed_record':fail,'inverted_return':flip,'random_x':rx,'random_y':ry,'updates':updates or {}})
    for slow in (0,1):
        for rx in (1233,1242):
            for ry in (715,719):add(repair=0,slow=slow,rx=rx,ry=ry)
    for fail in (0,618,650,655,668,672,676,729,759):
        for slow in (0,1):
            for flip in (False,True):add(repair=1,slow=slow,fail=fail,flip=flip)
    for mode in range(6):
        for home in (0,1):
            for flip in (False,True):add(repair=2,mode=mode,home=home,flip=flip)
    for fail in (0,885,915):
        for flip in (False,True):add(entry=879,fail=fail,flip=flip)
    for repair in (-1,3):add(repair=repair)
    add(repair=2,mode=5,updates={'864':{'completion_mode':4}})
    output={'cases':cases,'case_count':len(cases),'sdk_marker_is_test_data':True,'random_values_are_controlled_inputs':True,
            'native_rng_equivalence_claimed':False,'game_input_sent':False,'full_module_restored':False}
    path=PROJECT/'data/fishing-cases.json';path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(cases),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
