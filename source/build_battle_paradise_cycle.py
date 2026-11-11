"""Map the Paradise main loop using retained controls and cross-module layouts."""
import hashlib
import json

from build_battle_chaos_multi_cycle import normalized
from build_battle_entry_routes import END as PREVIOUS_END, WEEKLY, build as entry_routes
from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier
from export_cube_routines import translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

ENTRY, END = PREVIOUS_END[3], 368
READY = "V8ED1B6A5B580BACFF9A4AF887378756D"
ALT = "VF6A9DBC6C8C1BFAA819EB0C87378756D"
EXHAUSTED = "V8ED1D1BBB985B4A64D6A65757378756D"
COUNT = "V86C8D4CBB3A3C9ABF9A4AF887378756D"
SDK = "V8186B4D47378756D"
RETRIES = "V9FD1B3C4A6AAC7D6F8D765757378756D"


def build(raw, pool, digest, multi):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = ENTRY, 193
    calls, mirrors = [], []

    def emit(op, operand):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["missing_records"].remove(pc)
        candidate["code"][pc] = [op, code[pc][1], operand, code[pc][3]]
        pc += 1

    def text(opcode=None):
        nonlocal sl
        assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
        emit(opcode if opcode is not None else (30 if pool[sl]["kind"] == "decoded-text" else 2), sl)
        sl += 1

    def texts(stop):
        while sl < stop:
            text()

    def branch(target, key=None):
        if key is not None:
            assert strings[sl] == key
            text(27)
            text()
        assert code[pc][1] == code[pc + 1][1]
        text(4)
        emit(6, target - pc)

    def jump(target):
        emit(16, target - pc)

    def mirror(original, first, last, offset, targets=None):
        start = pc
        for at in range(first, last + 1):
            op, loc, arg, _ = original["code"][at]
            assert code[pc][1] + offset == loc, (pc, at)
            if op in (2, 4, 27, 30):
                assert normalized(original["strings"][arg]) == normalized(strings[sl]), (
                    pc, at, original["strings"][arg], strings[sl])
                text(op if op in (4, 27) else None)
            else:
                assert op in (6, 16)
                target = (targets or {}).get(at)
                emit(op, target - pc if target is not None else arg)
        mirrors.append(dict(module=original["module"], candidate=[start, pc - 1], retained=[first, last],
                            location_delta=offset, target_overrides=targets or {}))

    def call(target, refs=(), same_frame=None, traces=()):
        frame = strings[sl]
        name = decode_identifier(frame.split("=New ", 1)[1].split(":", 1)[0].rsplit("_V", 1)[1])
        assert code[pc][1] == code[pc + 1][1] == code[pc + 2][1]
        assert code[target - 1][0] == 16
        assert all(strings[code[at][2]] == frame and code[at + 1][0:3:2] == [12, target] for at in refs)
        assert same_frame is None or strings[same_frame] == frame
        calls.append(dict(record=pc + 1, target=target, frame_sl=sl, name=name,
                          retained_frames=list(refs), same_frame_sl=same_frame, body_evidence=list(traces)))
        text()
        emit(12, target)
        text()

    mirror(multi, 699, 706, 306, {705: 186})
    text()
    assert pc == 227 and "放技能判定.已开启" in strings[code[2848][2]]
    call(2845, traces=(2844, 2846, 2848, 2967))
    text()
    branch(END)
    text()
    branch(301)
    texts(215)
    assert (pc, sl) == (246, 215)
    mirror(raw, 3268, 3298, 2532)
    assert (pc, sl) == (277, 239)
    texts(251)
    branch(301)
    text()
    branch(299)
    texts(256)
    call(5412, same_frame=186, traces=(5505, 5637, 5763))
    texts(261)
    assert (pc, sl) == (302, 261)
    branch(309)
    text()
    assert "检查是否没次数了" in strings[code[6327][2]]
    call(6326, traces=(6327,))
    texts(267)
    branch(318)
    text()
    call(6369, traces=(6372, 6376, 6380, 6388, 6415))
    text()
    jump(367)
    assert (pc, sl) == (318, 272)
    branch(367)
    texts(276)
    assert pc == 323
    branch(362)
    texts(279)
    call(3260, same_frame=171, traces=(3675,))
    texts(283)
    call(2427, (743, 764))
    texts(288)
    call(2446, (546, 3195))
    text()
    branch(349)
    texts(294)
    call(5412, same_frame=186, traces=(5505, 5637, 5763))
    texts(298)
    call(527, same_frame=190, traces=(529,))
    text()
    mirror(multi, 699, 705, 197, {705: 323})
    assert (pc, sl) == (362, 305)
    text()
    call(839, (6414,))
    text()
    assert (pc, sl) == (367, 309) and code[368][0:3:2] == [16, 48]
    jump(231)
    rows = translate(candidate, ((ENTRY, END - 1, "樂園首次打怪與主迴圈"),),
                     external_targets=(186, END, *(c["target"] for c in calls)))["actions"]
    for row in rows:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    assert sorted(r["source_sl"] for r in rows if r["source_sl"] is not None) == list(range(193, 309))
    return dict(module=3, entry=ENTRY, boundary=END, rows=rows, calls=calls, retained_mirrors=mirrors,
                source_program_sha256=digest, original_values_recovered=0)


