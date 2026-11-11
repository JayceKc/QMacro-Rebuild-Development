"""Account for all preserved module05 records and their real missing targets."""
import hashlib
import json

from export_fishing_routines import PROJECT, routine_roles, translate_bodies


SUFFIX = (504,539)
SUFFIX_ROLES = {'V8B92AAD77378756D':'failure_count','V859CB696C584756D':'rebait','CS':'cycle_count'}
HOST = {0:'declaration',1:'declaration',2:'declaration',3:'entry_dispatch',
        540:'jump',878:'jump',924:'jump',925:'runner_message',926:'ui_pump',927:'iteration_end',928:'final_record'}


def build(program, routines):
    code = program['code']
    roles = routine_roles(program)|SUFFIX_ROLES
    actions = translate_bodies(program,(SUFFIX,),roles)
    for at,kind in HOST.items():
        op,loc,arg,flags = code[at]
        source = program['strings'][arg] if op in (30,33,35) else None
        action = dict(record=at,opcode=op,location=loc,source_sl=arg if source is not None else None,source=source,kind=kind)
        if kind=='jump':
            if op!=16:
                raise ValueError(('Unexpected host jump',at))
            action['target'] = at+arg
        else:
            expected = {'declaration':30,'entry_dispatch':29,'runner_message':33,'ui_pump':35,
                        'iteration_end':23,'final_record':22}
            if op!=expected[kind]:
                raise ValueError(('Unexpected host operation',at))
        actions.append(action)
    actions = sorted([dict(a) for a in routines['actions']]+actions,key=lambda a:a['record'])
    missing = set(program['missing_records'])
    ids = [a['record'] for a in actions]
    if len(ids)!=len(set(ids)) or set(ids)!=set(range(len(code)))-missing:
        raise ValueError('Fishing retained coverage differs')
    for a in actions:
        op,loc,arg,flags = code[a['record']]
        a.update(operand=arg,field_3=flags)
    suffix_targets = {a['target'] for a in actions if SUFFIX[0]<=a['record']<=SUFFIX[1] and 'target' in a}
    if suffix_targets & missing != {115,501}:
        raise ValueError('Fishing suffix boundary changed')
    return dict(module=5,actions=actions,missing_records=sorted(missing),total_records=len(code),
                original_record_count=len(actions),suffix_roles=SUFFIX_ROLES,
                source_program_sha256=routines['source_program_sha256'],full_module_restored=False)


def main():
    program = PROJECT/'programs/05.json'
    base = PROJECT/'data/fishing-routines.json'
    retained = build(json.loads(program.read_text('utf8')),json.loads(base.read_text('utf8')))
    assert retained['source_program_sha256']==hashlib.sha256(program.read_bytes()).hexdigest()
    retained['routine_plan_sha256'] = hashlib.sha256(base.read_bytes()).hexdigest()
    (PROJECT/'data/fishing-retained.json').write_text(json.dumps(retained,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(len(retained['actions']),len(retained['missing_records']))


if __name__=='__main__':
    main()
