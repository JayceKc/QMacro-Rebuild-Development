"""Reconstruct the repeated fishing finish loops against retained mode 5."""
import hashlib
import json

from build_fishing_catch import build as build_catch
from build_fishing_marker_scan import build as build_scan
from build_fishing_repair_dispatch import build as build_repair
from build_fishing_startup import INVENTORY, OUT, build as build_startup, replay as replay_startup
from export_fishing_routines import PROJECT, routine_roles, translate_bodies
from qmacro_fishing_retained import FishingRetainedMachine

GATES = (320, 344, 379, 414, 442, 498)
SL_GATES = (257, 274, 300, 326, 347, 396)
END, JOIN = 504, 526


def build(raw, alignment, pool, gathering):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    roles = routine_roles(raw) | {strings[264].split("=")[0]: "failure_count"}
    rows = []

    def emit(op, operand, **manual):
        at = GATES[0] + len(rows)
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

    def texts(lo, hi):
        for sl in range(lo, hi):
            text(sl)

    def edge(op, target):
        emit(op, target - (GATES[0] + len(rows)))

    def branch(sl, target):
        emit(4, sl)
        edge(6, target)

    for mode, (base, sl) in enumerate(zip(GATES, SL_GATES)):
        assert base == GATES[0] + len(rows)
        assert strings[sl].endswith(f"={mode})")
        next_gate = GATES[mode + 1] if mode < 5 else 525
        branch(sl, next_gate)
        text(sl + 1)
        loop, tail = base + 3, next_gate - 3
        assert strings[sl + 2] == "Sgn(vbTrue)"
        branch(sl + 2, tail + 2 if mode < 5 else 524)
        text(sl + 3)
        if mode == 5:
            assert GATES[0] + len(rows) == END and strings[sl + 4] == strings[code[END][2]]
            break

        text(sl + 4)
        branch(sl + 5, base + 12)
        texts(sl + 6, sl + 8)
        edge(16, tail + 2)
        texts(sl + 8, sl + 11)
        branch(sl + 11, tail)
        # Mode 5 retains the entire observation and failure-count sequence.
        for at in range(base + 6, base + 17):
            row = rows[at - GATES[0]]
            ref = code[at - base + 498]
            assert row["candidate_opcode"] == ref[0]
            assert row["location"] - code[base + 6][1] == ref[1] - code[504][1]
            if row["source_sl"] is not None:
                assert row["source"] == strings[ref[2]]

        if mode in (1, 2):
            text(sl + 12)
            branch(sl + 13, base + 24)
            text(sl + 14)
            assert strings[sl + 15] == strings[code[785][2]] == strings[code[803][2]]
            assert code[786][0:3:2] == code[804][0:3:2] == [12, 879]
            text(sl + 15, kind="frame_enter", name="return_home")
            emit(12, 879)
            text(sl + 16, kind="store_return", slot=mode)
            texts(sl + 17, SL_GATES[mode + 1] - 1)
        else:
            texts(sl + 12, SL_GATES[mode + 1] - 1)
        assert GATES[0] + len(rows) == tail
        text(SL_GATES[mode + 1] - 1)
        edge(16, loop)
        edge(16, JOIN)

    assert GATES[0] + len(rows) == END
    cursor = SL_GATES[0]
    same_location_pairs = []
    ref = gathering["code"][1460:1462]
    assert [r[0] for r in ref] == [16, 16] and ref[0][1] == ref[1][1]
    assert ref[0][2] < 0 < ref[1][2]
    for group in alignment["groups"]:
        if not GATES[0] <= group["records"][0] < END:
            continue
        refs = [rows[at - GATES[0]]["source_sl"] for at in group["records"]]
        following = cursor + sum(sl is not None for sl in refs)
        if len(refs) == 2 and refs == [None, None]:
            pair = [rows[at - GATES[0]] for at in group["records"]]
            assert [r["candidate_opcode"] for r in pair] == [16, 16]
            assert pair[0]["target"] < pair[0]["record"] < pair[1]["target"]
            same_location_pairs.append(group["records"])
            continue
        assert any(c["source_range"] == [cursor, following]
                   and [r["source_sl"] for r in c["instructions"]] == refs for c in group["candidates"]), (group["records"], refs)
        cursor = following
    assert cursor == 400
    return dict(module=5, entry=GATES[0], boundary=END, rows=rows, mode_gates=GATES,
                retained_loop=[504, 524], retained_rebait=[526, 539],
                extra_template=dict(module=8, reference=[1460, 1461], candidate_pairs=same_location_pairs),
                source_program_sha256=alignment["source_sha256"], original_values_recovered=0)


