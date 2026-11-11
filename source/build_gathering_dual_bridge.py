"""Connect the inferred mode 2 icon/name branches to retained module 08 code."""
from copy import deepcopy
import hashlib
import json
import re

from build_gathering_mode_gates import OUTPUT, PROJECT, build as build_gates, load
from export_fishing_routines import arguments
from qmacro_gathering_mode_gates import GatheringModeGateMachine


def source_references(retained):
    exact = {}
    for row in retained:
        if row.get("source") is not None:
            exact.setdefault(row["source"], []).append(row)
    return exact


def known_action(exact, source):
    refs = exact.get(source, [])
    if refs:
        evidence = {"record", "location", "field_3", "opcode", "source_sl", "source"}
        actions = [{k: v for k, v in ref.items() if k not in evidence} for ref in refs]
        assert all(action == actions[0] for action in actions), source
        return dict(deepcopy(actions[0]), reference_record=refs[0]["record"])
    query = re.fullmatch(r"DM_RET=DM\.(FINDPIC|FINDCOLOR)\((.*)\)", source)
    if query:
        args = arguments(query[2])
        picture = query[1] == "FINDPIC"
        assert len(args) == (10 if picture else 9) and args[-2:] == ["INTXX", "INTYY"]
        assert args[4][0] == args[4][-1] == '"'
        action = dict(kind="find_pic" if picture else "find_color",
                      rect=list(map(int, args[:4])), spec={"const": args[4][1:-1]},
                      similarity=float(args[-4]), direction=int(args[-3]), out_roles=["target_x", "target_y"])
        if picture:
            assert args[5][0] == args[5][-1] == '"'
            action["delta"] = {"const": args[5][1:-1]}
        return action
    if match := re.fullmatch(r'Call QMLibrary.TracePrint\(\("(.*)"\)\)', source):
        return dict(kind="trace", value={"const": match[1]})
    return None


def build(raw, main):
    code, strings = raw["code"], raw["strings"]
    retained = {row["record"]: row for row in main["root_actions"]}
    exact = source_references(retained.values())
    branch = {
        459: (499, "Analogous preserved mode 3 icon-miss L623→L639"),
        470: (494, "Location gap before L494; alternative is L495"),
        498: (580, "Analogous mode 3 skip L638→L676; L580 then jumps to original L591"),
        502: (540, "Analogous mode 3 name-miss L642→L666; retained mode 2 minimap starts at L540"),
    }
    expected_locations = [code[pc][1] - code[497][1] for pc in range(497, 508)]
    assert expected_locations == [code[pc][1] - code[637][1] for pc in range(637, 648)]
    assert [code[pc][1] == code[pc - 1][1] for pc in range(453, 507)].count(True) == 3
    assert all(code[pc][1] == code[pc - 1][1] for pc in (459, 470, 502))
    assert code[507][2] == 447 and code[507][0] == 30

    rows = []
    sl = 396
    for pc in range(452, 507):
        row = {"record": pc, "location": code[pc][1], "field_3": code[pc][3], "inferred": True}
        assert code[pc][0] == 255 and pc in raw["missing_records"]
        if pc in branch:
            target, basis = branch[pc]
            row.update(kind="jump" if pc == 498 else "if_zero", target=target, target_basis=basis)
            if pc == 470:
                row["alternative_target"] = 495
        else:
            source = strings[sl]
            row.update(source_sl=sl, source=source)
            action = known_action(exact, source)
            if action is None:
                raise ValueError((pc, sl, source))
            row.update(action)
            sl += 1
        rows.append(row)
    assert sl == 447 and len(rows) == 55
    assert [row.get("source_sl") for row in rows if row["kind"] == "test"] == [402, 412, 442]
    assert rows[506 - 452]["source"] == retained[646]["source"]
    gates = build_gates(raw, main)
    gates["actions"].extend(rows)
    return {"module": 8, "actions": rows, "runtime_plan": gates,
            "source_program_sha256": main["source_program_sha256"],
            "retained_join_points": [507, 540, 580, 591],
            "original_values_recovered": 0}


def verify(main, bridge, fixture):
    cases = []
    variants = ((True, True, False, False, True, False), (True, False, False, False, False, False),
                (False, False, True, False, False, False), (False, False, False, False, False, False),
                (False, False, False, True, False, False), (True, False, False, False, False, True))
    for icon, icon_again, name, minimap, tool, alternate in variants:
        context = dict(fixture["context"], gather_mode=2, repair_strategy=7)
        gate_plan = bridge["runtime_plan"]
        if alternate:
            gate_plan = deepcopy(gate_plan)
            second_miss = next(row for row in gate_plan["actions"] if row["record"] == 470)
            second_miss["target"] = second_miss["alternative_target"]
        machine = GatheringModeGateMachine(main, gate_plan, context.get, fixture["initial"], entry=429)
        outcomes = {457: icon, 468: icon_again, 500: name, 541: minimap, 445: tool}
        events = []
        for _ in range(2500):
            event = machine.step()
            events.append(event)
            kind, at = event["kind"], event["record"]
            if kind in ("find_pic", "find_color", "builtin_color"):
                l, t, _, _ = event["rect"]
                x, y = ((l + 1, t + 2) if outcomes.get(at, True) else (-1, -1))
                reply = x * 8192 + y if kind == "builtin_color" else int(x < 0)
                machine.supply_query(x, y, reply)
            elif kind == "random_int":
                machine.supply_random(fixture["random_values"][event["role"]])
            if at == 591:
                break
            assert not machine.done, (at, machine.reason)
        else:
            raise AssertionError("Mode 2 bridge exceeded step bound")
        records = [event["record"] for event in events]
        keys = [event["arguments"][0] for event in events
                if event["record"] in range(452, 507) and event["kind"] == "key_press"]
        expected = (["G", "G"] if icon else []) + (list("QFEADRS") if icon_again else [])
        assert keys == expected and machine.pc == 432 and len(machine.frames) == 1
        assert (507 in records) == (not icon and name)
        assert (540 in records) == (not icon and not name)
        assert (689 in records) == minimap
        assert (916 in records) == tool and (452 in records) == tool
        assert (494 in records) == (icon and not alternate)
        if icon:
            assert machine.values["fallback_attempts"] == machine.values["walk_repeats"] == 0
        cases.append({"icon_hit": icon, "second_icon_hit": icon_again, "name_hit": name,
                      "minimap_hit": minimap, "tool_hit": tool, "second_miss_alternative": alternate,
                      "inferred_keys": keys, "records": records,
                      "next_record": machine.pc})
    return {"cases": cases, "steps": sum(len(case["records"]) for case in cases),
            "covered_inferred_positions": sorted({record for case in cases for record in case["records"]}
                                                & set(range(452, 507))),
            "original_prefix_executed": False, "real_actions_sent": False}


def main():
    raw = load("programs/08.json")
    plan = load("data/gathering-main-suffix.json")
    assert hashlib.sha256((PROJECT / "programs/08.json").read_bytes()).hexdigest() == plan["source_program_sha256"]
    bridge = build(raw, plan)
    report = verify(plan, bridge, load("data/gathering-main-cases.json")["cases"][0])
    for name, data in (("gathering-dual-bridge", bridge), ("gathering-dual-bridge-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(bridge['actions'])} inferred positions; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
