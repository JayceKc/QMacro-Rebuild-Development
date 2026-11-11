"""Join each preserved record with a translated action or an explicit host operation."""
import hashlib
import json
import re

from export_battle_recovery import CANDIDATES
from export_battle_root import build_root
from export_battle_scan import ROOT_SUFFIX, SCAN_RANGES, build_scan, inventory
from export_cube_routines import FRAME, FRAME_RETURN, PROJECT, TEMP


def host_action(row):
    at, op, arg = (row[key] for key in ('record','opcode','operand'))
    source = row.get('source')
    action = dict(row,source=source,source_sl=arg if source is not None else None)
    if row['kind']=='form_callback':
        if op==2 and source.startswith('Set ') and '::Set ' in source:
            match = re.fullmatch(
                r'Set (\w+)=New (\w+)::Set \1\.(\w+)='+re.escape(FRAME)+r':Set '+re.escape(FRAME)+r'=\1',
                source)
            if not match:
                raise ValueError(('Unknown callback frame',at))
            action.update(kind='callback_frame_enter',class_name=match[2],parent_field=match[3])
        elif op==31 and source=='FILE\nIf IsEmpty(FILE) Then Set FILE=CreateObject("QMPlugin.File")':
            action.update(kind='load_service_intent',name='FILE')
        elif op==30 and (match:=re.fullmatch(r'Call FILE\.DELETEFOLDER\("([^"]+)"\)',source)):
            action.update(kind='delete_folder_intent',path=match[1])
        elif op==30 and (match:=re.fullmatch(r'Call QMLibrary\.MessageNotify\((\d+),"([^"]+)"\)',source)):
            action.update(kind='message_notify',level=int(match[1]),message=match[2])
        elif op==2 and source.startswith(f'{TEMP}={FRAME}.{FRAME_RETURN}:Set ') and source.endswith('=Nothing'):
            action['kind'] = 'frame_restore_intent'
        elif op==13:
            action['kind'] = 'return'
        else:
            raise ValueError(('Unknown callback record',at,op,source))
    elif op==30 and row['kind']=='declaration_or_dispatch' and source.startswith(('Dim ','Class ')):
        action['kind'] = 'declaration'
    elif op in (29,16,23,22,33,35):
        kinds = {29:'entry_dispatch',16:'jump',23:'iteration_end',22:'final_record',33:'runner_message',35:'ui_pump'}
        action['kind'] = kinds[op]
        if op in (33,35) and source!='Form1':
            raise ValueError(('Unexpected form name',at,source))
    else:
        raise ValueError(('Unknown host record',at,op))
    return action


def build_retained(module, raw, base):
    control = (build_root if module in ROOT_SUFFIX else build_scan)(module,raw,base)
    rest = inventory(module,raw,base,control)['records']
    host = [host_action(row) for row in rest]
    control['actions'].extend(host)
    control['host_records'] = [a['record'] for a in host]
    control['original_record_count'] = len(control['actions'])
    missing = set(raw['missing_records'])
    control['boundaries'] = dict.fromkeys(sorted(missing),'missing_original_record')
    control['total_records'] = len(raw['code'])
    control['form_gate'] = next(a['record'] for a in host if a['kind']=='runner_message')
    control['callbacks'] = raw['callbacks']
    seen = [a['record'] for a in base['actions']+control['actions']]
    if len(seen)!=len(set(seen)) or set(seen)|missing!=set(range(len(raw['code']))) or set(seen)&missing:
        raise ValueError(('Retained coverage differs',module))
    if {w['start_record'] for w in control['worker_wrappers']}!={w['record'] for w in raw['worker_starts']}:
        raise ValueError(('Retained worker coverage differs',module))
    return control


def main():
    for module in SCAN_RANGES:
        program = (PROJECT/f'programs/{module}.json').read_bytes()
        base = (PROJECT/f'data/battle-{module}.json').read_bytes()
        raw, base_plan = json.loads(program),json.loads(base)
        plan = build_retained(module,raw,base_plan)
        plan.update(source_program_sha256=hashlib.sha256(program).hexdigest(),
                    base_plan_sha256=hashlib.sha256(base).hexdigest())
        (CANDIDATES/f'battle-retained-{module}.json').write_text(
            json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,len(plan['actions'])+len(base_plan['actions']),len(plan['boundaries']))


if __name__=='__main__':
    main()
