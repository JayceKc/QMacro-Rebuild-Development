"""Map Chaos's initial fight, repeat branch and first count display."""
import hashlib
import json
import re

from build_battle_chaos_workers import END as ENTRY
from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier
from export_cube_routines import expression, translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

END, UNRESOLVED = 435, 415
MODE = "VFDDEA0D0CE9FB68B4D6A65757378756D"
POTION = "VFEBEA38DBCDAA7C44D6A65757378756D"
COUNTS = ("V86C8D4CBB3A3C9ABF9A4AF887378756D", "V87ADD284A3A6B580F9A4AF887378756D",
          "VF09AA6B0B3A3C9ABF9A4AF887378756D", "V9AA5A6B0B3A3C9ABF9A4AF887378756D",
          "VF2C2B2D4B3A3C9ABF9A4AF887378756D")


def build(raw, pool, digest):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = ENTRY, 318
    calls, manual = [], {}

    def emit(op, arg):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["missing_records"].remove(pc)
        candidate["code"][pc] = [op, code[pc][1], arg, code[pc][3]]
        pc += 1

    def text():
        nonlocal sl
        assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
        emit(30 if pool[sl]["kind"] == "decoded-text" else 2, sl)
        sl += 1

    def texts(stop):
        while sl < stop:
            text()

    def branch(target):
        nonlocal sl
        assert code[pc][1] == code[pc + 1][1] != code[pc + 2][1]
        emit(4, sl)
        emit(6, target - pc)
        sl += 1

    def call(target, trace, refs=()):
        start = pc
        assert code[start][1] == code[start + 1][1] == code[start + 2][1]
        frame = strings[sl]
        name = decode_identifier(frame.split("=New ", 1)[1].split(":", 1)[0].rsplit("_V", 1)[1])
        assert code[target - 1][0] == 16
        assert all(strings[code[at][2]] == frame and code[at + 1][0:3:2] == [12, target] for at in refs)
        assert all(code[at][0] in (2, 30) and "TracePrint" in strings[code[at][2]] for at in trace)
        calls.append(dict(record=start + 1, target=target, name=name, frame_sl=sl,
                          retained_trace=list(trace), retained_call_frames=list(refs)))
        text()
        emit(12, target)
        text()

    text()
    assert strings[sl] == MODE
    emit(27, sl)
    sl += 1
    text()
    branch(UNRESOLVED)
    text()
    call(8840, (8848, 8865))
    text()
    call(8159, (8164, 8283))
    text()
    assert strings[sl] == f"Sgn({POTION}=1)"
    branch(UNRESOLVED)
    text()
    assert pc == 394 and strings[sl] == "Sgn(vbTrue)"
    branch(UNRESOLVED)
    texts(337)
    call(1158, (1244, 1288, 1345))
    text()
    call(8840, (8848, 8865))
    text()
    call(1443, (), (4862, 4900, 4938))
    texts(347)
    assert pc == 414
    emit(16, 394 - pc)
    assert pc == UNRESOLVED
    pc += 1
    text()
    call(8159, (8164, 8283))
    text()
    assert pc == 421 and strings[sl] == "Sgn(vbTrue)"
    branch(END)
    texts(358)
    for i, key in enumerate((COUNTS[0], *COUNTS[2:]), 1):
        assert strings[sl] == f"FORM1.INPUTBOX{i}.TEXT={key}"
        manual[pc] = dict(record=pc, location=code[pc][1], field_3=code[pc][3], kind="assign_ui_text",
                          path=f"Form1.InputBox{i}.Text", value=expression(key),
                          source_sl=sl, source=strings[sl], candidate_opcode=30, inferred=True)
        text()
    texts(364)
    assert pc == END and sl == 364
    ranges = ((ENTRY, 414, "首次打怪與再來一次"), (416, 428, "主迴圈入口"), (433, 434, "找圖二前"))
    actions = translate(candidate, ranges, external_targets=(UNRESOLVED, END, *(c["target"] for c in calls)))["actions"]
    for row in actions:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    rows = sorted(actions + list(manual.values()), key=lambda row: row["record"])
    assert sorted(r["source_sl"] for r in rows if r["source_sl"] is not None) == list(range(318, 364))
    return dict(module=6, entry=ENTRY, boundary=END, rows=rows, calls=calls, unresolved=[UNRESOLVED],
                source_program_sha256=digest, original_values_recovered=0)


