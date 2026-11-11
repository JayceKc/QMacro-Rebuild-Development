"""Join battle settings and control flow in an offline replay of each root entry."""
import hashlib
import json

from build_battle_checkbox_setup import replay_checkboxes
from build_battle_first_screen import SDK_SEARCH
from build_battle_startup import replay_startup
from build_cube_prefix import INVENTORY, PROJECT
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

COMMON_PLANS = ("battle-first-screen", "battle-entry-routes")
MODULE_PLANS = {
    1: ("battle-chaos-multi-entry", "battle-chaos-multi-cycle"),
    3: ("battle-paradise-cycle",),
    6: ("battle-chaos-workers", "battle-chaos-first-fight", "battle-chaos-cycle"),
}
# These positions remain original missing records. Assumptions are opt-in.
BODY_FALLTHROUGH = {1: (315, 555), 3: (), 6: (321, 415)}
LOOP_EDGES = {1: (740, 433), 3: (367, 231), 6: (571, 421)}
SETTINGS = {
    1: {"Form1.ComboBox4.ListIndex": 1, "Form1.CheckBox4.Value": 1},
    3: {"Form1.ComboBox4.ListIndex": 1, "Form1.ComboBox1.ListIndex": 2},
    6: {"Form1.ComboBox6.ListIndex": 1},
}
EXTRA_MISSES = {1: {8863, *range(12054, 12079, 4)}, 3: {918, 922, 945, 953, 3323}, 6: set()}


def load_plan(name, module):
    result = json.loads((INVENTORY / f"{name}.json").read_text("utf8"))
    return next(p for p in result if p["module"] == module) if isinstance(result, list) else result


def load_module(module):
    path = PROJECT / "programs" / f"{module:02}.json"
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    missing = set(json.loads(data)["missing_records"])
    startup, checks, *plans = [load_plan(name, module) for name in (
        "battle-startup", "battle-checkbox-setup", *COMMON_PLANS, *MODULE_PLANS[module])]
    next_record, covered = startup["entry"], set()
    for plan in (startup, checks, *plans):
        assert plan["module"] == module and plan["source_program_sha256"] == digest
        assert plan["entry"] == next_record
        next_record = plan["boundary"]
        positions = {row["record"] for row in plan["rows"] if row.get("candidate_opcode") is not None}
        assert positions <= missing and not positions & covered
        covered.update(positions)
    assert missing - covered == set(startup["unresolved"]) | set(BODY_FALLTHROUGH[module]) | ({499, 500} if module == 6 else set())
    base, retained = [json.loads((PROJECT / "data" / f"{name}-{module:02}.json").read_text("utf8"))
                      for name in ("battle", "battle-retained")]
    return startup, checks, plans, base, retained


