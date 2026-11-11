"""Join the inferred module 08 initialization to its reviewable mode preview."""
from copy import deepcopy
import hashlib
import json

from build_gathering_dual_bridge import build as build_dual
from build_gathering_mode_gates import OUTPUT, PROJECT, load
from build_gathering_prefix import build as build_prefix, replay
from qmacro_gathering_mode_gates import GatheringModeGateMachine
from qmacro_gathering_retained import GatheringHostMachine
from qmacro_gathering_worker import GatheringGWorker


def build(raw, main, retained, worker):
    prefix = build_prefix()
    dual = build_dual(raw, main)
    digest = prefix["source_program_sha256"]
    if not all(part["source_program_sha256"] == digest for part in (main, retained, worker)):
        raise ValueError("Gathering startup input source hashes differ")
    rows = prefix["rows"]
    assert rows[78 - 7]["kind"] == "if_zero_unresolved"
    rows[78 - 7].update(kind="if_zero", target=90,
                        target_basis="L89 is the trailing worker delay; L90 starts common setup",
                        alternative_target=89)

    # SL77..87 require eleven statement slots. L90..99 alone has ten, and
    # the worker's location has one slot left after its nine-record template.
    code = raw["code"]
    assert [code[pc][1] for pc in range(89, 101)] == [70, *range(74, 84), 85]
    actions = [
        ("Call QMLibrary.Delay(1000)", dict(kind="delay", milliseconds=1000)),
        ("Call QMLibrary.Delay(100)", dict(kind="delay", milliseconds=100)),
        ("XX1=1743.0", dict(kind="initial_assignment", role="minimap_center_x", value=1743.0)),
        ("YY1=168.0", dict(kind="initial_assignment", role="minimap_center_y", value=168.0)),
        ("V88A365757378756D=3.1415926", dict(kind="initial_assignment", role="walk_pi", value=3.1415926)),
        ("V83B4A1CAC292756D=0", dict(kind="initial_assignment", role="no_target_counter", value=0)),
        ("VF6C2D38CB083A2BB4D6A65757378756D=0",
         dict(kind="initial_assignment", role="plant_name_counter", value=0)),
        ("VF299AB9AB083A2BB4D6A65757378756D=0",
         dict(kind="initial_assignment", role="mining_counter", value=0)),
        ("V9AB5ABCE7378756D=0", dict(kind="initial_assignment", role="walk_repeats", value=0)),
        ("V83B4A7B9BAD3756D=0", dict(kind="initial_assignment", role="sdk_miss_count", value=0)),
        ("Call QMLibrary.Delay((100))", dict(kind="delay", milliseconds=100)),
    ]
    for pc, (source, action) in enumerate(actions, 89):
        sl = pc - 12
        assert raw["strings"][sl] == source and code[pc][0] == 255 and pc in raw["missing_records"]
        if action.get("role") not in (None, "no_target_counter", "plant_name_counter"):
            assert main["name_roles"][source.split("=")[0]] == action["role"]
        rows.append(dict(record=pc, location=code[pc][1], sl=sl, source=source, inferred=True, **action))

    assert code[0][0] == 30 and code[6][0] == 29 and code[100][0] == 255
    assert retained["worker_entry"] == prefix["worker_body_candidate"] == 890
    prefix["unresolved"] = [28]
    prefix["end_exclusive"] = 100
    prefix["evidence"]["worker_start"]["limit"] = (
        "The nine-record template ends at L88. L89 is assigned the candidate 1000ms delay from SL77."
    )
    remaining = set(main["required_initial_values"]) - {"walk_repeats", "sdk_miss_count"}
    return {"module": 8, "source_program_sha256": digest, "prefix": prefix,
            "runtime_plan": dual["runtime_plan"], "remaining_initial_inputs": sorted(remaining),
            "original_values_recovered": 0}


def prepare(plan, retained, main, worker, *, remaining_initial, simulation_mode, startup_inputs):
    """Prepare parent/worker event models, preserving distinct unproved inputs."""
    if set(remaining_initial) != set(plan["remaining_initial_inputs"]):
        raise ValueError("Provide exactly the still-unresolved initialization inputs")
    host = GatheringHostMachine(retained, 0)
    host_events = [host.step() for _ in range(7)]
    assert host.pc == 7 and not host.done
    result = replay(plan["prefix"], **startup_inputs)
    if result["stop_at"] != 100:
        raise ValueError("Inferred startup did not reach the gathering mode gates")
    settings = result["settings"]
    context = {
        "gather_mode": settings["mode"], "repair_strategy": settings["repair"],
        "vitality_finish_mode": settings["completion"], "home_on_no_vitality": settings["home_when_no_vigor"],
        "home_on_no_durability": settings["home_when_no_durability"],
        "sdk_marker": settings["sdk_color_candidate"], "simulation_mode": simulation_mode,
        **{key: settings[key] for key in ("minimap_center_x", "minimap_center_y", "walk_pi")},
    }
    if "g_worker_id" in settings:
        context["worker_id"] = settings["g_worker_id"]
    initial = deepcopy(remaining_initial)
    initial.update({key: settings[key] for key in
                    ("walk_repeats", "sdk_miss_count", "no_target_counter", "plant_name_counter", "mining_counter")})
    machine = GatheringModeGateMachine(main, plan["runtime_plan"], context.get, initial)
    worker_machine = GatheringGWorker(worker, context.get) if "worker_id" in context else None
    return host_events + result["events"], machine, worker_machine


