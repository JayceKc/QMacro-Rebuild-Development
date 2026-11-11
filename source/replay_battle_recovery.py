"""Prepare bounded observations for the linked awakening, death and tower entries."""
import json

from export_battle_recovery import CANDIDATES, RECOVERY_RANGES
from replay_battle_control import build_cases
from replay_shared_battle import load, replay


def recovery_cases(module, base, control):
    entries = {start for start, _, _ in RECOVERY_RANGES[module]}
    if module == '01':
        entries.add(1007)
    cases = [case for case in build_cases(module, base, control) if case['entry'] in entries]
    for case in list(cases):
        if not case['default_found'] or case['worker_wrapper']:
            continue
        start, end = case['entry'], case['last']
        actions = [a for a in control['actions'] if start <= a['record'] <= end]
        builtins = [a['record'] for a in actions if a['kind'] in ('builtin_picture', 'builtin_color')]
        if start == 742:
            settings = case['shared'] | {'VF39FB5A4B9B5C2A84D6A65757378756D': 2}
            misses = {str(at): -1 for at in (803, 811, *builtins)}
            cases.append(dict(case, label='覺醒-雙重備援未命中', shared=settings, miss_budget=misses))
            cases.extend(dict(case, label=f'覺醒-備援命中-L{at}', shared=settings,
                              miss_budget={k: v for k, v in misses.items() if k != str(at)})
                         for at in builtins)
        elif builtins:
            dm_misses = [a['record'] for a in actions if a['kind'] in ('find_pic', 'find_color')
                         and a['record'] != start + 26]
            cases.extend(dict(case, label=f'塔場-備援命中-L{at}',
                              miss_budget={str(n): -1 for n in dm_misses + builtins if n != at})
                         for at in builtins)
    for i, case in enumerate(cases, 1):
        case['id'] = i
    return cases


def main():
    for module in RECOVERY_RANGES:
        base = load(f'data/battle-{module}.json')
        control = json.loads((CANDIDATES / f'battle-recovery-{module}.json').read_text('utf8'))
        cases = recovery_cases(module, base, control)
        results = [replay(base, case, control) for case in cases]
        expected = {a['record'] for a in control['actions'] if a['kind'] in ('builtin_color', 'builtin_picture')}
        seen = {e['record'] for result in results for e in result['events'] if e['kind'] == 'builtin_query_reply'}
        if expected != seen:
            raise ValueError(('Uncovered builtin queries', module, expected - seen))
        ranges = [[r['entry'], r['last']] for r in base['routines'] + control['routines']]
        spec = dict(cases=cases, ranges=ranges, boundaries=control['boundaries'], synthetic_context=True)
        (CANDIDATES / f'battle-recovery-{module}-cases.json').write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        selected = {at for lo, hi, _ in RECOVERY_RANGES[module] for at in range(lo, hi + 1)}
        observed = {at for result in results for at in result['records']} & selected
        print(module, len(cases), len(observed), sorted(seen))


if __name__ == '__main__':
    main()
