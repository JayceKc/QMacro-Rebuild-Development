"""Translate the retained main-loop suffixes with explicit missing targets."""
import hashlib
import json

from export_battle_recovery import CANDIDATES
from export_battle_scan import ROOT_SUFFIX, build_scan
from export_cube_routines import PROJECT, translate


def build_root(module, raw, base):
    control = build_scan(module,raw,base)
    start,last,missing_target = ROOT_SUFFIX[module]
    body = translate(raw,((start,last,'主流程保留尾段'),),range(len(raw['code'])))
    domain = {a['record'] for a in base['actions']+control['actions']}
    tail = {a['record'] for a in body['actions']}
    if tail & domain:
        raise ValueError(('Overlapping root suffix',module))
    external = {a['target'] for a in body['actions'] if 'target' in a}-domain-tail
    if external!={missing_target} or missing_target not in raw['missing_records']:
        raise ValueError(('Unreviewed root suffix boundary',module,external))
    control['actions'].extend(body['actions'])
    control['routines'].extend(body['routines'])
    control['root_entries'] = [start]
    control['root_required_slots'] = [17] if module=='01' else []
    control['original_record_count'] = len(control['actions'])
    control['boundaries'] = {missing_target:'missing_original_record'}
    return control


def main():
    for module in ROOT_SUFFIX:
        program = (PROJECT/f'programs/{module}.json').read_bytes()
        base = (PROJECT/f'data/battle-{module}.json').read_bytes()
        plan = build_root(module,json.loads(program),json.loads(base))
        plan.update(source_program_sha256=hashlib.sha256(program).hexdigest(),
                    base_plan_sha256=hashlib.sha256(base).hexdigest())
        (CANDIDATES/f'battle-root-{module}.json').write_text(
            json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,plan['root_entries'],plan['root_required_slots'],plan['boundaries'])


if __name__=='__main__':
    main()
