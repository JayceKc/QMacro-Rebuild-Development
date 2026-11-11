"""Use the intact parallel cube branch to reconstruct the L531 worker handoff."""
from copy import deepcopy
import hashlib
import json
import re

from build_cube_prefix import COMBOS, OUTPUT, PROJECT, build as build_prefix, replay as replay_prefix
from qmacro_cube_retained import CubeRetainedMachine
from replay_cube_retained import build_cases

BASE = 467
END = 531
REF_OFFSET = 193
LOCATION_OFFSET = 145
SL_OFFSET = 167
ROOT_SLOT_OFFSET = 26
ROOT_ARRAY = "F2730835_2229_445E_97C7_l3F761277lDA"


def remap_slots(node):
    if isinstance(node, list):
        return [remap_slots(item) for item in node]
    if not isinstance(node, dict):
        return node
    mapped = {key: remap_slots(value) for key, value in node.items()}
    if "root_slot" in mapped:
        mapped["root_slot"] -= ROOT_SLOT_OFFSET
    if isinstance(mapped.get("name"), str) and mapped["name"].startswith("CUBE_ROOT_SLOT_"):
        index = int(mapped["name"].removeprefix("CUBE_ROOT_SLOT_"))
        mapped["name"] = f"CUBE_ROOT_SLOT_{index - ROOT_SLOT_OFFSET}"
    if mapped.get("kind") == "assign_root_slot":
        mapped["slot"] -= ROOT_SLOT_OFFSET
    return mapped


def build(raw, tail, workers):
    code, strings = raw["code"], raw["strings"]
    reference = {a["record"]: a for plan in (tail, workers) for a in plan["actions"]}
    excluded = {"record", "opcode", "operand", "location", "field_3", "source", "source_sl"}
    rows = []
    for pc in range(BASE, 535):
        ref = reference[pc + REF_OFFSET]
        assert ref["location"] - code[pc][1] == LOCATION_OFFSET
        action = remap_slots({k: v for k, v in ref.items() if k not in excluded})
        if "target" in action and action["kind"] != "call":
            action["target"] -= REF_OFFSET
        sl = ref["source_sl"]
        source = None
        if sl is not None:
            sl -= SL_OFFSET
            source = strings[sl]
            expected = re.sub(re.escape(ROOT_ARRAY) + r"\((\d+)\)",
                              lambda m: ROOT_ARRAY + f"({int(m[1]) - ROOT_SLOT_OFFSET})",
                              ref["source"])
            if pc == 474:
                assert expected == "Call DM.MOVETO(1338+X,225+Y)"
                expected = "Call DM.MOVETO(636+X,865+Y)"
                for expr, const in zip(action["arguments"], (636, 865)):
                    expr["numeric"]["args"][0]["const"] = const
            assert expected == source, (pc, sl)
        if pc >= END:
            original = reference[pc]
            assert original["source_sl"] == sl
            assert action == {k: v for k, v in original.items() if k not in excluded}
        else:
            assert pc in raw["missing_records"] and code[pc][0] == 255
            rows.append(dict(action, record=pc, source_sl=sl, source=source,
                             location=code[pc][1], reference_record=ref["record"],
                             reference_opcode=ref["opcode"], inferred=True))
    assert sorted(row["source_sl"] for row in rows if row["source_sl"] is not None) == [
        sl for sl in range(386, 443) if sl not in (440, 441)]
    return dict(module=7, entry=BASE, worker_entry=526, actions=rows,
                original_values_recovered=0, parallel_reference=[660, 727])


def machine_for(bridge, plans, shared, values, entry):
    if entry not in (bridge["entry"], bridge["worker_entry"]):
        raise ValueError("Unreviewed inferred cube entry")
    tail, main, workers, child = plans
    machine = CubeRetainedMachine(tail, main, workers, child, 0, lambda key, pc: shared[key], values, {})
    actions = {row["record"]: deepcopy(row) for row in bridge["actions"]}
    assert len(actions) == len(bridge["actions"]) and actions.keys() <= machine.boundaries.keys()
    machine.actions.update(actions)
    for pc in actions:
        del machine.boundaries[pc]
    machine.pc = entry
    return machine


