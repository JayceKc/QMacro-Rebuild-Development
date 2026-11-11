"""Align the fishing exit actions and calls into the retained repair body."""
import hashlib
import json

from build_cube_start_workers import decode_identifier
from build_fishing_catch import build as build_catch, OPAQUE
from build_fishing_startup import INVENTORY, OUT, build as build_startup, replay as replay_startup
from export_fishing_routines import PROJECT, routine_roles, translate_bodies
from qmacro_fishing_retained import FishingRetainedMachine

ENTRY, REPAIR, END = 204, 252, 277


def build(raw, alignment, pool):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    rows = []
    roles = routine_roles(raw)

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

    def texts(lo, hi):
        for sl in range(lo, hi):
            text(sl)

    def branch(sl, target, **manual):
        emit(4, sl, **manual)
        emit(6, target - (ENTRY + len(rows)))

    def jump(target):
        emit(16, target - (ENTRY + len(rows)))

    def repair(sl):
        frame = strings[sl].split("=New ", 1)[1].split(":", 1)[0]
        assert strings[code[2][2]].startswith(f"Class {frame}:")
        assert decode_identifier(frame.rsplit("_V", 1)[1]) == "工具红了"
        text(sl, kind="frame_enter", name="repair")
        emit(12, 541)
        assert "(1)=" in strings[sl + 1]
        text(sl + 1, kind="store_return", slot=1)

    for at in range(204, 238):
        op, loc, sl, _ = code[at + 622]
        assert loc - code[at][1] == 625
        if at == 204:
            assert op == 4 and strings[sl] == strings[164].replace("=3)", "=4)")
        elif at == 205:
            assert op == 6 and at + 622 + sl == 864
        else:
            assert op == 30 and strings[sl] == strings[at - 41]
    branch(164, 243)
    texts(165, 201)
    jump(REPAIR)
    branch(201, REPAIR)
    text(202)
    assert code[516][0:3:2] == [31, 203] and strings[code[517][2]] == strings[204]
    emit(31, 203)
    texts(204, 213)
    positive = [{"gt": [{"role": f"query_{axis}"}, {"const": 0}]} for axis in "xy"]
    for sl, target in ((213, 267), (216, 267)):
        assert strings[sl] == "Sgn(INTX>0 And INTY>0)"
        branch(sl, target, kind="test", condition={"all": positive})
        if sl == 213:
            texts(214, 216)
    text(217)
    repair(218)
    texts(220, 223)
    assert strings[223] == "Sgn((INTX>0))"
    branch(223, 276, kind="test", condition=positive[0])
    text(224)
    repair(225)
    texts(227, 229)
    assert ENTRY + len(rows) == END

    cursor = 164
    for group in alignment["groups"]:
        if not ENTRY <= group["records"][0] < END:
            continue
        refs = [rows[at - ENTRY]["source_sl"] for at in group["records"]]
        following = cursor + sum(sl is not None for sl in refs)
        assert any(c["source_range"] == [cursor, following]
                   and [r["source_sl"] for r in c["instructions"]] == refs for c in group["candidates"]), (group["records"], refs)
        cursor = following
    assert cursor == 229
    return dict(module=5, entry=ENTRY, repair_entry=REPAIR, boundary=END, rows=rows,
                retained_exit_reference=[826, 859], retained_sys_reference=[516, 517],
                catch_join_assumption={"record": 148, "target": REPAIR},
                repair_call_target_status="candidate by decoded class name and retained repair behavior",
                original_values_recovered=0, source_program_sha256=alignment["source_sha256"])


def verify(plan, startup, catch, routines, retained):
    cases = []
    scenarios = [(80, mode, None, markers) for mode in range(6)
                 for markers in ((False, False, False), (True, True, True))]
    scenarios += [(80, 4, 3, (False, False, False)), (79, 5, None, (False, False, False)),
                  (79, 0, None, (True, False, True)), (79, 0, None, (False, True, False))]
    for count, mode, updated_mode, hits in scenarios:
        ui = {setting["property"]: 0 for setting in startup["settings"]}
        ui.update({"Form1.ComboBox1.ListIndex": mode, "Form1.CheckBox4.Value": 1})
        _, state, pc, _ = replay_startup(startup, ui, "7.2450", "AB12CD", (314, 256))
        assert pc == catch["entry"]
        options = [state[setting["key"]] for setting in startup["settings"]]
        context = dict(completion_mode=options[0], repair_mode=options[1], return_home=options[3],
                       slow_repair=options[6], simulation_mode=0, sdk_marker="AB12CD",
                       saved_cursor_x=state["MX"], saved_cursor_y=state["MY"])
        machine = FishingRetainedMachine(routines, retained, context.get, 0)
        machine.pc = pc
        machine.frames.append({"slots": {}, "value": None})
        machine.values.update(catch_count=count - 1, cycle_count=state["CS"],
                              stop_at_80=options[4], complete_at_80=options[5])
        for row in catch["rows"] + plan["rows"]:
            at = row["record"]
            if at in OPAQUE:
                row = dict(record=at, kind="jump", target=at + 1)
            if at == 148:
                row = dict(row, target=REPAIR)
            machine.actions[at] = row
            machine.missing.remove(at)
        events = []
        for _ in range(500):
            if machine.done:
                break
            if machine.pc == ENTRY and updated_mode is not None:
                context["completion_mode"] = updated_mode
            event = machine.step()
            events.append(event)
            kind, at = event["kind"], event["record"]
            if kind in ("find_color", "find_pic"):
                left, top, _, _ = event["rect"]
                found = hits[(255, 259, 268).index(at)] if at in (255, 259, 268) else True
                machine.supply_query(left + 1 if found else -1, top + 1 if found else -1, int(not found))
            elif kind == "random_int":
                machine.supply_random(event["lower"])
        records = [e["record"] for e in events]
        shutdown = count == 80 and mode == 5
        click_exit = updated_mode == 3
        continue_to_repair = count != 80 or (mode == 4 and not click_exit)
        assert machine.done
        if continue_to_repair:
            assert machine.pc == END
        assert (247 in records) == shutdown and (207 in records) == click_exit
        assert (REPAIR in records) == continue_to_repair
        calls = [e["record"] for e in events if e["kind"] == "call" and e["target"] == 541]
        expected = ([264] if all(hits[:2]) else []) + ([273] if hits[2] else []) if continue_to_repair else []
        assert calls == expected and all(at + 1 in records for at in calls)
        assert machine.reason == ("missing_original_record" if continue_to_repair else "script_stop")
        cases.append(dict(count=count, mode=mode, mode_at_204=updated_mode, markers=hits, records=records,
                          repair_calls=calls, shutdown_intent=shutdown, next_record=machine.pc, reason=machine.reason))
    return dict(cases=cases, steps=sum(len(c["records"]) for c in cases), os_exit_called=False, real_actions_sent=False)


def main():
    source = (PROJECT / "programs/05.json").read_bytes()
    raw = json.loads(source)
    alignment = json.loads((OUT / "prefix-structured-alignment.json").read_text("utf8"))
    pool = json.loads((INVENTORY / "05-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    startup = build_startup(raw, alignment, pool, hashlib.sha256(source).hexdigest())
    catch = build_catch(raw, alignment, pool)
    plan = build(raw, alignment, pool)
    routines, retained = [json.loads((PROJECT / "data" / f"fishing-{name}.json").read_text("utf8"))
                          for name in ("routines", "retained")]
    report = verify(plan, startup, catch, routines, retained)
    for name, data in (("fishing-repair-dispatch", plan), ("fishing-repair-dispatch-verification", report)):
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} candidates; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
