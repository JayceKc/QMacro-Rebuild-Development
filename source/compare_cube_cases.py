"""Compare saved fixed-guest original text paths against the owned cube port."""
import collections,hashlib,json
from pathlib import Path
from export_cube_routines import PROJECT


def effects(case):
    result=[];pending=None
    for e in case['events']:
        k=e['kind'];record=e['record']
        if k in ('find_pic','find_color'):pending=e;continue
        if k=='query_reply':
            assert pending and pending['record']==record
            args=pending['rect']+[pending['spec']]
            if pending['kind']=='find_pic':args.append(pending['delta'])
            args.extend((pending['similarity'],pending['direction']))
            result.append({'record':record,'kind':pending['kind'],'value':{'arguments':args,'x':e['x'],'y':e['y'],'return_value':e['return_value']}});pending=None
        elif k in ('delay','trace','exit_script'):result.append({'record':record,'kind':k,'value':e['arguments'][0]})
        elif k in ('key_press','mouse_click','move_to','os_exit_intent'):result.append({'record':record,'kind':k,'value':e['arguments']})
        elif k=='load_service_intent':result.append({'record':record,'kind':k,'value':e['name']})
    assert pending is None
    return result


def compare(native,owned):
    assert native['ok'] and owned['ok'] and len(native['cases'])==len(owned['cases'])
    matched=[];count=0;covered=set()
    for old,new in zip(native['cases'],owned['cases']):
        for key in ('id','records','reason','next_record','query_count','shared_accesses','final_shared'):
            assert old[key]==new[key],(new['id'],key,old[key] if key!='records' else len(old[key]),new[key] if key!='records' else len(new[key]))
        if new['reason']=='routine_return':assert old['root_frame_restored'] and old['return_is_empty'] and new['frame_restore_requested']
        actual=[{'record':e['Record'],'kind':e['Kind'],'value':e['Value']} for e in old['events']];expected=effects(new)
        assert actual==expected,('effects',new['id'],next(((a,b) for a,b in zip(actual,expected) if a!=b),(len(actual),len(expected))))
        count+=len(expected);covered.update(new['records']);matched.append({'id':new['id'],'records':len(new['records']),'events':len(expected),'reason':new['reason']})
    return {'ok':True,'cases':len(matched),'external_events':count,'covered_records':sorted(covered),'records_covered':len(covered),'matched':matched}


def main():
    np=PROJECT/'verification/original-cube-routines.json';op=PROJECT/'verification/cube-owned.json'
    native=json.loads(np.read_text('utf-8-sig'));owned=json.loads(op.read_text('utf8'))
    assert native['case_spec_sha256']==owned['case_spec_sha256']==hashlib.sha256((PROJECT/'data/cube-cases.json').read_bytes()).hexdigest()
    assert native['source_program_sha256']==owned['source_program_sha256']==hashlib.sha256((PROJECT/'programs/07.json').read_bytes()).hexdigest()
    assert owned['source_plan_sha256']==hashlib.sha256((PROJECT/'data/cube-routines.json').read_bytes()).hexdigest()
    for name,sha in owned['owned_source_sha256'].items():assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==sha
    result=compare(native,owned)
    plan=json.loads((PROJECT/'data/cube-routines.json').read_text('utf8'));by={a['record']:a for a in plan['actions']};edges=collections.defaultdict(set)
    for case in native['cases']:
        for at,nxt in zip(case['records'],case['records'][1:]):edges[at].add(nxt)
    branches=[]
    for a in plan['actions']:
        if a['kind']!='if_zero':continue
        at=a['record'];constant=by[at-1]['source'].lower().replace(' ','')=='sgn(vbtrue)'
        expected={at+1} if constant else {at+1,a['target']}
        assert edges[at]==expected,('conditional edge coverage',at,edges[at],expected)
        branches.append({'record':at,'source_condition_record':at-1,'observed_successors':sorted(edges[at]),'constant_true':constant})
    result.update(conditional_branches=branches,conditional_edges=sum(len(b['observed_successors']) for b in branches),
                  op31_uses_owned_library_provider=True,
                  guest_fixture_source_sha256={n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ('QMacroCubeGuestTest.cs','CubeDigests.cs','Build-CubeGuestFixture.ps1','Run-CubeGuestTest.ps1')})
    result.update(source_program_sha256=native['source_program_sha256'],case_spec_sha256=native['case_spec_sha256'],
                  source_action_sha256=hashlib.sha256(json.dumps(json.loads((PROJECT/'data/cube-routines.json').read_text('utf8'))['actions'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest(),
                  original_guest_sha256=hashlib.sha256(np.read_bytes()).hexdigest(),owned_source_sha256=owned['owned_source_sha256'],
                  frame_restoration_for_explicit_null_parent_verified=True,full_frame_lifecycle_verified=False,
                  original_native_loaded=False,game_input_sent=False,system_exit_executed=False,original_rng_equivalent=False,original_timing_verified=False,full_module_restored=False)
    (PROJECT/'verification/cube-original-vs-rebuild.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('ok','cases','external_events','records_covered')}))


if __name__=='__main__':main()