def verify(bridge, plans, prefix):
    cases = []
    fixture = build_cases(plans[0], plans[2])[1]
    shared_default = fixture["shared"]
    keys = {row["record"]: row["key"] for row in bridge["actions"] if "key" in row}
    for mode in range(4):
        options = {setting["property"]: 0 for setting in prefix["settings"]}
        options["Form1.ComboBox99.ListIndex"] = mode
        startup = replay_prefix(prefix, options, version="7.2450", sdk_value="AB12CD")
        for hit_set in ("first", "second", "none"):
            shared = dict(shared_default, **startup["shared"])
            shared[keys[506]] = 6200
            machine = machine_for(bridge, plans, shared, fixture["values"], BASE)
            events = []
            for _ in range(160):
                event = machine.step()
                events.append(event)
                pc, kind = event["record"], event["kind"]
                if kind == "random_int":
                    machine.supply_random(event["lower"])
                elif kind == "find_pic":
                    found = (pc == 486 and hit_set == "first") or (pc == 496 and hit_set == "second")
                    x, y = (event["rect"][0] + 1, event["rect"][1] + 1) if found else (-1, -1)
                    machine.supply_query(x, y, int(not found))
                elif kind == "worker_start":
                    machine.supply_worker_id(7300 + mode)
                elif kind == "write_global":
                    shared[event["key"]] = event["value"]
                if pc == 557:
                    break
                assert not machine.done
            else:
                raise AssertionError("Failed to reach retained SDK read")
            records = [event["record"] for event in events]
            created = hit_set != "none" and mode in (0, 1, 3)
            assert (524 in records) == (531 in records) == (532 in records) == created
            assert shared[keys[510]] == int(hit_set != "none")
            assert events[-1]["value"] == "AB12CD"
            control = [e for e in events if e["kind"] == "thread_control_intent"]
            resumed = 547 if hit_set == "none" else 542 if mode == 2 else None
            assert [e["record"] for e in control] == [508] + ([resumed] if resumed else []) + [551]
            assert control[0]["arguments"] == [6200, 2]
            assert {526, 527, 528}.isdisjoint(records)
            if created:
                assert machine.root_slots[10] == machine.root_slots[11] == shared["V8BBFDCD03A3C756D"] == 7300 + mode
            else:
                assert 11 not in machine.root_slots
            cases.append(dict(mode=mode, lucky_match=hit_set, records=records, created_worker=created,
                              worker_id=machine.root_slots.get(11), resumed_record=resumed))

    child = machine_for(bridge, plans, dict(shared_default), fixture["values"], bridge["worker_entry"])
    child_events = []
    for _ in range(40):
        event = child.step()
        child_events.append(event)
        if event["record"] == 6652:
            break
    assert child_events[1]["target"] == 6638 and child.pc == 6639
    assert [event["arguments"][0] for event in child_events if event["kind"] == "key_press"] == ["C", "C"]
    rereads = []
    for values, create in (((2, 2, 2), False), ((3, 2, 2), True), ((2, 1, 2), True), ((2, 2, 0), True)):
        shared = dict(shared_default)
        machine = machine_for(bridge, plans, shared, fixture["values"], BASE)
        machine.pc = 515
        machine.read_global = lambda key, pc: values[{515: 0, 517: 1, 519: 2}[pc]]
        trace = []
        for _ in range(20):
            event = machine.step()
            trace.append(event)
            if event["kind"] == "worker_start":
                machine.supply_worker_id(-17)
            elif event["kind"] == "write_global":
                shared[event["key"]] = event["value"]
            if machine.pc in (533, 535):
                break
        assert (machine.pc == 533) == create
        assert [machine.root_slots[i] for i in (7, 8, 9)] == list(values)
        if create:
            assert shared["V8BBFDCD03A3C756D"] == -17
        rereads.append(dict(observed_party_values=values, worker_created=create,
                            records=[event["record"] for event in trace], next_record=machine.pc))
    return dict(cases=cases, parent_steps=sum(len(case["records"]) for case in cases),
                child_records=[event["record"] for event in child_events], child_next_record=child.pc,
                independent_shared_reread_cases=rereads,
                original_prefix_executed=False, real_actions_sent=False)


def main():
    path = PROJECT / "programs/07.json"
    raw = json.loads(path.read_text("utf8"))
    plans = tuple(json.loads((PROJECT / "data" / f"{name}.json").read_text("utf8")) for name in
                  ("cube-retained-tail", "cube-main", "cube-workers", "cube-routines"))
    prefix = build_prefix()
    bridge = build(raw, plans[0], plans[2])
    bridge["source_program_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert bridge["source_program_sha256"] == prefix["source_program_sha256"]
    report = verify(bridge, plans, prefix)
    for name, data in (("cube-lucky-bridge", bridge), ("cube-lucky-bridge-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(bridge['actions'])} inferred positions; {len(report['cases'])} parent cases; "
          f"{report['parent_steps']} parent steps and {len(report['child_records'])} worker steps")


if __name__ == "__main__":
    main()