def replay(module, setup, ui, sdk, *, assume_startup=False, body_assumptions=()):
    startup, checks, plans, base, retained = setup
    assert set(body_assumptions) <= set(BODY_FALLTHROUGH[module])
    shared = {}
    machine = RetainedBattleMachine(base, retained, 0, lambda key, at: shared[key], {})
    prelude = []
    while machine.pc < startup["entry"] and not machine.done:
        prelude.append(machine.step()["record"])
    assert machine.pc == startup["entry"]

    startup_ui = {row["property"]: ui[row["property"]] for row in startup["settings"]}
    startup_case = replay_startup(startup, startup_ui, "7.2450", sdk, 415,
                                  assumed_fallthrough=startup["unresolved"] if assume_startup else ())
    result = dict(module=module, ui=ui, sdk_fixture=sdk,
                  startup_assumptions=startup["unresolved"] if assume_startup else [],
                  body_assumptions=list(body_assumptions),
                  retained_prelude=prelude, startup_records=startup_case["records"])
    if startup_case["next_record"] != startup["boundary"]:
        return dict(result, next_record=startup_case["next_record"], reason="missing_original_record")
    checkbox_ui = {row["property"]: ui[row["property"]] for row in checks["settings"]}
    checked = replay_checkboxes(checks, checkbox_ui, startup_case["shared"], startup_case["local"])
    result.update(checkbox_records=checked["records"], local_at_handoff=checked["local"],
                  shared_at_handoff=checked["shared"])
    if checked["next_record"] != checks["boundary"]:
        assert sdk == "" and checked["records"].count(checks["sdk_wait_loop"]) >= 2
        return dict(result, next_record=checked["next_record"], reason="waiting_for_sdk_color")
    assert checked["next_record"] == plans[0]["entry"]
    assert checked["shared"]["V8186B4D47378756D"] == sdk

    source = base["actions"] + retained["actions"] + [r for p in plans for r in p["rows"]]
    shared = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    shared.update(checked["shared"])
    machine.values.update({n: 0 for n in scalar_names(source)
                           if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))})
    machine.values.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    machine.values.update(checked["local"])
    machine.pc = checked["next_record"]
    for plan in plans:
        for row in plan["rows"]:
            if row.get("candidate_opcode") is not None:
                machine.actions[row["record"]] = row
                del machine.boundaries[row["record"]]
    for at in body_assumptions:
        machine.actions[at] = dict(record=at, kind="jump", target=at + 1)
        del machine.boundaries[at]
    records, root_calls, used_assumptions, looped = [], [], [], False
    edge, destination = LOOP_EDGES[module]
    root_limit = {1: 740, 3: 367, 6: 571}[module]
    for _ in range(6500):
        if machine.done:
            break
        event = machine.step()
        at, kind = event["record"], event["kind"]
        records.append(at)
        if at in body_assumptions:
            used_assumptions.append(at)
        if at == edge:
            assert machine.pc == destination
            looped = True
            break
        if kind == "call" and checked["next_record"] <= at <= root_limit:
            root_calls.append([at, event["target"]])
        elif kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
            x, y = event["rect"][:2]
            hit = at not in EXTRA_MISSES[module]
            coords = (x + 1, y + 1) if hit else (-1, -1)
            if kind.startswith("builtin"):
                machine.supply_builtin(*coords)
            else:
                # The first two startup scans consume DM's zero-on-hit return.
                startup_scan = SDK_SEARCH.get(module, -10)
                returned = int(not hit) if at in (startup_scan, startup_scan + 4) else int(hit and kind == "find_color")
                machine.supply_query(*coords, returned)
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
    return dict(result, records=records, root_calls=root_calls, used_body_assumptions=used_assumptions,
                next_record=machine.pc, reason=machine.reason or ("loop_back" if looped else "step_limit"))


def main():
    cases = []
    for module in MODULE_PLANS:
        setup = load_module(module)
        ui = {row["property"]: 0 for plan in setup[:2] for row in plan["settings"]}
        ui.update(SETTINGS[module])
        startup, checks = setup[:2]
        assumptions = BODY_FALLTHROUGH[module]
        specs = [("AB12CD", False, (), startup["entry"], "missing_original_record"),
                 ("", True, (), None, "waiting_for_sdk_color")]
        specs.extend(("AB12CD", True, assumptions[:i], at, "missing_original_record")
                     for i, at in enumerate(assumptions))
        specs.append(("AB12CD", True, assumptions, LOOP_EDGES[module][1], "loop_back"))
        for sdk, assume_startup, assumed_body, expected, reason in specs:
            result = replay(module, setup, ui, sdk, assume_startup=assume_startup, body_assumptions=assumed_body)
            assert result["retained_prelude"] == list(range(startup["entry"]))
            assert result["reason"] == reason, (module, result["next_record"], result["reason"], expected)
            if expected is not None:
                assert result["next_record"] == expected, (module, result["next_record"], expected)
            else:
                assert checks["sdk_wait_loop"] in result["checkbox_records"] and "records" not in result
            if reason == "loop_back":
                assert result["used_body_assumptions"] == list(assumptions)
                assert result["records"][-1] == LOOP_EDGES[module][0]
                expected_calls = {1: [[380, 10955], [679, 10955]], 3: [[210, 5412]], 6: [[516, 3458]]}
                assert all(call in result["root_calls"] for call in expected_calls[module])
            cases.append(result)
        property_name = {1: "Form1.CheckBox4.Value", 3: "Form1.ComboBox1.ListIndex", 6: "Form1.ComboBox99.ListIndex"}[module]
        alternative = replay(module, setup, dict(ui, **{property_name: int(module == 6)}), "AB12CD",
                             assume_startup=True, body_assumptions=assumptions)
        assert alternative["reason"] == "loop_back"
        removed = {1: [[380, 10955], [679, 10955]], 3: [[210, 5412]], 6: [[516, 3458]]}
        assert all(call not in alternative["root_calls"] for call in removed[module])
        if module == 6:
            assert [521, 3660] in alternative["root_calls"] and alternative["local_at_handoff"]["JCXL"] == 10
        cases.append(alternative)
    path = INVENTORY / "battle-entry-join-verification.json"
    path.write_text(json.dumps(dict(cases=cases, original_effects_run=False), ensure_ascii=False, indent=2) + "\n", "utf8")
    print([(c["module"], c["next_record"], c["reason"]) for c in cases])


if __name__ == "__main__":
    main()
