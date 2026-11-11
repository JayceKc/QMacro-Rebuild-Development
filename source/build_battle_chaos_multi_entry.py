"""Reconstruct multi-character Chaos's post-switch dispatch and initial fight."""
import hashlib
import json
import re

from build_battle_entry_routes import END as PREVIOUS_END, MODE, build as entry_routes
from build_cube_prefix import INVENTORY, PROJECT
from export_cube_routines import translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

ENTRY, END = PREVIOUS_END[1], 433
READY = "V8ED1B6A5B580BACFF9A4AF887378756D"
WEEKLY = "V8B92AAD7A5A4BDA3839B65757378756D"
GUILD = "VF4C1DE947378756D"
ROUTE = "VFDDEA0D0CE9FB68B4D6A65757378756D"
RETRY = "V9BB2B5B7CCD2BFD14D6A65757378756D"
FIGHT_STATE = "V98B8D0C8A4B7B6A84D6A65757378756D"


def normalize_mirror(text):
    return re.sub(r"(lDA)\(\d+\)", r"\1(#)", text).replace("-----主控-----", ">>>>>>")


def build(raw, pool, digest):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = ENTRY, 306
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

    def mirror(first, last, location_delta, override=None):
        nonlocal sl
        start = pc
        for at in range(first, last + 1):
            op, loc, arg, _ = code[at]
            assert code[pc][1] + location_delta == loc
            if op in (2, 4, 27, 30):
                old, new = strings[arg], strings[sl]
                assert normalize_mirror(old) == normalize_mirror(new), (pc, old, new)
                text(sl, op)
                sl += 1
            else:
                assert op in (6, 12, 16)
                if op == 12:
                    calls.append(dict(record=pc, target=arg, retained_frame=at - 1, retained_call=at))
                emit(op, override if at == last and override is not None else arg)
        mirrors.append(dict(candidate=[start, pc - 1], retained=[first, last], location_delta=location_delta))

    def call(target, ref=None, body_evidence=()):
        start = pc
        assert code[start][1] == code[start + 1][1] == code[start + 2][1]
        if ref is not None:
            assert code[ref + 1][0:3:2] == [12, target] and strings[code[ref][2]] == strings[sl]
        else:
            assert code[target - 1][0] == 16 and body_evidence
        calls.append(dict(record=start + 1, target=target, frame_sl=sl, retained_frame=ref,
                          retained_call=ref + 1 if ref is not None else None, body_evidence=list(body_evidence)))
        texts(sl + 1)
        emit(12, target)
        texts(sl + 1)

    def write(key):
        nonlocal sl
        assert code[pc][1] == code[pc + 1][1] == code[pc + 2][1] and strings[sl + 1] == key
        text(sl + 2)
        text(sl)
        text(sl + 1, 28)
        sl += 3

    mirror(646, 667, 184)
    mirror(673, 692, 187)
    assert (pc, sl) == (394, 334)
    texts(336)
    call(3479, 670)
    texts(340)
    call(1020, 695)
    mirror(698, 705, 184, override=340 - 411)
    assert (pc, sl) == (412, 347)
    texts(348)
    write(RETRY)
    write(FIGHT_STATE)
    assert (pc, sl) == (419, 354)
    mirror(724, 732, 192)
    texts(362)
    assert "ThreadControl" in strings[code[8325][2]] and "放技能判定.已开启" in strings[code[8327][2]]
    call(8322, body_evidence=(8321, 8325, 8327, 8340))
    texts(365)
    assert (pc, sl) == (END, 365)
    rows = translate(candidate, ((ENTRY, END - 1, "切角後的副本與首次打怪"),),
                     external_targets=(340, END, *(c["target"] for c in calls)))["actions"]
    for row in rows:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    assert sorted(r["source_sl"] for r in rows if r["source_sl"] is not None) == list(range(306, 365))
    return dict(module=1, entry=ENTRY, boundary=END, rows=rows, calls=calls, retained_mirrors=mirrors,
                source_program_sha256=digest, original_values_recovered=0)