def verify(plan, retained, main, worker, fixture):
    cases = []
    for mode in range(11):
        for branch_to_delay in (False, True) if mode == 0 else (False,):
            variant = plan
            if branch_to_delay:
                variant = deepcopy(plan)
                guard = variant["prefix"]["rows"][78 - 7]
                guard["target"] = guard["alternative_target"]
            events, parent, child = prepare(
                variant, retained, main, worker,
                remaining_initial={k: fixture["initial"][k] for k in plan["remaining_initial_inputs"]},
                simulation_mode=0, startup_inputs=dict(
                    version="7.2450", mode=mode, repair=7, completion=2, vigor=1,
                    durability=0, worker_id=4321, random_values=(0.1, 0.5), sdk_value="A1B2C3"))
            launched = mode in (1, 2, 3)
            startup_records = [event["record"] for event in events]
            assert startup_records[:8] == list(range(8))
            assert (89 in startup_records) == (launched or branch_to_delay)
            assert 90 in startup_records and startup_records[-1] == 99
            assert (80 in startup_records) == launched and not ({82, 83, 84} & set(startup_records))
            assert parent.read_context("worker_id") == (4321 if launched else None)
            assert parent.read_context("minimap_center_x") == 1743.0
            assert parent.read_context("minimap_center_y") == 168.0
            assert parent.read_context("walk_pi") == 3.1415926
            assert parent.values["walk_repeats"] == parent.values["sdk_miss_count"] == 0
            if child:
                for _ in range(20):
                    event = child.step()
                    if event["kind"] == "find_color":
                        assert event["record"] == 899 and event["arguments"][4] == "A1B2C3-151515"
                        break
                else:
                    raise AssertionError("G worker failed to request shared marker")

            parent_events = []
            for _ in range(2500):
                if parent.done:
                    break
                event = parent.step()
                parent_events.append(event)
                kind, at = event["kind"], event["record"]
                if kind in ("find_color", "find_pic", "builtin_color"):
                    l, t, _, _ = event["rect"]
                    hit = at not in (116, 279, 445, 457, 609, 621)
                    x, y = (l + 1, t + 2) if hit else (-1, -1)
                    parent.supply_query(x, y, x * 8192 + y if kind == "builtin_color" else int(not hit))
                elif kind == "random_int":
                    parent.supply_random(fixture["random_values"][event["role"]])
                if at in (591, 687):
                    break
            else:
                raise AssertionError("Joined gathering preview exceeded step bound")
            records = [event["record"] for event in parent_events]
            expected = {0: 123, 1: 287, 2: 432, 3: 596}
            assert parent.pc == expected.get(mode, 1626), (mode, parent.pc)
            if mode in (0, 1, 2, 3):
                assert any(event.get("target") == 1344 for event in parent_events if event["kind"] == "call")
            if mode == 2:
                assert 507 in records and 591 in records
            if mode == 3:
                assert 593 in records and 687 in records
            cases.append({"mode": mode, "mode_0_alternate_delay": branch_to_delay,
                          "startup_records": startup_records, "main_records": records,
                          "worker_requested_shared_color": child is not None, "next_record": parent.pc})
    return {"cases": cases, "parent_steps": sum(len(c["startup_records"]) + len(c["main_records"]) for c in cases),
            "original_prefix_executed": False, "real_actions_sent": False}


def main():
    raw = load("programs/08.json")
    main = load("data/gathering-main-suffix.json")
    retained = load("data/gathering-retained.json")
    worker = load("data/gathering-worker.json")
    assert hashlib.sha256((PROJECT / "programs/08.json").read_bytes()).hexdigest() == main["source_program_sha256"]
    result = build(raw, main, retained, worker)
    report = verify(result, retained, main, worker, load("data/gathering-main-cases.json")["cases"][0])
    for name, data in (("gathering-startup-join", result), ("gathering-startup-join-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(report['cases'])} joined cases; {report['parent_steps']} parent steps")


if __name__ == "__main__":
    main()
