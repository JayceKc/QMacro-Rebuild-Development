"""Saved original-body observations against the owned closed grammar."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/gathering-routines.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def effects(case):
    result=[];pending=None
    for e in case['events']:
        kind=e['kind'];value=None;record=e['record']
        if kind in ('find_color','find_pic','builtin_color'):pending=e;continue
        if kind=='query_reply':
            assert pending and pending['record']==record
            args=pending['rect']+[pending['path'] if pending['kind']=='find_pic' else pending['color']]
            if pending['kind']=='find_pic':args.append(pending['delta'])
            args+=([pending['direction'],pending['similarity']] if pending['kind']=='builtin_color' else [pending['similarity'],pending['direction']])
            value={'arguments':args,'x':e['x'],'y':e['y'],'return_value':e['return_value']}
            result.append({'record':record,'kind':'builtin_observation' if pending['kind']=='builtin_color' else pending['kind'],'value':value});pending=None;continue
        if kind=='delay':value=e['milliseconds']
        elif kind in ('key_press','key_down','key_up','mouse_click','move_to','thread_control'):value=e['arguments']
        elif kind=='trace':value=e['text']
        elif kind=='exit_script':value=e['restart']
        else:continue
        result.append({'record':record,'kind':'thread_control_unmatched' if kind=='thread_control' else kind,'value':value})
    assert pending is None;return result


def compare(native,owned):
    assert native['ok'] and owned['ok'] and len(native['cases'])==len(owned['cases'])==129
    matched=[];count=0
    for old,new in zip(native['cases'],owned['cases']):
        for k in ('id','records','reason','query_count'):assert old[k]==new[k],(old['id'],k)
        if new['reason']=='routine_return':assert old['root_frame_restored'] and old['return_is_empty'] and new['last_return'] is None and new['frame_depth']==0
        expected=effects(new);actual=[{'record':e['Record'],'kind':e['Kind'],'value':e['Value']} for e in old['events'] if e['Kind']!='builtin_color']
        assert expected==actual,('external events',old['id'],next(((i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),(len(actual),len(expected))))
        count+=len(expected);matched.append({'id':old['id'],'records':len(old['records']),'events':len(expected),'reason':old['reason']})
    return {'ok':True,'cases':129,'external_events':count,'records_covered':len({r for c in native['cases'] for r in c['records']}),'matched':matched}


def main():
    path=PROJECT/'verification/original-gathering-routines.json';native=json.loads(path.read_text(encoding='utf-8-sig'))
    owned=json.loads((PROJECT/'verification/gathering-routines-owned.json').read_text())
    assert native['source_program_sha256']==hashlib.sha256((PROJECT/'programs/08.json').read_bytes()).hexdigest()
    assert native['case_spec_sha256']==owned['case_spec_sha256']==hashlib.sha256((PROJECT/'data/gathering-cases.json').read_bytes()).hexdigest()
    assert owned['source_plan_sha256']==hashlib.sha256((PROJECT/'data/gathering-routines.json').read_bytes()).hexdigest()
    for name,sha in owned['owned_source_sha256'].items():assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==sha
    plan=json.loads((PROJECT/'data/gathering-routines.json').read_text())
    action_sha=hashlib.sha256(json.dumps(plan['actions'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    result=compare(native,owned);result.update(source_action_sha256=action_sha,original_guest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_program_sha256=native['source_program_sha256'],
        source_plan_sha256=owned['source_plan_sha256'],case_spec_sha256=owned['case_spec_sha256'],owned_source_sha256=owned['owned_source_sha256'],
        original_native_loaded=False,game_input_sent=False,real_worker_pause_resume_verified=False,original_rng_equivalent=False,original_timing_verified=False,full_module_restored=False)
    (PROJECT/'verification/gathering-routines-original-vs-rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('ok','cases','external_events','records_covered')}))


if __name__=='__main__':main()
