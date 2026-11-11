"""Join module 01's missing loop prefix to the retained L562..740 body."""
import hashlib
import json
import re

from build_battle_chaos_multi_entry import (
    END as ENTRY, MODE, RETRY, ROUTE, WEEKLY, build as multi_entry, entry_routes, normalize_mirror,
)
from build_cube_prefix import INVENTORY, PROJECT
from export_cube_routines import ARRAY, FRAME, translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

END, UNKNOWN = 562, 555
DISMANTLE = "V85C1D7CAC4AEC88F4D6A65757378756D"
REWARD = "V8C86D0ADB3B6A3B1F0DBA58D7378756D"
COUNT = "V86C8D4CBB3A3C9ABF9A4AF887378756D"
LAST_ROLE = "VF0ADACDECE99BF954D6A65757378756D"


def normalized(source):
    source = normalize_mirror(source)
    source = source.replace(f"{FRAME}.{ARRAY}", ARRAY)
    return re.sub(r"Delay\(\((\d+)\)\)", r"Delay(\1)", source)


def build(raw, pool, digest):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = ENTRY, 365
    calls, mirrors = [], []

    def emit(op, operand):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["missing_records"].remove(pc)
        candidate["code"][pc] = [op, code[pc][1], operand, code[pc][3]]
        pc += 1

    def text(ref, opcode=None):
        assert pool[ref]["index"] == ref and pool[ref]["value"] == strings[ref]
        emit(opcode if opcode is not None else (30 if pool[ref]["kind"] == "decoded-text" else 2), ref)

    def texts(stop):
        nonlocal sl
        while sl < stop:
            text(sl)
            sl += 1

    def branch(target):
        nonlocal sl
        assert code[pc][1] == code[pc + 1][1]
        text(sl, 4)
        emit(6, target - pc)
        sl += 1

    def mirror(first, last, offset):
        nonlocal sl
        start = pc
        for at in range(first, last + 1):
            op, loc, arg, _ = code[at]
            assert code[pc][1] + offset == loc, (pc, at)
            if op in (2, 4, 27, 30):
                assert normalized(strings[arg]) == normalized(strings[sl]), (pc, at, strings[arg], strings[sl])
                text(sl, op)
                sl += 1
            else:
                assert op in (6, 12, 16)
                if op == 12:
                    calls.append(dict(record=pc, target=arg, retained_call=at))
                emit(op, arg)
        mirrors.append(dict(candidate=[start, pc - 1], retained=[first, last], location_delta=offset))

    assert strings[sl] == "Sgn(vbTrue)" and code[740][0:3:2] == [16, ENTRY - 740]
    branch(741)
    texts(368)
    assert strings[sl] == ROUTE
    text(sl, 27)
    sl += 1
    texts(370)
    branch(550)
    texts(373)
    mirror(11285, 11293, 9475)
    mirror(11317, 11336, 9495)
    assert (pc, sl) == (472, 396)
    texts(397)
    assert strings[398] == RETRY
    text(399)
    text(397)
    text(398, 28)
    sl = 400
    texts(401)
    mirror(634, 706, 94)
    assert (pc, sl) == (550, 452)
    texts(457)
    assert pc == UNKNOWN
    pc += 1
    assert code[4058][0] == 16 and "图2到了" in strings[code[4071][2]]
    assert code[556][1] == code[557][1] == code[558][1]
    calls.append(dict(record=557, target=4059, body_evidence=[4058, 4062, 4071]))
    texts(458)
    emit(12, 4059)
    texts(461)
    assert code[562][0:3:2] == [2, 461] and code[563][0:3:2] == [28, 462]
    assert code[561][1] == code[562][1] == code[563][1]
    assert normalized(strings[463]) == normalized(strings[466]) and code[564][0:3:2] == [2, 466]
    emit(2, 463)
    assert pc == END
    rows = translate(candidate, ((ENTRY, UNKNOWN - 1, "主迴圈及切角"), (556, END - 1, "找圖二與原寫入接合")),
                     external_targets=(END, 741, UNKNOWN, *(c["target"] for c in calls)))["actions"]
    for row in rows:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    assert sorted(r["source_sl"] for r in rows if r["source_sl"] is not None) == [*range(365, 461), 463]
    return dict(module=1, entry=ENTRY, boundary=END, rows=rows, calls=calls, retained_mirrors=mirrors,
                unresolved=[UNKNOWN], retained_return=[740, ENTRY],
                source_program_sha256=digest, original_values_recovered=0)


