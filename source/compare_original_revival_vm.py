"""Compare the owned monitor to the actual fixed-guest original-body replay."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/revival-plan.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
sys.path.insert(0,str(PROJECT))
from qmacro_revival import RevivalMachine
native=ROOT/'outputs/plugin-recovery/original-revival-vm-test.json'
if not native.exists():native=PROJECT/'verification/original-revival-vm-test.json'

def main():
    if not native.exists():raise SystemExit('Original-body guest report is still pending; no equivalence claim can be made.')
    data=json.loads(native.read_text(encoding='utf-8-sig'));assert data['ok'] and data['completed_cases']==18
    plan_path=PROJECT/'data/revival-plan.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
    matched=0;cases=[]
    for case in data['cases']:
        expected=[];queries=[];cursor=[]
        for event in case['events']:
            kind=event['Kind'];at=event['Record'];value=event['Value']
            if kind in ('delay','trace','set_error_display'):expected.append((at,kind,value))
            elif kind=='mouse_mode_request':expected.append((at,'configure_mouse',tuple(value)))
            elif kind in ('find_color','find_pic'):
                expected.append((at,kind,tuple(value['arguments'])));queries.append(value)
            elif kind=='cursor_read':expected.append((at,'read_cursor',tuple(value)));cursor.append(value)
            elif kind in ('move_to','mouse_click','thread_control_unmatched'):
                expected.append((at,'thread_control' if kind=='thread_control_unmatched' else kind,tuple(value)))
            else:assert kind=='source_rewrite',('Unexpected original-body event',kind)
        model=RevivalMachine(plan,lambda role:{'sdk_marker':'112233','skill_worker':41,'potion_worker':42}[role])
        actual=[];q=0;c=0
        for _ in range(1000):
            event=model.step();kind=event['kind'];at=event['record']
            if kind=='delay':actual.append((at,kind,event['milliseconds']))
            elif kind=='log':actual.append((at,'trace',event['text']))
            elif kind=='set_error_display':actual.append((at,kind,event['value']))
            elif kind=='configure_mouse':actual.append((at,kind,tuple(event['arguments'])));model.supply_mouse_configuration(1)
            elif kind in ('find_color','find_pic'):
                args=event['rect']+([event['color'],event['similarity'],event['direction']] if kind=='find_color' else [event['path'],event['delta'],event['similarity'],event['direction']])
                actual.append((at,kind,tuple(args)));value=queries[q];q+=1;model.supply_query(value['x'],value['y'],value['return_value'])
            elif kind=='read_cursor':value=cursor[c];c+=1;actual.append((at,kind,tuple(value)));model.supply_cursor(*value)
            elif kind=='move_to':actual.append((at,kind,(event['x'],event['y'])))
            elif kind=='mouse_click':actual.append((at,kind,(event['button'],0,event['count'])))
            elif kind=='thread_control':actual.append((at,kind,(event['worker_id'],event['mode'])))
            if model.cycles==case['cycles']:break
        else:raise AssertionError('Owned monitor exceeded loop bound')
        assert q==len(queries) and c==len(cursor)
        assert actual==expected,(case['first_failed_query'],case['inconsistent_return_value'],next(((a,b) for a,b in zip(actual,expected) if a!=b),('length',len(actual),len(expected))))
        matched+=len(actual);cases.append({'first_failed_query':case['first_failed_query'],'inconsistent_return_value':case['inconsistent_return_value'],'matched_events':len(actual)})
    report={'ok':True,'cases':len(cases),'matched_events':matched,'observations':cases,
            'source_sha256':hashlib.sha256((PROJECT/'qmacro_revival.py').read_bytes()).hexdigest(),
            'plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),'guest_report_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
            'scope':'Preserved original-body actions with controlled query/cursor results, synthetic SDK marker and recording-only thread/mouse ports.',
            'sdk_marker_recovered':False,'live_game_revival_verified':False,'full_program_restored':False}
    (PROJECT/'verification/revival-original-vs-rebuild.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('observations','scope')}))
if __name__=='__main__':main()
