"""Map the Chaos second/third floors and close the main loop at original L571."""
import hashlib
import json

from build_battle_chaos_first_fight import COUNTS, END as ENTRY, POTION, build as first_fight
from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier
from export_cube_routines import translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

END = 570
UNRESOLVED = (499, 500)
FLOOR = "VFF89AF887378756D"
THIRD = "VFD8CD4CBA2D9A19C4D6A65757378756D"
REENTRY = "V9BB2B5B7CCD2BFD14D6A65757378756D"
BUTTON = "VF68BB1C47378756D"


def build(raw, pool, digest):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = ENTRY, 364
    calls = []

    def emit(op, arg):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["missing_records"].remove(pc)
        candidate["code"][pc] = [op, code[pc][1], arg, code[pc][3]]
        pc += 1

    def text(ref):
        assert pool[ref]["index"] == ref and pool[ref]["value"] == strings[ref]
        emit(30 if pool[ref]["kind"] == "decoded-text" else 2, ref)

    def texts(stop):
        nonlocal sl
        while sl < stop:
            text(sl)
            sl += 1

    def write():
        nonlocal sl
        assert code[pc][1] == code[pc + 1][1] == code[pc + 2][1]
        text(sl + 2)
        text(sl)
        emit(28, sl + 1)
        sl += 3

    def branch(target, key=None):
        nonlocal sl
        if key is not None:
            assert strings[sl] == key
            emit(27, sl)
            sl += 1
            texts(sl + 1)
        assert code[pc][1] == code[pc + 1][1] != code[pc + 2][1]
        emit(4, sl)
        emit(6, target - pc)
        sl += 1

    def jump(target):
        emit(16, target - pc)

    def call(target, traces=()):
        frame = strings[sl]
        refs = [at for at, (op, _, arg, _) in enumerate(code[:-1])
                if op in (2, 30) and strings[arg] == frame and code[at + 1][0:3:2] == [12, target]]
        assert refs or traces
        assert all(code[at][0] in (2, 30) and "TracePrint" in strings[code[at][2]] for at in traces)
        assert code[target - 1][0] == 16
        assert code[pc][1] == code[pc + 1][1] == code[pc + 2][1]
        name = decode_identifier(frame.split("=New ", 1)[1].split(":", 1)[0].rsplit("_V", 1)[1])
        calls.append(dict(record=pc + 1, target=target, name=name, frame_sl=sl,
                          retained_trace=list(traces), retained_call_frames=refs))
        texts(sl + 1)
        emit(12, target)
        texts(sl + 1)

    call(3864, (3876,))
    texts(368)
    write()
    write()
    write()
    texts(378)
    write()
    texts(382)
    call(1443)
    texts(385)
    write()
    assert pc == 461
    branch(475, THIRD)
    texts(393)
    call(4957, (4978,))
    texts(396)
    call(1443)
    jump(484)
    assert pc == 475
    branch(484, THIRD)
    texts(402)
    call(3439)
    texts(406)
    assert pc == 485
    branch(501, THIRD)
    texts(411)
    branch(500)
    texts(413)
    call(1158, (1244, 1288, 1345))
    texts(417)
    assert pc == UNRESOLVED[0]
    pc += len(UNRESOLVED)
    texts(419)
    call(3190)
    texts(422)
    call(3439)
    texts(426)
    assert pc == 512
    branch(519)
    texts(428)
    call(3458)
    jump(523)
    assert pc == 519
    texts(431)
    call(3660)
    texts(434)
    branch(531)
    texts(437)
    call(3329)
    assert pc == 531
    texts(441)
    call(856, (857,))
    texts(444)
    branch(549, REENTRY)
    texts(448)
    call(3190)
    texts(451)
    call(856, (857,))
    assert pc == 549
    texts(454)
    write()
    texts(459)
    write()
    write()
    texts(466)
    write()
    call(1443)
    texts(473)
    assert pc == END and code[END][0:3:2] == [30, 473] and code[571][0:3:2] == [16, 421 - 571]

    ranges = ((ENTRY, 498, "二層、三層與再來一次"), (501, END - 1, "退出、重進與回到一層"))
    external = (END, *UNRESOLVED, *(c["target"] for c in calls))
    rows = translate(candidate, ranges, external_targets=external)["actions"]
    for row in rows:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    assert sorted(r["source_sl"] for r in rows if r["source_sl"] is not None) == list(range(364, 473))
    return dict(module=6, entry=ENTRY, boundary=END, retained_tail=[570, 571],
                retained_jump_target=421, rows=rows, calls=calls, unresolved=list(UNRESOLVED),
                source_program_sha256=digest, original_values_recovered=0)


