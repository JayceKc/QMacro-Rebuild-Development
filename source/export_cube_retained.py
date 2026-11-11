"""Cover the remaining original records and inventory the full retained graph."""
import hashlib
import itertools
import json
import re

from export_cube_routines import ARRAY, FRAME, PROJECT, translate


def build(raw, main, workers):
    base = main['actions'] + workers['actions']
    occupied = {a['record'] for a in base}
    if len(occupied) != len(base):
        raise ValueError('Overlapping retained plans')
    missing = set(raw['missing_records'])
    retained = set(range(len(raw['code']))) - missing
    if not occupied <= retained or raw['callbacks']:
        raise ValueError('Retained domain or callbacks changed')
    residue = retained - occupied
    special = set(range(31)) | {6816,6817,6819}
    spans = []
    for _, group in itertools.groupby(enumerate(sorted(residue-special)),lambda item:item[1]-item[0]):
        indices = [item[1] for item in group]
        spans.append((indices[0],indices[-1],'保留銜接'))
    translated = translate(raw,spans,set(range(len(raw['code']))))['actions']
    auxiliary = 'F2730835_2229_445E_97C7_13F76l277lDA'
    declaration = f'Dim {ARRAY}(256):Dim {FRAME},{auxiliary}:Set {FRAME}=Nothing:Set {auxiliary}=Nothing'
    for at in sorted(special):
        op,loc,arg,flags = raw['code'][at]
        source = raw['strings'][arg] if op in (30,33,35) else None
        action = dict(record=at,opcode=op,location=loc,operand=arg,field_3=flags,
                      source_sl=arg if source is not None else None,source=source)
        if at==0 and op==30 and source==declaration:
            action['kind']='declare_root'
        elif 1<=at<=29 and op==30 and re.fullmatch(r'Class [A-Za-z_0-9]+:Dim [A-Za-z_0-9]+,[A-Za-z_0-9]+,[A-Za-z_0-9]+\(256\):End Class',source):
            action['kind']='declare_class'
        elif at==30 and op==29:
            action['kind']='entry_dispatch'
        elif at in (6816,6817) and op==(33 if at==6816 else 35) and source=='Form1':
            action['kind']='runner_message' if at==6816 else 'ui_pump'
        elif at==6819 and op==22:
            action['kind']='final_record'
        else:
            raise ValueError(('Unreviewed retained scaffold',at,op,source))
        translated.append(action)
    if {a['record'] for a in translated}!=residue:
        raise ValueError('Residual coverage differs')
    edges = []
    for action in base+translated:
        at = action['record']
        if raw['code'][at]!=[action[k] for k in ('opcode','location','operand','field_3')]:
            raise ValueError(('Original tuple changed',at))
        if action['source_sl'] is not None and raw['strings'][action['source_sl']]!=action['source']:
            raise ValueError(('Original text changed',at))
        if 'target' in action:
            target = action['target']
            if target not in retained|missing:
                raise ValueError(('Invalid original target',at,target))
            edges.append(dict(record=at,target=target,kind=action['kind'],target_missing=target in missing))
    return dict(schema=1,module=7,total_records=len(raw['code']),retained_records=len(retained),
                missing_records=sorted(missing),actions=sorted(translated,key=lambda a:a['record']),
                explicit_edges=sorted(edges,key=lambda a:a['record']),saved_callbacks=[],
                full_module_restored=False,original_thread_timing_verified=False)


def main():
    def load(name):
        return json.loads((PROJECT/name).read_text('utf8'))
    inputs = ('programs/07.json','data/cube-main.json','data/cube-workers.json')
    plan = build(*(load(name) for name in inputs))
    plan['input_sha256'] = {name:hashlib.sha256((PROJECT/name).read_bytes()).hexdigest() for name in inputs}
    (PROJECT/'data/cube-retained-tail.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'new_records':len(plan['actions']),'retained_records':plan['retained_records'],
                      'missing_edges':[edge for edge in plan['explicit_edges'] if edge['target_missing']]}))


if __name__ == '__main__':
    main()
