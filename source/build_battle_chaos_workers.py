"""Infer the first Chaos workers, setup calls and parent ID writes."""
import hashlib
import json

from build_battle_entry_routes import END as PREVIOUS_END
from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier
from export_cube_routines import translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

ENTRY, END = PREVIOUS_END[6], 377
AWAKEN_ID = "VF39FB5A43A3C756D"
DEATH_ID = "VF18ADAADB8B8B89B042E65757378756D"


def build(raw, pool, digest):
    code, strings = raw["code"], raw["strings"]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = ENTRY, 295

    def emit(op, arg):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["missing_records"].remove(pc)
        candidate["code"][pc] = [op, code[pc][1], arg, code[pc][3]]
        pc += 1

    def text(ref):
        assert pool[ref]["index"] == ref and pool[ref]["value"] == strings[ref]
        emit(30 if pool[ref]["kind"] == "decoded-text" else 2, ref)

    def consume():
        nonlocal sl
        text(sl)
        sl += 1

    def group(width):
        assert len({code[at][1] for at in range(pc, pc + width)}) == 1
        assert code[pc - 1][1] != code[pc][1] != code[pc + width][1]

    def worker(callee, name, trace_at, *, shared):
        nonlocal sl
        start = pc
        width = 9 if shared else 7
        group(width + 1)  # The post-launch delay shares the source location.
        original = code[1503:1503 + width]
        assert [r[0] for r in original[:7]] == [24, 16, 2, 12, 23, 2, 2]
        assert original[0][2] == 2 and original[1][2] == 4
        frame_class = strings[sl].split("=New ", 1)[1].split(":", 1)[0]
        assert decode_identifier(frame_class.rsplit("_V", 1)[1]) == name
        assert code[callee - 1][0] == 16 and name in strings[code[trace_at][2]]
        emit(24, 2)
        emit(16, 4)
        consume()
        emit(12, callee)
        emit(23, 0)
        consume()
        if shared:
            assert strings[sl + 1] == DEATH_ID
            text(sl + 2)
            text(sl)
            emit(28, sl + 1)
            sl += 3
        else:
            assert strings[sl].startswith(AWAKEN_ID + "=")
            consume()
        assert pc == start + width
        return dict(start=start, wrapper=start + 2, target=callee, source_trace=trace_at,
                    name=name, shared_id=shared)

    def call(callee, ref=None, trace=None):
        start = pc
        group(3)
        if ref is not None:
            assert strings[sl] == strings[code[ref][2]] and code[ref + 1][0:3:2] == [12, callee]
        else:
            assert code[callee - 1][0] == 16 and "按钮点击进本" in strings[code[trace][2]]
        consume()
        emit(12, callee)
        consume()
        return dict(record=start + 1, target=callee, retained_frame=ref, retained_trace=trace)

    workers = [worker(573, "觉醒", 576, shared=False)]
    consume()
    consume()
    workers.append(worker(669, "监控死亡", 686, shared=True))
    consume()
    consume()
    calls = [call(8754, ref=885)]
    consume()
    calls.append(call(856, trace=857))
    reset_keys = []
    for _ in range(2):
        group(3)
        assert strings[sl + 2].endswith("(1)=0")
        text(sl + 2)
        text(sl)
        emit(28, sl + 1)
        reset_keys.append(strings[sl + 1])
        sl += 3
    assert pc == END and sl == 318
    targets = tuple(s["target"] for s in workers + calls)
    rows = translate(candidate, ((ENTRY, END - 1, "覺醒、死亡監控與進本"),), external_targets=targets)["actions"]
    for row in rows:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    assert sorted(r["source_sl"] for r in rows if r["source_sl"] is not None) == list(range(295, 318))
    return dict(module=6, entry=ENTRY, boundary=END, rows=rows, workers=workers, calls=calls,
                reset_keys=reset_keys, source_program_sha256=digest, original_values_recovered=0)