def verify(plan, base, retained):
    source = base["actions"] + retained["actions"]
    globals_default = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    values_default = {n: 0 for n in scalar_names(source) if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values_default.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    cases = []
    for entry, mode, potion, assumption, limit, map401 in (
            (ENTRY, 0, 0, False, 50, False), (ENTRY, 4, 1, False, 900, False),
            (391, 4, 0, False, 30, False), (391, 4, 1, False, 1100, False),
            (ENTRY, 0, 0, True, 900, False), (421, 0, 0, False, 50, False),
            (ENTRY, 4, 1, False, 2500, True)):
        shared = dict(globals_default, **{MODE: mode, "V8186B4D47378756D": "AB12CD"})
        values = dict(values_default, **{POTION: potion, **dict(zip(COUNTS, (7, 8, 2, 3, 4)))})
        machine = RetainedBattleMachine(base, retained, 0, lambda key, at: shared[key], values)
        machine.pc = entry
        for row in plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        if assumption:
            machine.actions[UNRESOLVED] = dict(record=UNRESOLVED, kind="jump", target=416)
            del machine.boundaries[UNRESOLVED]
        events, calls = [], []
        for _ in range(limit):
            if machine.done:
                break
            event = machine.step()
            events.append(event)
            at, kind = event["record"], event["kind"]
            if kind == "call" and ENTRY <= at < END:
                calls.append([at, event["target"]])
            elif kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                x, y = event["rect"][:2]
                coords = (-1, -1) if map401 and at in range(8892, 8917, 4) else (x + 1, y + 1)
                if kind.startswith("builtin"):
                    machine.supply_builtin(*coords)
                else:
                    machine.supply_query(*coords, int(kind == "find_color" and coords[0] >= 0))
            elif kind == "random_int":
                machine.supply_random(event["lower"])
            elif kind == "write_global":
                shared[event["key"]] = event["value"]
            elif kind == "worker_start":
                machine.supply_worker_id(1000 + at)
            elif kind == "dm_real_mouse_intent":
                machine.supply_dm_return(1)
            elif kind == "capture_intent":
                machine.supply_capture_return(1)
        if entry == 421:
            assert machine.pc == END and machine.done
            assert [machine.values[key] for key in COUNTS[:2]] == [8, 9]
            assert [e["value"] for e in events if e["kind"] == "assign_ui_text"] == ["8", "2", "3", "4"]
        elif not assumption and potion == 0:
            assert machine.pc == UNRESOLVED and machine.done and not calls
        else:
            expected = [418, 8159] if assumption else [402, 1158] if entry == 391 else [384, 8840]
            assert calls and calls[0] == expected
        if assumption:
            assert machine.done and machine.pc == END
            assert [e["value"] for e in events if e["kind"] == "assign_ui_text"] == ["8", "2", "3", "4"]
        if map401:
            assert calls == [[384, 8840], [388, 8159], [402, 1158], [406, 8840], [410, 1443]]
            assert machine.done and machine.reason == "script_stop"
        cases.append(dict(entry=entry, mode=mode, potion=potion, assumed_l415_fallthrough=assumption,
                          map401_observations=map401, root_calls=calls, records=[e["record"] for e in events],
                          ui_writes=[e for e in events if e["kind"] == "assign_ui_text"],
                          reason=machine.reason or "step_limit", next_record=machine.pc))
    return dict(cases=cases, original_effects_run=False)


def main():
    path = PROJECT / "programs/06.json"
    source = path.read_bytes()
    pool = json.loads((INVENTORY / "06-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(json.loads(source), pool, hashlib.sha256(source).hexdigest())
    base, retained = [json.loads((PROJECT / "data" / f"{stem}-06.json").read_text("utf8"))
                      for stem in ("battle", "battle-retained")]
    report = verify(plan, base, retained)
    for name, value in (("battle-chaos-first-fight", plan), ("battle-chaos-first-fight-verification", report)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} candidates", [(c["entry"], c["next_record"], c["root_calls"]) for c in report["cases"]])


if __name__ == "__main__":
    main()
