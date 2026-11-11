"""Join preserved cube parent, button/ALTQ helpers and the three proven bodies."""
import hashlib,json,re
from export_cube_routines import ARRAY, FRAME, PROJECT, RANGES, TEMP, translate

JOINED=((1677,3363,'魔方上層保留流程'),(3365,3486,'找按鈕'),(6657,6689,'檢查新舊ALTQ'))+RANGES


def build(raw):
    p = translate(raw, JOINED)
    by = {a['record']: a for a in p['actions']}
    calls = []
    for a in p['actions']:
        if a['kind'] != 'call':
            continue
        setup = by[a['record'] - 1]
        store = by[a['record'] + 1]
        if setup['kind'] != 'frame_enter' or store['kind'] != 'assign_slot' or store['value'] != {'temporary': True}:
            raise ValueError(('Unreviewed call protocol', a['record']))
        declaration = next((s for s in raw['strings'] if s.startswith('Class ' + setup['class_name'] + ':')), '')
        fields = re.fullmatch(r'Class [A-Za-z_0-9]+:Dim ([A-Za-z_0-9]+),([A-Za-z_0-9]+),([A-Za-z_0-9]+)\(256\):End Class', declaration)
        if fields is None or fields[1] != setup['parent_field'] or fields[3] != ARRAY:
            raise ValueError(('Unreviewed frame class', a['record']))
        end = next(last for entry, last, _ in JOINED if entry == a['target'])
        restore = by[end - 1]
        temp_object = 'F2730835_2229_445E_97C7_13F76l277lDA'
        expected = (f'{TEMP}={FRAME}.{fields[2]}:Set {temp_object}={FRAME}:'
                    f'Set {FRAME}={FRAME}.{fields[1]}:Set {temp_object}=Nothing')
        if restore['source'] != expected or by[end]['kind'] != 'return':
            raise ValueError(('Unreviewed frame restoration', a['target']))
        calls.append({'record': a['record'], 'target': a['target'], 'return_pc': a['record'] + 1,
                      'frame_setup_record': setup['record'], 'frame_restore_record': restore['record'],
                      'frame_class': setup['class_name'], 'class_declaration': declaration,
                      'return_slot': store['slot'], 'return_field': fields[2]})
    p.update(name='魔方上層與五個子程序銜接',joined_calls=calls,controlled_entry=1677,
             original_body_guest_verified=False,full_frame_lifecycle_verified=False,
             original_timing_verified=False,real_worker_control_verified=False,
             dm_creation_policy='An explicit create_dm_intent, never original CreateObject on host.')
    return p


def main():
    path=PROJECT/'programs/07.json';p=build(json.loads(path.read_text('utf8')));p['source_program_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    (PROJECT/'data/cube-main.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':len(p['actions']),'calls':len(p['joined_calls']),'new_parent_and_helper_records':1842}))


if __name__=='__main__':main()
