"""Reconstruct and replay the first fishing catch and completion branches."""
from collections import Counter
import hashlib
import json
import re

from build_fishing_startup import INVENTORY, OUT
from export_fishing_routines import PROJECT, routine_roles, translate_bodies
from qmacro_fishing_retained import FishingRetainedMachine

ENTRY, END, HOME = 115, 204, 879
OPAQUE = (116, 139)


def build(raw, alignment, pool):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    manual = {}
    pc = ENTRY

    def emit(op, arg, **override):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["code"][pc] = [op, code[pc][1], arg, code[pc][3]]
        candidate["missing_records"].remove(pc)
        if override:
            manual[pc] = override
        pc += 1

    def text(sl, **override):
        assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
        emit(30 if pool[sl]["kind"] == "decoded-text" else 2, sl, **override)

    def texts(lo, hi):
        for sl in range(lo, hi):
            text(sl)

    def jump(target):
        emit(16, target - pc)

    def test(sl, target, **override):
        emit(4, sl, **override)
        emit(6, target - pc)

    def unknown():
        nonlocal pc
        assert pc in OPAQUE
        pc += 1

    def home(sl, slot):
        assert strings[sl] == strings[code[785][2]] == strings[code[803][2]]
        assert code[786][0:3:2] == code[804][0:3:2] == [12, HOME]
        text(sl, kind="frame_enter", name="return_home")
        emit(12, HOME)
        retained_store = strings[code[787 if slot == 1 else 805][2]]
        assert strings[sl + 1] == retained_store.split(".", 1)[1]
        text(sl + 1, kind="store_return", slot=slot)

    roles = routine_roles(raw) | {"CS": "cycle_count", strings[112].split("=")[0]: "catch_count"}
    for sl, role in ((114, "stop_at_80"), (120, "complete_at_80")):
        key = re.fullmatch(r"Sgn\((V[A-F0-9]+)=1 and (V[A-F0-9]+)=80\)", strings[sl])
        assert key and roles[key[2]] == "catch_count"
        roles[key[1]] = role

    def at_eighty(sl, target, role):
        condition = {"all": [{"equals": [{"role": role}, {"const": 1}]},
                             {"equals": [{"role": "catch_count"}, {"const": 80}]}]}
        test(sl, target, kind="test", condition=condition)

    text(95)
    unknown()
    test(96, 121)
    text(97)
    jump(131)
    texts(98, 101)
    test(101, 129)
    texts(102, 106)
    jump(ENTRY)
    texts(106, 114)
    unknown()
    assert pc == 140
    at_eighty(114, 146, "stop_at_80")
    texts(115, 120)
    at_eighty(120, END, "complete_at_80")
    text(121)
    test(122, 157)
    texts(123, 127)
    jump(END)
    for condition, next_mode, slot in ((127, 175, 1), (141, 193, 2)):
        test(condition, next_mode)
        text(condition + 1)
        test(condition + 2, pc + 6)
        text(condition + 3)
        home(condition + 4, slot)
        texts(condition + 6, condition + 14)
        jump(END)
    test(155, END)
    texts(156, 164)
    jump(END)
    assert pc == END

    rows = []
    for at in range(ENTRY, END):
        op, loc, arg, flags = candidate["code"][at]
        if at in OPAQUE:
            row = dict(record=at, location=loc, source_sl=None, source=None, kind="unresolved_control")
        elif at in manual:
            row = dict(record=at, location=loc, source_sl=arg, source=strings[arg], **manual[at])
        else:
            row = translate_bodies(candidate, ((at, at),), roles)[0]
            row.pop("opcode")
        row.update(candidate_opcode=op if at not in OPAQUE else None, field_3=flags, inferred=True)
        rows.append(row)
    assert Counter(r["source_sl"] for r in rows if r["source_sl"] is not None) == Counter(range(95, 164))
    cursor = 95
    for g in alignment["groups"]:
        if not ENTRY <= g["records"][0] < END:
            continue
        refs = [rows[at - ENTRY]["source_sl"] for at in g["records"]]
        following = cursor + sum(sl is not None for sl in refs)
        assert any(c["source_range"] == [cursor, following]
                   and [r["source_sl"] for r in c["instructions"]] == refs for c in g["candidates"]), (g["records"], refs)
        cursor = following
    assert cursor == 164 and code[539][0:3:2] == [5, ENTRY]
    return dict(module=5, entry=ENTRY, boundary=END, rows=rows, unresolved=list(OPAQUE),
                retained_restart=539, retained_home=[785, 786, 803, 804, HOME],
                alternative_first_query_record=116,
                source_program_sha256=alignment["source_sha256"], original_values_recovered=0)