def verify(plan, previous, base, retained):
    source = base["actions"] + retained["actions"]
    globals_default = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    values_default = {n: 0 for n in scalar_names(source) if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values_default.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    cases = []
    for entry, alt, exhausted, weekly, ready, initial_count, misses in (
            (ENTRY, 0, 0, 0, 0, 0, 0), (ENTRY, 0, 0, 0, 1, 0, 0),
            (231, 1, 0, 0, 0, 0, 0), (231, 1, 0, 2, 0, 1, 3),
            (309, 0, 0, 0, 0, 0, 0), (309, 0, 1, 0, 0, 0, 0),
            (323, 0, 0, 2, 1, 0, 0), (205, 0, 0, 2, 0, 0, 0)):
        shared = dict(globals_default, **{READY: ready, SDK: "AB12CD"})
        values = dict(values_default, **{ALT: alt, EXHAUSTED: exhausted, WEEKLY: weekly, COUNT: initial_count})
        machine = RetainedBattleMachine(base, retained, 0, lambda key, at: shared[key], values)
        machine.pc = entry
        for row in previous["rows"] + plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        records, calls, returns, reads = [], [], [], []
        loop_count = 0
        loop_limit = 2 if entry == 205 else 1
        for _ in range(4000):
            if machine.done or machine.pc == 186 or loop_count == loop_limit or (records and records[-1] == 361):
                break
            if entry == 323 and ready and machine.pc == 355:
                shared[READY] = 1
            event = machine.step()
            at, kind = event["record"], event["kind"]
            records.append(at)
            if at == 367:
                assert machine.pc == 231
                loop_count += 1
            if kind == "call" and 205 <= at < END:
                calls.append([at, event["target"]])
            elif kind == "return" and 205 <= event.get("target", -1) < END:
                returns.append(event["target"])
            elif kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                x, y = event["rect"][:2]
                miss = (at == 251 and len(reads) < misses) or at in (918, 922, 945, 953, 3323)
                coords = (-1, -1) if miss else (x + 1, y + 1)
                if at == 251:
                    reads.append(list(coords))
                if kind.startswith("builtin"):
                    machine.supply_builtin(*coords)
                else:
                    machine.supply_query(*coords, int(kind == "find_color" and not miss))
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
        switch = [[328, 3260], [333, 2427], [339, 2446]]
        if weekly:
            switch.append([347, 5412])
        switch.append([352, 527])
        if entry == ENTRY and ready:
            expected = []
            assert records == [218, 219, 220, 221, 224] and machine.pc == 186
        elif entry == 323:
            expected = switch
            assert records[-5:] == [355, 356, 357, 358, 361] and machine.pc == 323
        else:
            repeat = [[306, 6326], [314, 6369]]
            if entry == 205:
                expected = [[210, 5412], [215, 527], [228, 2845]] + repeat * 2
            elif entry == ENTRY:
                expected = [[228, 2845]] + repeat
            elif alt or exhausted:
                expected = ([[297, 5412]] if alt and initial_count == 1 and weekly else []) + switch + [[364, 839]]
            else:
                expected = [[314, 6369]]
            assert loop_count == loop_limit and machine.pc == 231 and not machine.done
        assert calls == expected, (entry, calls, expected)
        assert returns == [at + 1 for at, _ in calls], (entry, returns)
        if alt:
            assert len(reads) == misses + 1 and reads[:misses] == [[-1, -1]] * misses
            assert [at for at in records if at == 258] == [258] * misses
            assert (273 in records) == bool(misses)
        cases.append(dict(entry=entry, alt=alt, exhausted=exhausted, weekly=weekly, initial_ready=ready,
                          forced_reentry_flag=bool(entry == 323 and ready), main_back_edges=loop_count,
                          count=machine.values[COUNT], root_calls=calls, returned=returns, sdk_reads=reads,
                          records=records, next_record=machine.pc, reason=machine.reason))
    return dict(cases=cases, original_effects_run=False)


def main():
    source = (PROJECT / "programs/03.json").read_bytes()
    raw, digest = json.loads(source), hashlib.sha256(source).hexdigest()
    multi = json.loads((PROJECT / "programs/01.json").read_text("utf8"))
    pool = json.loads((INVENTORY / "03-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(raw, pool, digest, multi)
    previous = entry_routes(raw, pool, digest)
    base, retained = [json.loads((PROJECT / "data" / f"{stem}-03.json").read_text("utf8"))
                      for stem in ("battle", "battle-retained")]
    report = verify(plan, previous, base, retained)
    for name, value in (("battle-paradise-cycle", plan), ("battle-paradise-cycle-verification", report)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} candidates", [(c["entry"], c["next_record"], c["main_back_edges"])
                                              for c in report["cases"]])


if __name__ == "__main__":
    main()
