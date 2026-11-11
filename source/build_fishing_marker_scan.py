"""Infer the post-repair color scan using the retained gathering color ladder."""
import hashlib
import json
import re

from build_fishing_startup import INVENTORY, OUT
from export_fishing_routines import PROJECT, routine_roles, translate_bodies
from qmacro_fishing_retained import FishingRetainedMachine

ENTRY, FALLBACK, JOIN, UNKNOWN, END = 277, 311, 317, 319, 320
BUILTIN = (282, 287, 292, 297)
SEARCHES = (278, *BUILTIN, 302, 307)


def build(raw, gathering, alignment, pool):
    code, strings = raw["code"], raw["strings"]
    reference, reference_strings = gathering["code"], gathering["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    roles = routine_roles(raw)
    rows = []

    def emit(op, operand, **manual):
        at = ENTRY + len(rows)
        assert at in candidate["missing_records"] and code[at][0] == 255
        candidate["missing_records"].remove(at)
        loc, flags = code[at][1], code[at][3]
        candidate["code"][at] = [op, loc, operand, flags]
        if manual:
            row = dict(record=at, location=loc, source_sl=operand, source=strings[operand], **manual)
        else:
            row = translate_bodies(candidate, ((at, at),), roles)[0]
            row.pop("opcode")
        rows.append(dict(row, candidate_opcode=op, field_3=flags, inferred=True))

    def text(sl, **manual):
        assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
        emit(30 if pool[sl]["kind"] == "decoded-text" else 2, sl, **manual)

    def branch(sl, target, **manual):
        emit(4, sl, **manual)
        emit(6, target - (ENTRY + len(rows)))

    def jump(target):
        emit(16, target - (ENTRY + len(rows)))

    def positive(axis):
        return {"gt": [{"role": f"query_{axis}"}, {"const": 0}]}

    # From the first search through the fourth hit jump the retained
    # gathering code has exactly the same record and location deltas.
    for at in range(282, 301):
        assert reference[at + 1074][1] - code[at][1] == 980
    text(229)
    text(230)
    branch(231, FALLBACK)
    text(232)
    for i, (at, color) in enumerate(zip(BUILTIN, ("40752B", "35DF86", "31B972", "3F722A"))):
        sl = 233 + 3 * i
        assert ENTRY + len(rows) == at
        op, _, ref_sl, _ = reference[at + 1074]
        assert op == 30 and f'"{color}"' in reference_strings[ref_sl]
        ref = at + 1074
        assert [row[0] for row in reference[ref:ref + 4]] == [30, 4, 6, 16]
        assert ref + 2 + reference[ref + 2][2] == ref + 4
        assert ref + 3 + reference[ref + 3][2] == 1390
        match = re.fullmatch(r'Call FindColorEx\((\d+),(\d+),(\d+),(\d+),"([A-F0-9]{6})",(\d+),(0\.9),INTX,INTY\)',
                             strings[sl])
        assert match and match[5] == color and strings[sl + 1] == "Sgn(INTX>0 And INTY>0)"
        text(sl, kind="builtin_color", rect=[int(n) for n in match.groups()[:4]],
             color=color, direction=int(match[6]), similarity=float(match[7]))
        branch(sl + 1, at + 4, kind="test", condition={"all": [positive("x"), positive("y")]})
        jump(JOIN)
        text(sl + 2)
    text(245)
    assert strings[246] == "Sgn(INTX>0)"
    branch(246, 306, kind="test", condition=positive("x"))
    jump(JOIN)
    text(247)
    text(248)
    assert strings[249] == "Sgn((INTX>0))"
    branch(249, FALLBACK, kind="test", condition=positive("x"))
    jump(JOIN)
    for sl in (250, 251, 252):
        text(sl)
    branch(253, JOIN)
    for sl in (254, 255, 256):
        text(sl)
    assert ENTRY + len(rows) == UNKNOWN
    rows.append(dict(record=UNKNOWN, location=code[UNKNOWN][1], field_3=code[UNKNOWN][3],
                     source_sl=None, source=None, kind="unresolved_control", candidate_opcode=None, inferred=True))
    cursor = 229
    for group in alignment["groups"]:
        if not ENTRY <= group["records"][0] < END:
            continue
        refs = [rows[at - ENTRY]["source_sl"] for at in group["records"]]
        following = cursor + sum(sl is not None for sl in refs)
        assert any(c["source_range"] == [cursor, following]
                   and [r["source_sl"] for r in c["instructions"]] == refs for c in group["candidates"]), (group["records"], refs)
        cursor = following
    assert cursor == 257
    return dict(module=5, entry=ENTRY, boundary=END, rows=rows, unresolved=[UNKNOWN],
                reference=dict(module=8, records=[1356, 1374], record_delta=1074, location_delta=980),
                sdk_miss_alternatives=[FALLBACK, JOIN], original_values_recovered=0,
                source_program_sha256=alignment["source_sha256"])


def verify(plan, routines, retained):
    cases = []
    outcomes = (*BUILTIN, 302, 307, None, 278)
    for outcome in outcomes:
        for slow in (0, 1):
            for pass_unknown in (False, True):
                context = dict(slow_repair=slow, simulation_mode=0, sdk_marker="AB12CD")
                machine = FishingRetainedMachine(routines, retained, context.get, 0)
                machine.pc = ENTRY
                for row in plan["rows"]:
                    at = row["record"]
                    if at == UNKNOWN:
                        if not pass_unknown:
                            continue
                        row = dict(record=at, kind="jump", target=END)
                    machine.actions[at] = row
                    machine.missing.remove(at)
                events = []
                for _ in range(60):
                    if machine.done:
                        break
                    event = machine.step()
                    events.append(event)
                    at, kind = event["record"], event["kind"]
                    if kind == "find_color":
                        left, top, right, bottom = event["rect"]
                        found = (outcome != 278) if at == 278 else outcome == at
                        if found:
                            try:
                                machine.supply_query(right, bottom, 0)
                            except ValueError:
                                pass
                            else:
                                raise AssertionError("DM unexpectedly accepted the excluded corner")
                        machine.supply_query(left if found else -1, top if found else -1, int(not found))
                    elif kind == "builtin_color":
                        right, bottom = event["rect"][2:]
                        dm_return = machine.values["query_return"]
                        coords = (right, bottom) if outcome == at else (-1, -1)
                        machine.supply_builtin_color(*coords)
                        assert machine.values["query_return"] == dm_return
                records = [e["record"] for e in events]
                queries = [at for at in records if at in SEARCHES]
                expected = SEARCHES[:1] if outcome == 278 else SEARCHES if outcome is None else SEARCHES[:SEARCHES.index(outcome) + 1]
                assert queries == list(expected)
                used_b = outcome in (None, 278)
                assert [e["arguments"][0] for e in events if e["kind"] == "key_press"] == (["B"] if used_b else [])
                assert (316 in records) == (used_b and slow == 1)
                assert machine.done and machine.pc == (END if pass_unknown else UNKNOWN)
                cases.append(dict(first_hit=outcome if outcome != 278 else None, sdk_hit=outcome != 278,
                                  slow_repair=slow, assume_l319_fallthrough=pass_unknown,
                                  records=records, events=events, boundary=machine.pc))
    assert set(at for c in cases for at in c["records"]) & set(range(ENTRY, END)) == set(range(ENTRY, END))
    return dict(cases=cases, steps=sum(len(c["records"]) for c in cases), real_actions_sent=False)


def main():
    source = (PROJECT / "programs/05.json").read_bytes()
    raw = json.loads(source)
    gathering = json.loads((PROJECT / "programs/08.json").read_text("utf8"))
    alignment = json.loads((OUT / "prefix-structured-alignment.json").read_text("utf8"))
    assert hashlib.sha256(source).hexdigest() == alignment["source_sha256"]
    pool = json.loads((INVENTORY / "05-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(raw, gathering, alignment, pool)
    routines, retained = [json.loads((PROJECT / "data" / f"fishing-{name}.json").read_text("utf8"))
                          for name in ("routines", "retained")]
    report = verify(plan, routines, retained)
    for name, data in (("fishing-marker-scan", plan), ("fishing-marker-scan-verification", report)):
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows']) - 1} candidates; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