def verify(plan, previous, base, retained):
    source = base["actions"] + retained["actions"]
    globals_default = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    values_default = {n: 0 for n in scalar_names(source) if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values_default.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    cases = []
    for entry, third, potion, button, threshold, retry in (
            (421, 0, 0, 0, 10, False), (421, 0, 0, 1, 9, True),
            (421, 1, 1, 0, 10, False), (484, 1, 1, 0, 10, False),
            (484, 1, 0, 0, 10, False), (421, 2, 0, 0, 10, False),
            (499, 1, 1, 0, 10, False)):
        shared = dict(globals_default, **{THIRD: third, REENTRY: 0, "V8186B4D47378756D": "AB12CD"})
        values = dict(values_default, **{POTION: potion, BUTTON: button, "JCXL": threshold,
                                        **dict(zip(COUNTS, (7, 8, 2, 3, 4)))})
        machine = RetainedBattleMachine(base, retained, 0, lambda key, at: shared[key], values)
        machine.pc = entry
        for row in previous["rows"] + plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        events, calls, looped = [], [], False
        for _ in range(4000):
            if machine.done or (looped and machine.pc == ENTRY):
                break
            if machine.pc == 537 and retry:
                shared[REENTRY] = 1
            event = machine.step()
            events.append(event)
            at, kind = event["record"], event["kind"]
            if kind == "call" and ENTRY <= at < END:
                calls.append([at, event["target"]])
            elif kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                x, y = event["rect"][:2]
                if kind.startswith("builtin"):
                    machine.supply_builtin(x + 1, y + 1)
                else:
                    machine.supply_query(x + 1, y + 1, int(kind == "find_color"))
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
            if at == 571:
                assert machine.pc == 421
                looped = True
        records = [e["record"] for e in events]
        ui_writes = [e["value"] for e in events if e["kind"] == "assign_ui_text"]
        floor_writes = [e["value"] for e in events if e["kind"] == "write_global" and e["key"] == FLOOR]
        if entry == 421 and third != 1:
            expected = [[436, 3864], [455, 1443]]
            if third == 0:
                expected.append([481, 3439])
            expected.extend(([504, 3190], [508, 3439], [516, 3458] if button == 0 else [521, 3660]))
            if threshold <= 9:
                expected.append([529, 3329])
            expected.append([534, 856])
            if retry:
                expected.extend(([543, 3190], [547, 856]))
            assert calls == expected + [[566, 1443]]
            tail = records.index(570)
            assert records[tail:tail + 3] == [570, 571, 421]
            assert ui_writes == ["8", "2", "3", "4", "9", "2", "3", "4"]
            assert floor_writes[:3] == [2, 2, 3] and floor_writes[-1] == 1
            assert looped and machine.pc == ENTRY and not machine.done
        elif potion == 1 and entry != 499:
            prefix = [[436, 3864], [455, 1443], [468, 4957], [472, 1443]] if entry == 421 else []
            assert calls == prefix + [[495, 1158]]
            assert records[-3:] == [496, 497, 498] and machine.reason == "script_stop"
        else:
            assert machine.pc == (499 if entry == 499 else 500) and machine.reason == "missing_original_record"
            assert not calls
        cases.append(dict(entry=entry, third=third, potion=potion, button=button, threshold=threshold,
                          forced_reentry_flag=retry, root_calls=calls, records=records,
                          ui_writes=ui_writes, floor_writes=floor_writes,
                          looped=looped, reason=machine.reason or ("loop_closed" if looped else "step_limit"),
                          next_record=machine.pc))
    return dict(cases=cases, original_effects_run=False)


def main():
    source = (PROJECT / "programs/06.json").read_bytes()
    raw, digest = json.loads(source), hashlib.sha256(source).hexdigest()
    pool = json.loads((INVENTORY / "06-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(raw, pool, digest)
    previous = first_fight(raw, pool, digest)
    base, retained = [json.loads((PROJECT / "data" / f"{stem}-06.json").read_text("utf8"))
                      for stem in ("battle", "battle-retained")]
    report = verify(plan, previous, base, retained)
    for name, value in (("battle-chaos-cycle", plan), ("battle-chaos-cycle-verification", report)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} candidates", [(c["entry"], c["next_record"], c["root_calls"]) for c in report["cases"]])


if __name__ == "__main__":
    main()
