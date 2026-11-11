"""Compare original guest bodies to the owned fishing state machine exactly."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'qmacro_fishing.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def owned_events(case):
    result=[];pending=None
    for event in case['events']:
        kind=event['kind'];record=event['record'];value=None
        if kind in ('find_color','find_pic'):pending=event;continue
        if kind=='query_reply':
            assert pending and pending['record']==record
            args=pending['rect']+[pending['color'] if pending['kind']=='find_color' else pending['path']]
            if pending['kind']=='find_pic':args.append(pending['delta'])
            args += [pending['similarity'],pending['direction']]
            result.append({'record':record,'kind':pending['kind'],'value':{'arguments':args,'x':event['x'],'y':event['y'],'return_value':event['return_value']}})
            pending=None;continue
        if kind=='delay':value=event['milliseconds']
        elif kind in ('key_press','key_down','key_up','mouse_click','move_to'):value=event['arguments']
        elif kind=='trace':value=event['text']
        elif kind=='exit_script':value=event['restart']
        elif kind=='load_service_intent':value=event['name']
        elif kind=='os_exit_intent':value=event['flags']
        else:continue
        result.append({'record':record,'kind':kind,'value':value})
    assert pending is None
    return result


def main():
    path=PROJECT/'verification/original-fishing-vm-test.json';raw=path.read_bytes();native=json.loads(raw.decode('utf-8-sig'))
    owned=json.loads((PROJECT/'verification/fishing-owned-replay.json').read_text(encoding='utf8'))
    assert native['ok'] and native['completed_cases']==77 and native['original_body_executed']
    assert native['source_program_sha256']==hashlib.sha256((PROJECT/'programs/05.json').read_bytes()).hexdigest()
    assert native['case_spec_sha256']==owned['case_spec_sha256']==hashlib.sha256((PROJECT/'data/fishing-cases.json').read_bytes()).hexdigest()
    assert owned['source_plan_sha256']==hashlib.sha256((PROJECT/'data/fishing-routines.json').read_bytes()).hexdigest()
    code_root=ROOT if (ROOT/'qmacro_fishing.py').exists() else ROOT/'work'
    for name,sha in owned['owned_source_sha256'].items():assert hashlib.sha256((code_root/name).read_bytes()).hexdigest()==sha,('stale owned code',name)
    matched=[];total=0
    for old,new in zip(native['cases'],owned['cases']):
        assert old['id']==new['id'] and old['records']==new['records'],('instruction path',old['id'])
        assert old['reason']==new['reason'] and old['query_count']==new['query_count'],('termination/query count',old['id'])
        if new['reason']=='routine_return':assert old['root_frame_restored'] and old['return_is_empty'] and new['last_return'] is None and new['frame_depth']==0
        expected=owned_events(new);actual=[{'record':e['Record'],'kind':e['Kind'],'value':e['Value']} for e in old['events']]
        assert actual==expected,('external event arguments/order',old['id'],next(((i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),(len(actual),len(expected))))
        total+=len(expected);matched.append({'id':old['id'],'records':len(new['records']),'events':len(expected),'reason':new['reason']})
    assert len(matched)==77
    plan=json.loads((PROJECT/'data/fishing-routines.json').read_text(encoding='utf8'))
    action_sha=hashlib.sha256(json.dumps(plan['actions'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    report={'ok':True,'cases':77,'external_events':total,'matched':matched,'source_action_sha256':action_sha,'owned_source_sha256':owned['owned_source_sha256'],
            'original_guest_report_sha256':hashlib.sha256(raw).hexdigest(),'source_plan_sha256':owned['source_plan_sha256'],
            'source_program_sha256':native['source_program_sha256'],'case_spec_sha256':owned['case_spec_sha256'],
            'original_native_loaded':False,'game_input_sent':False,'original_rng_equivalent':False,'original_timing_verified':False,
            'full_module_restored':False}
    (PROJECT/'verification/fishing-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'ok':True,'cases':77,'external_events':total}))


if __name__=='__main__':main()
