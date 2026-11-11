import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/gathering-routines.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    cases=[]
    def add(entry=916,strategy=1,mode=0,home=0,miss=None,flip=False,rx=1233,ry=695,updates=None):
        cases.append({'id':len(cases),'entry':entry,'context':{'repair_strategy':strategy,'vitality_finish_mode':mode,
                      'home_on_no_vitality':home,'home_on_no_durability':home,'sdk_marker':'112233','worker_id':12345,'simulation_mode':0},
                      'miss_budget':{str(k):v for k,v in (miss or {}).items()},'inverted_return':flip,'random_x':rx,'random_y':ry,'updates':updates or {}})
    for rx in (1233,1252):
        for ry in (695,709):add(strategy=0,rx=rx,ry=ry)
    for record in (0,990,1024,1039,1043,1047,1100,1132):
        for flip in (False,True):add(miss={record:1} if record else {},flip=flip)
    for strategy in (-1,2,3,4,5,6,7):
        for home in (0,1):
            for flip in (False,True):add(strategy=strategy,home=home,flip=flip)
    for record in (0,1285,1312,1334):
        for budget in ((0,) if not record else (1,3)):
            for flip in (False,True):add(entry=1277,miss={record:budget} if record else {},flip=flip)
    for mode in range(5):
        for home in (0,1):
            for hit in (1356,1361,1366,1371):
                add(entry=1344,mode=mode,home=home,miss={i:1 for i in (1356,1361,1366,1371) if i<hit})
    for record in (1352,1397,1419,1468,1517,1560):
        for budget in (1,3,5):
            mode={1397:0,1419:1,1468:2,1517:3,1560:4}.get(record,0)
            add(entry=1344,mode=mode,miss={record:budget})
    for budget in (1,3,4):add(entry=1277,miss={1285:budget,1312:budget})
    for record,mode in ((1419,1),(1468,2)):
        add(entry=1344,mode=mode,home=1,miss={record:5})
    add(entry=1344,miss={i:1 for i in (1356,1361,1366,1371)})
    for mode in (-1,5):add(entry=1344,mode=mode)
    add(strategy=0,updates={'1270':{'worker_id':54321}})
    output={'cases':cases,'case_count':len(cases),'sdk_marker_is_synthetic_test_data':True,'worker_ids_are_unmatched_test_ids':True,'native_timing_equivalence_claimed':False}
    path=PROJECT/'data/gathering-cases.json';path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'cases':len(cases),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
