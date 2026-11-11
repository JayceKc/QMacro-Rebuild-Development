"""Compare original guest records and supplied effects; no original execution."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'data/gathering-worker.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def compare(native,owned):
    assert native['ok'] and owned['ok'] and len(native['cases'])==len(owned['cases'])==41
    matched=[];events=0
    for a,b in zip(native['cases'],owned['cases']):
        for key in ('id','records','next_record','loops','reason'):assert a[key]==b[key],(a['id'],key)
        expected=[]
        for e in b['events']:
            kind=e['kind']
            if kind in ('find_color','find_pic'):value={k:e[k] for k in ('arguments','x','y','return_value')}
            elif kind in ('delay','load_vision_intent','set_show_error','key_press'):value=e['value']
            else:continue
            expected.append({'record':e['record'],'kind':kind,'value':value})
        actual=[{'record':e['Record'],'kind':e['Kind'],'value':e['Value']} for e in a['events'] if e['Kind']!='source_rewrite']
        assert expected==actual,('external events',a['id'])
        rewrites=[e for e in a['events'] if e['Kind']=='source_rewrite']
        assert len(rewrites)==int(891 in a['records'])
        for e in rewrites:assert e['Record']==891 and e['Value']==['SET DM=CREATEOBJECT("dm.dmsoft")','Set DM=QMacroGatheringVision']
        events+=len(actual);matched.append({'id':a['id'],'records':len(a['records']),'external_events':len(actual),'next_record':a['next_record']})
    return {'ok':True,'cases':41,'external_events':events,'records_covered':len({r for c in native['cases'] for r in c['records']}),'matched':matched}


def main():
    path=PROJECT/'verification/original-gathering-worker.json';native=json.loads(path.read_text(encoding='utf-8-sig'))
    owned=json.loads((PROJECT/'verification/gathering-worker-owned.json').read_text())
    assert native['source_program_sha256']==hashlib.sha256((PROJECT/'programs/08.json').read_bytes()).hexdigest()
    assert native['case_spec_sha256']==owned['case_spec_sha256']==hashlib.sha256((PROJECT/'data/gathering-worker-cases.json').read_bytes()).hexdigest()
    assert owned['source_plan_sha256']==hashlib.sha256((PROJECT/'data/gathering-worker.json').read_bytes()).hexdigest()
    for name,sha in owned['owned_source_sha256'].items():assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==sha
    plan=json.loads((PROJECT/'data/gathering-worker.json').read_text())
    action_sha=hashlib.sha256(json.dumps(plan['actions'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    result=compare(native,owned);result.update(source_action_sha256=action_sha,original_guest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        source_plan_sha256=owned['source_plan_sha256'],case_spec_sha256=owned['case_spec_sha256'],owned_source_sha256=owned['owned_source_sha256'],
        source_program_sha256=native['source_program_sha256'],original_dm_construction_verified=False,
        original_cancellation_protocol_verified=False,original_timing_verified=False,sdk_marker_is_synthetic_test_data=True,game_input_sent=False,full_module_restored=False)
    (PROJECT/'verification/gathering-worker-original-vs-rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('ok','cases','external_events','records_covered')}))


if __name__=='__main__':main()