def verify(plan, previous, base, retained):
    source = base["actions"] + retained["actions"]
    globals_default = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    values_default = {n: 0 for n in scalar_names(source) if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values_default.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    cases = []
    for entry, route, choices, assumed, stop in (
            (ENTRY, 4, 0, False, 477), (ENTRY, 4, 7, False, 477),
            (ENTRY, 0, 0, False, None), (ENTRY, 0, 0, True, 565),
            (ENTRY, 0, 0, True, None), (ENTRY, 4, 7, True, None), (706, 4, 0, False, None),
            (316, 0, 0, True, None)):
        shared = dict(globals_default, **{ROUTE: route, "V8186B4D47378756D": "AB12CD"})
        values = dict(values_default, **{COUNT: 7, MODE: 0, LAST_ROLE: int(entry == 316), WEEKLY: choices & 1,
                                        DISMANTLE: (choices >> 1) & 1, REWARD: (choices >> 2) & 1})
        machine = RetainedBattleMachine(base, retained, 0, lambda key, at: shared[key], values)
        machine.pc = entry
        for row in previous + plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        if assumed:
            machine.actions[UNKNOWN] = dict(record=UNKNOWN, kind="jump", target=556)
            del machine.boundaries[UNKNOWN]
        records, calls, notes, writes, thread_controls, looped = [], [], [], [], [], False
        for _ in range(3500):
            if machine.done or machine.pc == stop or (looped and machine.pc == ENTRY):
                break
            event = machine.step()
            at, kind = event["record"], event["kind"]
            records.append(at)
            if at == 740:
                assert machine.pc == ENTRY
                looped = True
            if kind == "call" and 316 <= at <= 740:
                calls.append([at, event["target"]])
            elif kind == "trace" and ENTRY <= at <= 740:
                notes.append([at, event["arguments"]])
            elif kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                x, y = event["rect"][:2]
                miss = at == 8863 or at in range(12054, 12079, 4)
                coords = (-1, -1) if miss else (x + 1, y + 1)
                if kind.startswith("builtin"):
                    machine.supply_builtin(*coords)
                else:
                    machine.supply_query(*coords, int(kind == "find_color" and not miss))
            elif kind == "random_int":
                machine.supply_random(event["lower"])
            elif kind == "write_global":
                shared[event["key"]] = event["value"]
                if ENTRY <= at <= 740:
                    writes.append([at, event["key"], event["value"]])
            elif kind == "worker_start":
                machine.supply_worker_id(1000 + at)
            elif kind == "dm_real_mouse_intent":
                machine.supply_dm_return(1)
            elif kind == "capture_intent":
                machine.supply_capture_return(1)
            elif kind == "thread_control_intent" and ENTRY <= at <= 740:
                thread_controls.append([at, event["arguments"]])
        common = [[557, 4059], [576, 1591], [584, 5120], [588, 1591], [631, 11284], [639, 8795]]
        side = [[456, 10955], [463, 11342], [470, 11961]] if choices else []
        if stop == 477:
            assert machine.pc == 477 and calls == side and machine.values[COUNT] == 99
            assert writes == [[475, RETRY, 0]]
        elif not assumed and entry == ENTRY:
            assert machine.pc == UNKNOWN and machine.reason == "missing_original_record" and not calls
        elif stop == 565:
            assert machine.pc == 565 and calls == [[557, 4059]]
            assert records[-4:] == [561, 562, 563, 564] and writes == [[563, "VF2C2A4BE7378756D", 0]]
        elif route == 4 and entry == ENTRY:
            assert machine.pc == 8701 and machine.reason == "script_stop"
            assert calls == side + [[482, 8795], [487, 3623], [495, 3642], [514, 3479],
                                    [522, 10955], [539, 1020]] + common
        else:
            assert looped and machine.pc == ENTRY and records[-3:] == [738, 739, 740], (
                entry, machine.pc, machine.reason, calls, records[-16:])
            if entry == 706:
                assert calls == [[731, 12002], [735, 1591]]
            else:
                prefix = [[321, 3642], [345, 8795], [350, 3623], [358, 3642], [397, 3479],
                          [402, 1020], [430, 8322]] if entry == 316 else []
                assert calls == prefix + common + [[644, 3623], [652, 3642], [671, 3479], [696, 1020], [735, 1591]]
                assert [value for _, key, value in writes if key == "VFF89AF887378756D"] == [2, 3, 1]
                assert [at for at, _ in thread_controls][:5] == [598, 602, 606, 610, 614], thread_controls
        cases.append(dict(entry=entry, route=route, choices=choices, last_role_index=values[LAST_ROLE],
                          assumed_l555_fallthrough=assumed,
                          root_calls=calls, records=records, notes=notes, root_shared_writes=writes,
                          root_thread_controls=thread_controls,
                          count=machine.values[COUNT], looped=looped, next_record=machine.pc,
                          reason=machine.reason or ("loop_closed" if looped else "fixture_stop" if stop else "step_limit")))
    return dict(cases=cases, original_effects_run=False)


def main():
    source = (PROJECT / "programs/01.json").read_bytes()
    raw, digest = json.loads(source), hashlib.sha256(source).hexdigest()
    pool = json.loads((INVENTORY / "01-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(raw, pool, digest)
    base, retained = [json.loads((PROJECT / "data" / f"{stem}-01.json").read_text("utf8"))
                      for stem in ("battle", "battle-retained")]
    previous = entry_routes(raw, pool, digest)["rows"] + multi_entry(raw, pool, digest)["rows"]
    report = verify(plan, previous, base, retained)
    for name, value in (("battle-chaos-multi-cycle", plan), ("battle-chaos-multi-cycle-verification", report)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    for case in report["cases"]:
        print(case["entry"], case["route"], case["choices"], case["root_calls"], case["next_record"],
              case["reason"], len(case["records"]), case["records"][-10:])


if __name__ == "__main__":
    main()
