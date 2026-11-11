from pathlib import Path
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'outputs/QMacro-Rebuild-Development'
if (ROOT/'qmacro_potion.py').exists():PROJECT=ROOT
spec=importlib.util.spec_from_file_location('potion',PROJECT/'qmacro_potion.py');potion=importlib.util.module_from_spec(spec);spec.loader.exec_module(potion)
plans={p['entry']:p for p in json.loads((PROJECT/'data/potion-plans.json').read_text(encoding='utf-8'))['plans']}
native_path=ROOT/'outputs/plugin-recovery/original-potion-vm-test.json'
if not native_path.exists():native_path=ROOT/'verification/original-potion-vm-test.json'
data=json.loads(native_path.read_text(encoding='utf-8-sig'));assert data['ok'] and data['completed_cases']==48


def main():
    total=0;cases=[]
    for case in data['cases']:
        plan=plans[case['entry']];machine=potion.PotionMachine(plan,bool(case['use_f1']),bool(case['use_one']))
        expected=[];colors=[]
        for e in case['events']:
            kind=e['Kind'];record=e['Record'];value=e['Value']
            if kind=='delay':expected.append((record,kind,value))
            elif kind in ('key_press','key_down','key_up'):
                key,mode,count=value;assert mode==0 and count==1
                expected.append((record,'key' if kind=='key_press' else kind,key))
            elif kind=='find_color':
                expected.append((record,kind,tuple(value['rect']),value['color'],value['similarity'],value['direction']))
                colors.append(value)
            elif kind=='set_error_display':expected.append((record,kind,value))
        actual=[];index=0
        for _ in range(10000):
            e=machine.step();kind=e['kind'];record=e['record']
            if kind=='delay':actual.append((record,kind,e['milliseconds']))
            elif kind in ('key','key_down','key_up'):actual.append((record,kind,e['key']))
            elif kind=='set_error_display':actual.append((record,kind,int(e['enabled'])))
            elif kind=='find_color':
                actual.append((record,kind,tuple(e['rect']),e['color'],e['similarity'],e['direction']))
                value=colors[index];index+=1;machine.supply_color_result(value['x'],value['y'],value['return_value'])
            if machine.cycles==len(case['results']):break
        else:raise AssertionError('Unexpected potion loop')
        assert index==len(colors)
        assert actual==expected,(case['entry'],case['use_f1'],case['use_one'],case['results'],
            next(((a,b) for a,b in zip(actual,expected) if a!=b),('lengths',len(actual),len(expected))))
        total+=len(actual);cases.append({'entry':case['entry'],'use_f1':case['use_f1'],'use_one':case['use_one'],
                                       'color_results':case['results'],'matched_events':len(actual)})
    report={'ok':True,'cases':len(cases),'matched_events':total,'observations':cases,
            'source_sha256':hashlib.sha256((PROJECT/'qmacro_potion.py').read_bytes()).hexdigest(),
            'plans_sha256':hashlib.sha256((PROJECT/'data/potion-plans.json').read_bytes()).hexdigest(),
            'guest_report_sha256':hashlib.sha256(native_path.read_bytes()).hexdigest(),
            'scope':'Exact record/color-query/key-lifecycle/delay events with controlled color results, not live capture or game input.',
            'full_program_restored':False,'live_game_potion_verified':False}
    (PROJECT/'verification/potion-original-vs-rebuild.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('observations','scope')}))


if __name__=='__main__':main()
