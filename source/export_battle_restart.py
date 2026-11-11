"""Link the three retained restart entries and their screenshot helpers."""
import hashlib
import json

from export_battle_control import build
from export_battle_recovery import CANDIDATES, RECOVERY_RANGES
from export_cube_routines import PROJECT


RESTART_RANGES = {
    '01': ((11725,11873,'重新啟動'),(13605,13609,'擷取畫面')),
    '03': ((5885,6011,'重新啟動'),(6457,6461,'擷取畫面')),
    '06': ((8621,8752,'重新啟動'),(10289,10293,'擷取畫面')),
}


def build_restart(module, raw, base):
    plan = build(module, raw, base, RECOVERY_RANGES[module]+RESTART_RANGES[module])
    if plan['boundaries']:
        raise ValueError(('Unexpected linked restart boundary',module,plan['boundaries']))
    plan['name'] = '戰鬥啟停、覺醒、死亡處理、塔場與重新啟動'
    plan['scope'] = 'Linked retained routines. Capture and restart are recorded requests.'
    return plan


def main():
    CANDIDATES.mkdir(exist_ok=True)
    for module,ranges in RESTART_RANGES.items():
        program = (PROJECT/f'programs/{module}.json').read_bytes()
        base = (PROJECT/f'data/battle-{module}.json').read_bytes()
        plan = build_restart(module,json.loads(program),json.loads(base))
        plan.update(source_program_sha256=hashlib.sha256(program).hexdigest(),
                    base_plan_sha256=hashlib.sha256(base).hexdigest())
        (CANDIDATES/f'battle-restart-{module}.json').write_text(
            json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(module,sum(last-first+1 for first,last,_ in ranges),len(plan['actions']))


if __name__=='__main__':
    main()
