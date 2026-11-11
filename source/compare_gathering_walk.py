from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    native_path=PROJECT/'verification/original-gathering-walk.json';raw=native_path.read_bytes();native=json.loads(raw.decode('utf-8-sig'))
    owned=json.loads((PROJECT/'verification/gathering-walk-owned.json').read_text(encoding='utf8'))
    assert native['ok'] and native['case_count']==owned['case_count']==146
    assert native['source_program_sha256']==hashlib.sha256((PROJECT/'programs/08.json').read_bytes()).hexdigest()
    assert native['case_spec_sha256']==owned['case_spec_sha256']==hashlib.sha256((PROJECT/'data/gathering-walk-cases.json').read_bytes()).hexdigest()
    assert owned['source_plan_sha256']==hashlib.sha256((PROJECT/'data/gathering-walk.json').read_bytes()).hexdigest()
    source_root=Path(__file__).resolve().parent
    for name,sha in owned['owned_source_sha256'].items():assert hashlib.sha256((source_root/name).read_bytes()).hexdigest()==sha
    matched=[];event_count=0
    for a,b in zip(native['cases'],owned['cases']):
        assert a['id']==b['id'] and a['records']==b['records'],('instruction path',a['id'])
        assert a['reason']==b['reason'] and a['angle_is_empty']==b['angle_is_empty'],('termination/Empty',a['id'])
        if a['reason']=='numeric_overflow':assert 'scode=800a0006' in a['error_evidence'].lower()
        if a['angle'] is None:assert b['angle'] is None
        else:assert math.isclose(a['angle'],b['angle'],rel_tol=1e-12,abs_tol=1e-10),('angle',a['id'],a['angle'],b['angle'])
        expected=[{'record':e['record'],'kind':e['kind'],'value':e['value']} for e in b['events'] if e['kind'] in ('delay','move_to','mouse_click')]
        actual=[{'record':e['Record'],'kind':e['Kind'],'value':e['Value']} for e in a['events']]
        assert actual==expected,('external events',a['id']);event_count+=len(actual)
        matched.append({'id':a['id'],'records':len(a['records']),'external_events':len(actual),'reason':a['reason'],'angle':a['angle']})
    assert len(matched)==146
    plan=json.loads((PROJECT/'data/gathering-walk.json').read_text(encoding='utf8'))
    action_sha=hashlib.sha256(json.dumps(plan['actions'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    report={'ok':True,'cases':146,'external_events':event_count,'original_records_covered':len({r for c in native['cases'] for r in c['records']}),'source_action_sha256':action_sha,
            'matched':matched,'original_guest_sha256':hashlib.sha256(raw).hexdigest(),'owned_source_sha256':owned['owned_source_sha256'],
            'source_plan_sha256':owned['source_plan_sha256'],'case_spec_sha256':owned['case_spec_sha256'],
            'original_rng_equivalent':False,'original_timing_verified':False,'game_input_sent':False,'full_module_restored':False}
    (PROJECT/'verification/gathering-walk-original-vs-rebuild.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'ok':True,'cases':146,'external_events':event_count,'original_records_covered':report['original_records_covered']}))


if __name__=='__main__':main()