def verify(plan, routines, retained):
    reports = []
    scenarios = [(0, 0, 0, 0, 0, 0, None), (0, 0, 0, 0, 0, 0, 139)]
    scenarios += [(79, 0, 1, 1, mode, home, False) for mode in range(5) for home in range(2)]
    scenarios += [(79, 0, 1, 0, mode, home, False) for mode in range(5) for home in range(2)]
    scenarios += [(count, cycles, 1, 1, 1, 0, False)
                  for count in (78, 80) for cycles in (264, 265, 266)]
    scenarios.append((77, 0, 0, 0, 0, 0, False))
    for count, cycles, complete, stop, mode, home, boundary in scenarios:
        misses = 266 if count == 77 else int(bool(cycles))
        context = dict(completion_mode=mode, return_home=home, simulation_mode=0, sdk_marker="AB12CD")
        machine = FishingRetainedMachine(routines, retained, context.get, 0)
        machine.pc = ENTRY
        machine.frames.append({"slots": {}, "value": None})
        machine.values.update(catch_count=count, cycle_count=cycles, complete_at_80=complete, stop_at_80=stop)
        for row in plan["rows"]:
            at = row["record"]
            if at in OPAQUE:
                if boundary is not None and boundary != at:
                    machine.actions[at] = dict(kind="jump", target=at + 1)
                    machine.missing.remove(at)
                continue
            machine.actions[at] = row
            machine.missing.remove(at)
        events, finds = [], 0
        for _ in range(3000):
            if machine.done:
                break
            event = machine.step()
            events.append(event)
            if event["kind"] in ("find_color", "find_pic"):
                at = event["record"]
                if at == ENTRY:
                    finds += 1
                x, y = event["rect"][:2]
                found = at != ENTRY or finds > misses
                machine.supply_query(x + 1 if found else -1, y + 1 if found else -1, int(not found))
        records = [e["record"] for e in events]
        assert machine.done, (count, cycles, complete, stop, mode, home, records[-30:])
        if boundary is not False:
            assert machine.pc == (116 if boundary is None else boundary)
        else:
            keys = [e["arguments"][0] for e in events if e["kind"] == "key_press"]
            completion_key = {1: "F10", 2: "F8", 3: "F6"}.get(mode) if count == 79 and not stop else None
            assert [key for key in keys if key in ("F10", "F8", "F6")] == ([completion_key] * 2 if completion_key else [])
            assert [key for key in keys if key == "E"] == ["E", "E"]
            assert machine.values["catch_count"] == count + 1
            assert finds == misses + 1
            expected_retry_count = cycles + misses
            assert records.count(126) == int(expected_retry_count >= 266)
            assert machine.values["cycle_count"] == (0 if expected_retry_count >= 266 else expected_retry_count)
            assert (HOME in records) == (completion_key in ("F10", "F8") and bool(home))
            if HOME in records:
                assert (165 if mode == 1 else 183) in records
            if count == 79 and (stop or mode < 4):
                assert machine.reason == "script_stop"
            else:
                assert machine.pc == END and machine.reason == "missing_original_record"
        reports.append(dict(start_count=count, start_cycles=cycles, complete=complete, stop=stop,
                            mode=mode, home=home, first_query_misses=misses, unresolved_stop=boundary, records=records,
                            reason=machine.reason, next_record=machine.pc))
    return dict(cases=reports, steps=sum(len(c["records"]) for c in reports), real_actions_sent=False)


def main():
    source = (PROJECT / "programs/05.json").read_bytes()
    raw = json.loads(source)
    alignment = json.loads((OUT / "prefix-structured-alignment.json").read_text("utf8"))
    assert hashlib.sha256(source).hexdigest() == alignment["source_sha256"]
    pool = json.loads((INVENTORY / "05-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(raw, alignment, pool)
    routines, retained = [json.loads((PROJECT / "data" / f"fishing-{name}.json").read_text("utf8"))
                          for name in ("routines", "retained")]
    report = verify(plan, routines, retained)
    for name, data in (("fishing-catch", plan), ("fishing-catch-verification", report)):
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows']) - len(OPAQUE)} candidates; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