def verify(plan, previous, base, retained):
    source = base["actions"] + retained["actions"]
    globals_default = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    values_default = {n: 0 for n in scalar_names(source) if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values_default.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    cases = []
    for entry, mode, weekly, guild, route, retry in (
            (349, 0, 0, 0, 0, False), (ENTRY, 1, 1, 0, 0, False),
            (ENTRY, 2, 0, 1, 0, False), (ENTRY, 3, 1, 1, 0, False),
            (ENTRY, 0, 0, 0, 0, True), (419, 0, 0, 0, 4, False)):
        shared = dict(globals_default, **{READY: 0, ROUTE: route, RETRY: 9, FIGHT_STATE: 8,
                                          "V8186B4D47378756D": "AB12CD"})
        values = dict(values_default, **{MODE: mode, WEEKLY: weekly, GUILD: guild})
        machine = RetainedBattleMachine(base, retained, 0, lambda key, at: shared[key], values)
        machine.pc = entry
        for row in previous["rows"] + plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        records, calls, returns, writes = [], [], [], []
        for _ in range(3500):
            if machine.done or machine.pc in (340, END):
                break
            if retry and machine.pc == 405:
                shared[READY] = 1
            event = machine.step()
            at, kind = event["record"], event["kind"]
            records.append(at)
            if kind == "call" and 349 <= at < END:
                calls.append([at, event["target"]])
            elif kind == "return" and 349 <= event.get("target", -1) < END:
                returns.append(event["target"])
            elif kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                x, y = event["rect"][:2]
                coords = (-1, -1) if at in range(12054, 12079, 4) else (x + 1, y + 1)
                if kind.startswith("builtin"):
                    machine.supply_builtin(*coords)
                else:
                    machine.supply_query(*coords, int(kind == "find_color" and coords[0] >= 0))
            elif kind == "random_int":
                machine.supply_random(event["lower"])
            elif kind == "write_global":
                shared[event["key"]] = event["value"]
                if ENTRY <= at < END:
                    writes.append([at, event["key"], event["value"]])
            elif kind == "worker_start":
                machine.supply_worker_id(1000 + at)
            elif kind == "dm_real_mouse_intent":
                machine.supply_dm_return(1)
            elif kind == "capture_intent":
                machine.supply_capture_return(1)
        if entry == 419:
            expected = [[426, 12002], [430, 8322]]
            assert writes == []
        else:
            expected = [[350, 3623]] if entry == 349 else []
            expected += {0: [[358, 3642]], 1: [[365, 3838]], 2: [[372, 3642]], 3: []}[mode]
            if weekly:
                expected.append([380, 10955])
            if guild:
                expected.append([390, 11169])
            expected.extend(([397, 3479], [402, 1020]))
            if retry:
                assert records[-5:] == [405, 406, 407, 408, 411] and writes == []
            else:
                expected.append([430, 8322])
                assert writes == [[415, RETRY, 0], [418, FIGHT_STATE, 0]]
        assert calls == expected and returns == [at + 1 for at, _ in calls]
        assert machine.pc == (340 if retry else END) and not machine.done
        cases.append(dict(entry=entry, mode=mode, weekly=weekly, guild=guild, route=route,
                          forced_retry=retry, root_calls=calls, return_slots=returns, records=records,
                          next_record=machine.pc, root_shared_writes=writes))
    return dict(cases=cases, original_effects_run=False)


def main():
    source = (PROJECT / "programs/01.json").read_bytes()
    raw, digest = json.loads(source), hashlib.sha256(source).hexdigest()
    pool = json.loads((INVENTORY / "01-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(raw, pool, digest)
    previous = entry_routes(raw, pool, digest)
    base, retained = [json.loads((PROJECT / "data" / f"{stem}-01.json").read_text("utf8"))
                      for stem in ("battle", "battle-retained")]
    report = verify(plan, previous, base, retained)
    for name, value in (("battle-chaos-multi-entry", plan), ("battle-chaos-multi-entry-verification", report)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} candidates", [(c["entry"], c["next_record"], c["root_calls"]) for c in report["cases"]])


if __name__ == "__main__":
    main()
