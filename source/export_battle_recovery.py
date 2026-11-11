"""Translate the retained awakening, death and tower entries into a linked candidate."""
import hashlib
import json
from pathlib import Path

from export_battle_control import build
from export_cube_routines import PROJECT


RECOVERY_RANGES = {
    '01': ((742, 836, '覺醒'), (838, 1018, '死亡處理'), (6783, 7704, '塔場')),
    '03': ((417, 525, '死亡處理'),),
    '06': ((6620, 7541, '塔場'),),
}
RESTART = {'01': 11725, '03': 5885, '06': 8621}
CANDIDATES = Path(__file__).with_name('battle-recovery-candidates')


def build_recovery(module, raw, base):
    plan = build(module, raw, base, RECOVERY_RANGES[module])
    if plan['boundaries'] != {RESTART[module]: 'untranslated_call'}:
        raise ValueError(('Unexpected recovery boundary', module, plan['boundaries']))
    plan['name'] = '戰鬥啟停、覺醒、死亡處理與塔場'
    plan['scope'] = 'Linked translation with explicit builtin observations and recorded log intents.'
    return plan


def main():
    CANDIDATES.mkdir(exist_ok=True)
    for module, ranges in RECOVERY_RANGES.items():
        program = (PROJECT / f'programs/{module}.json').read_bytes()
        base = (PROJECT / f'data/battle-{module}.json').read_bytes()
        plan = build_recovery(module, json.loads(program), json.loads(base))
        plan.update(source_program_sha256=hashlib.sha256(program).hexdigest(),
                    base_plan_sha256=hashlib.sha256(base).hexdigest())
        path = CANDIDATES / f'battle-recovery-{module}.json'
        path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        print(module, sum(end - start + 1 for start, end, _ in ranges), plan['boundaries'])


if __name__ == '__main__':
    main()