def verify(plan, routines, retained):
    cases = []
    specs = [(mode, misses, rebait, home) for mode in range(6) for misses in (0, 2, 5)
             for rebait, home in ((0, 0), (1, 1))]
    specs.append((6, 0, 1, 0))
    for mode, misses, rebait, home in specs:
        context = dict(completion_mode=mode, return_home=home, simulation_mode=0,
                       sdk_marker="AB12CD", saved_cursor_x=314, saved_cursor_y=256)
        machine = FishingRetainedMachine(routines, retained, context.get, 0)
        machine.pc = plan["entry"]
        machine.frames.append({"slots": {}, "value": None})
        machine.values.update(rebait=rebait, cycle_count=13, failure_count=0)
        for row in plan["rows"]:
            machine.actions[row["record"]] = row
            machine.missing.remove(row["record"])
        events, observed = [], 0
        query_at = GATES[mode] + 6 if mode < 6 else None
        for _ in range(300):
            if machine.done:
                break
            event = machine.step()
            events.append(event)
            if event["kind"] in ("find_color", "find_pic"):
                at = event["record"]
                if at == query_at:
                    observed += 1
                x, y = event["rect"][:2]
                hit = at != query_at or observed > misses
                machine.supply_query(x + 1 if hit else -1, y + 1 if hit else -1, int(not hit))
        records = [e["record"] for e in events]
        keys = [e["arguments"][0] for e in events if e["kind"] == "key_press" and e["record"] < 541]
        if misses < 5:
            assert machine.reason == "missing_original_record" and machine.pc == 115 and 539 in records
            assert keys == (["S", "E"] if rebait else ["E"])
            assert machine.values["cycle_count"] == 0 and machine.values["failure_count"] == 0
            assert observed == (misses + 1 if mode < 6 else 0)
        else:
            assert machine.reason == "script_stop" and observed == 5
            assert machine.values["failure_count"] == 5 and 539 not in records
            expected = {1: ["F10", "F10"], 2: ["F8", "F8"], 3: ["F6", "F6"], 4: ["Enter"]}
            assert keys == expected.get(mode, [])
        assert (879 in records) == (misses == 5 and mode in (1, 2) and home == 1)
        assert any(e["kind"] == "os_exit_intent" for e in events) == (misses == 5 and mode == 5)
        cases.append(dict(mode=mode, misses=misses, rebait=rebait, home=home, records=records,
                          keys=keys, reason=machine.reason, next_record=machine.pc))
    return dict(cases=cases, steps=sum(len(c["records"]) for c in cases),
                real_actions_sent=False, os_exit_called=False)


def verify_joined(raw, gathering, alignment, pool, plan, routines, retained):
    startup = build_startup(raw, alignment, pool, alignment["source_sha256"])
    parts = [build_catch(raw, alignment, pool), build_repair(raw, alignment, pool),
             build_scan(raw, gathering, alignment, pool), plan]
    rows = [row for part in parts for row in part["rows"]]
    assert [row["record"] for row in startup["rows"] + rows] == list(range(4, 504))
    results = []
    for mode in (0, 5):
        ui = {setting["property"]: 0 for setting in startup["settings"]}
        ui.update({"Form1.ComboBox1.ListIndex": mode, "Form1.CheckBox1.Value": 1})
        startup_events, values, pc, _ = replay_startup(startup, ui, "7.2450", "AB12CD", (314, 256))
        options = [values[setting["key"]] for setting in startup["settings"]]
        context = dict(completion_mode=options[0], repair_mode=options[1], return_home=options[3],
                       slow_repair=options[6], simulation_mode=0, sdk_marker="AB12CD",
                       saved_cursor_x=values["MX"], saved_cursor_y=values["MY"])
        machine = FishingRetainedMachine(routines, retained, context.get, 0)
        root = [machine.step()["record"] for _ in range(4)]
        assert root == [0, 1, 2, 3] and machine.pc == startup["entry"]
        assert pc == parts[0]["entry"]
        machine.pc = pc
        machine.frames.append({"slots": {}, "value": None})
        machine.values.update(catch_count=values["VF89CA4BECFC0C1A34D6A65757378756D"],
                              cycle_count=values["CS"], rebait=options[2],
                              stop_at_80=options[4], complete_at_80=options[5], failure_count=0)
        for row in rows:
            at = row["record"]
            if row["kind"] == "unresolved_control":
                row = dict(record=at, kind="jump", target=at + 1)
            elif at == 148:
                row = dict(row, target=252)
            machine.actions[at] = row
            machine.missing.remove(at)
        events, restarts = [], 0
        finish_query = GATES[mode] + 6
        for _ in range(350):
            if machine.done:
                break
            event = machine.step()
            events.append(event)
            at, kind = event["record"], event["kind"]
            if at == 539:
                restarts += 1
            if kind == "find_color" or kind == "find_pic":
                x, y = event["rect"][:2]
                hit = at not in (255, 268) and (at != finish_query or restarts == 0)
                machine.supply_query(x + 1 if hit else -1, y + 1 if hit else -1, int(not hit))
            elif kind == "builtin_color":
                machine.supply_builtin_color(*event["rect"][2:])
        records = [e["record"] for e in events]
        assert machine.done and machine.reason == "script_stop"
        assert restarts == 1 and records.count(finish_query) == 6
        assert records.count(115) == 2 and machine.values["catch_count"] == 2
        assert [e["record"] for e in events if e["kind"] == "os_exit_intent"] == ([517] if mode == 5 else [])
        results.append(dict(mode=mode, records=root + [e["record"] for e in startup_events] + records,
                            reason=machine.reason, next_record=machine.pc, restarts=restarts))
    return dict(cases=results, control_assumptions={116: 117, 139: 140, 148: 252, 319: 320},
                still_unresolved=[26, 116, 139, 319])


def main():
    source = (PROJECT / "programs/05.json").read_bytes()
    raw = json.loads(source)
    alignment = json.loads((OUT / "prefix-structured-alignment.json").read_text("utf8"))
    assert hashlib.sha256(source).hexdigest() == alignment["source_sha256"]
    pool = json.loads((INVENTORY / "05-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    gathering = json.loads((PROJECT / "programs/08.json").read_text("utf8"))
    plan = build(raw, alignment, pool, gathering)
    routines, retained = [json.loads((PROJECT / "data" / f"fishing-{name}.json").read_text("utf8"))
                          for name in ("routines", "retained")]
    report = verify(plan, routines, retained)
    report["joined_startup"] = verify_joined(raw, gathering, alignment, pool, plan, routines, retained)
    for name, data in (("fishing-finish-modes", plan), ("fishing-finish-modes-verification", report)):
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} candidates; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
