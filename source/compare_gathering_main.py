import json,hashlib
from pathlib import Path
from compare_gathering_routines import effects as routine_effects
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def effects(case):
    # Reuse the already-verified common effects while including MoveToEx at its
    # original position (its native movement/randomness is intentionally stubbed).
    result=[];chunk=[]
    for event in case['events']:
        if event['kind']=='move_to_ex':
            result+=routine_effects({'events':chunk});chunk=[]
            result.append({'record':event['record'],'kind':'move_to_ex','value':event['arguments']})
        else:chunk.append(event)
    return result+routine_effects({'events':chunk})


def compare(native,owned):
    assert native['ok'] and owned['ok'] and len(native['cases'])==len(owned['cases'])==74
    matched=[];count=0
    for old,new in zip(native['cases'],owned['cases']):
        for key in ('id','records','reason','next_record','main_cycles','query_count','root_current_is_nothing','root_slots','history'):
            assert old[key]==new[key],(old['id'],key,old[key],new[key])
        if old['reason']=='numeric_overflow':assert 'scode=800a0006' in old['error_evidence'].lower()
        expected=effects(new);actual=[{'record':e['Record'],'kind':e['Kind'],'value':e['Value']} for e in old['events'] if e['Kind']!='builtin_color']
        assert actual==expected,('events',old['id'],next(((i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),(len(actual),len(expected))))
        count+=len(actual);matched.append({'id':old['id'],'reason':old['reason'],'records':len(old['records']),'events':len(actual)})
    return {'ok':True,'cases':74,'external_events':count,'matched':matched}


def main():
    path=PROJECT/'verification/original-gathering-main.json';native=json.loads(path.read_text(encoding='utf-8-sig'))
    owned=json.loads((PROJECT/'verification/gathering-main-owned.json').read_text());plan=json.loads((PROJECT/'data/gathering-main-suffix.json').read_text())
    assert native['source_program_sha256']==plan['source_program_sha256']==hashlib.sha256((PROJECT/'programs/08.json').read_bytes()).hexdigest()
    assert native['case_spec_sha256']==owned['case_spec_sha256']==hashlib.sha256((PROJECT/'data/gathering-main-cases.json').read_bytes()).hexdigest()
    assert owned['source_plan_sha256']==hashlib.sha256((PROJECT/'data/gathering-main-suffix.json').read_bytes()).hexdigest()
    for n,sha in owned['owned_source_sha256'].items():assert hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()==sha
    out=compare(native,owned);out.update(source_program_sha256=native['source_program_sha256'],source_plan_sha256=owned['source_plan_sha256'],
        case_spec_sha256=owned['case_spec_sha256'],original_guest_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),owned_source_sha256=owned['owned_source_sha256'],
        covered_root_records=owned['covered_root_records'],uncovered_root_records=owned['uncovered_root_records'],erased_prefix_restored=False,
        original_native_loaded=False,game_input_sent=False,field_3_semantics_verified=False,full_module_restored=False)
    (PROJECT/'verification/gathering-main-original-vs-rebuild.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k in ('ok','cases','external_events','uncovered_root_records')}))


if __name__=='__main__':main()