def verify(plan, base, retained):
    source = base["actions"] + retained["actions"]
    shared_default = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    values = {n: 0 for n in scalar_names(source) if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)

    def replay(entry, shared, *, worker_ids=None, stop_at=None):
        machine = RetainedBattleMachine(base, retained, 0, lambda key, pc: shared[key], values)
        machine.pc = entry
        for row in plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        events = []
        for _ in range(350):
            if machine.done:
                break
            event = machine.step()
            events.append(event)
            at, kind = event["record"], event["kind"]
            if kind == "worker_start":
                machine.supply_worker_id(worker_ids[at])
            elif kind == "write_global":
                shared[event["key"]] = event["value"]
            elif kind == "dm_real_mouse_intent":
                machine.supply_dm_return(1)
            elif kind == "random_int":
                machine.supply_random(event["lower"])
            elif kind == "capture_intent":
                machine.supply_capture_return(1)
            elif kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                x, y = event["rect"][:2]
                if kind.startswith("builtin"):
                    machine.supply_builtin(x + 1, y + 1)
                else:
                    machine.supply_query(x + 1, y + 1, int(kind == "find_color"))
            if at == stop_at:
                break
        return machine, events

    parents, children = [], []
    for awake, dead in ((741, 913), (-4, 0)):
        shared = dict(shared_default, **{key: 88 for key in plan["reset_keys"]})
        m, events = replay(ENTRY, shared, worker_ids={344: awake, 353: dead})
        records = [e["record"] for e in events]
        assert m.done and m.pc == END and m.reason == "missing_original_record"
        assert [e["target"] for e in events if e["kind"] == "worker_start"] == [346, 355]
        assert set(range(346, 349)).isdisjoint(records) and set(range(355, 358)).isdisjoint(records)
        assert m.values[AWAKEN_ID] == awake and shared[DEATH_ID] == dead
        assert [shared[key] for key in plan["reset_keys"]] == [0, 0]
        assert [e["target"] for e in events if e["kind"] == "call" and ENTRY <= e["record"] < END] == [8754, 856]
        assert [e["target"] for e in events if e["kind"] == "return" and ENTRY <= e.get("target", 0) < END] == [366, 370]
        consumer = RetainedBattleMachine(base, retained, 3190, lambda key, pc: shared[key], values)
        consumer_events = [consumer.step() for _ in range(4)]
        assert consumer_events[1]["key"] == DEATH_ID and consumer_events[1]["value"] == dead
        assert consumer_events[-1]["record"] == 3193 and consumer_events[-1]["arguments"] == [dead, 1]
        parents.append(dict(worker_ids=[awake, dead], records=records, next_record=m.pc,
                            isolated_retained_consumer=consumer_events))
    for mode in (0, 1, 2, 3):
        shared = dict(shared_default, VF39FB5A4B9B5C2A84D6A65757378756D=mode)
        stop_at = {0: 585, 2: 630}.get(mode)
        m, events = replay(346, shared, stop_at=stop_at)
        records = [e["record"] for e in events]
        assert events[1]["kind"] == "call" and events[1]["target"] == 573
        assert (585 in records) == (mode == 0) and (630 in records) == (mode == 2)
        if mode == 1:
            assert not m.done and records.count(617) >= 2
        if mode == 3:
            assert m.done and m.reason == "iteration_end"
        children.append(dict(wrapper=346, mode=mode, records=records, next_record=m.pc,
                             reason=m.reason or ("step_limit" if mode == 1 else "observation_checkpoint")))
    for flag in (0, 1):
        shared = dict(shared_default, VF5DEDE9B7378756D=flag)
        m, events = replay(355, shared, stop_at=686)
        records = [e["record"] for e in events]
        assert events[1]["kind"] == "call" and events[1]["target"] == 669
        assert records[-1] == 686 and (685 in records) == bool(flag)
        children.append(dict(wrapper=355, flag=flag, records=records, next_record=m.pc,
                             reason="observation_checkpoint"))
    return dict(parent_cases=parents, child_cases=children, real_parallelism=False, real_actions_sent=False)


def main():
    path = PROJECT / "programs/06.json"
    source = path.read_bytes()
    pool = json.loads((INVENTORY / "06-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(json.loads(source), pool, hashlib.sha256(source).hexdigest())
    base, retained = [json.loads((PROJECT / "data" / f"{stem}-06.json").read_text("utf8"))
                      for stem in ("battle", "battle-retained")]
    report = verify(plan, base, retained)
    for name, value in (("battle-chaos-workers", plan), ("battle-chaos-workers-verification", report)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} candidates; {len(report['parent_cases'])} parent cases; {len(report['child_cases'])} child cases")


if __name__ == "__main__":
    main()
