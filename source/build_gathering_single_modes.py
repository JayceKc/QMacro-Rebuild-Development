"""Rebuild the flower/mineral mode branches as a separate, traceable preview."""
from copy import deepcopy
import hashlib
import json
import re

from build_gathering_dual_bridge import known_action, source_references
from build_gathering_mode_gates import OUTPUT, PROJECT, load
from build_gathering_startup_join import build as build_startup, prepare
from qmacro_gathering_walk import Expression


MODES = (
    dict(start=123, end=263, sl=105, sl_end=232, loop=103, sdk_branch=110,
         conditions=(128, 139, 171, 182, 212, 222, 254), condition_sl=(110, 120, 150, 160, 188, 196, 226),
         frame=216, frame_sl=191, slot=4, skips=(168, 209, 250, 261, 262),
         second_miss=164, retry=251, name_count="plant_name_counter"),
    dict(start=286, end=429, sl=249, sl_end=379, loop=266, sdk_branch=273,
         conditions=(292, 305, 337, 348, 378, 388, 420), condition_sl=(255, 267, 297, 307, 335, 343, 373),
         frame=382, frame_sl=338, slot=8, skips=(334, 375, 416, 427, 428),
         second_miss=330, retry=417, name_count="mining_counter"),
)
PLANT = "VF6C2D38CB083A2BB4D6A65757378756D"


def translate(source, exact, roles):
    action = known_action(exact, source)
    if action is not None:
        return action
    if source == f"Sgn({PLANT}>5)":
        return dict(kind="test", condition={"numeric": {"op": ">",
                    "args": [{"name": "plant_name_counter"}, {"const": 5}]}})
    if source == f"{PLANT}={PLANT}+1":
        return dict(kind="assign", role="plant_name_counter", value={"numeric": {"op": "+",
                    "args": [{"name": "plant_name_counter"}, {"const": 1}]}})
    if match := re.fullmatch(r"Call QMLibrary.Delay\(\((\d+)\)\)", source):
        return dict(kind="delay", milliseconds=int(match[1]))
    if source.startswith("Sgn("):
        return dict(kind="test", condition={"numeric": Expression(source).parse()})
    if match := re.fullmatch(r"([A-Za-z0-9_]+)=(.*)", source):
        if match[1] not in roles:
            raise ValueError("Unknown inferred variable " + match[1])
        return dict(kind="assign", role=roles[match[1]], value={"numeric": Expression(match[2]).parse()})
    raise ValueError("Unknown inferred gathering statement " + source)


def build_rows(raw, main, mode):
    code, strings = raw["code"], raw["strings"]
    exact = source_references(main["root_actions"])
    roles = dict(main["name_roles"], **{PLANT: "plant_name_counter"})
    conditions = mode["conditions"]
    skip_icon, skip_name, skip_sdk, back, exit_mode = mode["skips"]
    branch = dict(zip((pc + 1 for pc in conditions),
                      (skip_icon + 1, mode["second_miss"], skip_name + 1, skip_name - 1,
                       skip_sdk, skip_sdk, back)))
    jumps = dict(zip(mode["skips"], (skip_sdk, skip_sdk, back, mode["loop"], 688)))
    text_anchors = dict(zip(conditions, mode["condition_sl"]))
    assert code[mode["second_miss"]][1] - code[mode["second_miss"] - 1][1] == 2
    for pc in conditions:
        assert code[pc - 1][1] != code[pc][1] == code[pc + 1][1] != code[pc + 2][1]
    frame = mode["frame"]
    assert len({code[pc][1] for pc in range(frame, frame + 3)}) == 1
    assert code[frame - 1][1] != code[frame][1] != code[frame + 3][1]
    for inferred, preserved, count in ((skip_icon - 1, 637, 10), (skip_name - 1, 538, 8),
                                        (skip_sdk, 580, 13)):
        expected = [code[i][1] - code[preserved][1] for i in range(preserved, preserved + count)]
        if inferred == 208:
            expected[3:] = [value + 1 for value in expected[3:]]  # One additional location gap.
        assert [code[i][1] - code[inferred][1] for i in range(inferred, inferred + count)] == expected

    rows = []
    sl = mode["sl"]
    for pc in range(mode["start"], mode["end"]):
        assert code[pc][0] == 255 and pc in raw["missing_records"]
        row = dict(record=pc, location=code[pc][1], field_3=code[pc][3], inferred=True)
        if pc in branch:
            row.update(kind="if_zero", target=branch[pc])
            if pc == conditions[1] + 1:
                row["alternative_target"] = mode["second_miss"] + 1
        elif pc in jumps:
            row.update(kind="jump", target=jumps[pc])
        elif pc == frame + 1:
            assert code[547][0] == 12 and code[547][2] == 689
            row.update(kind="call", target=689, reference_record=547)
        else:
            source = strings[sl]
            if pc in text_anchors:
                assert sl == text_anchors[pc] and source.startswith("Sgn(")
            if pc == frame:
                assert sl == mode["frame_sl"] and source == strings[code[546][2]]
            if pc == frame + 2:
                assert source == strings[code[548][2]].replace("(12)", f"({mode['slot']})")
                action = dict(kind="root_store_temp", slot=mode["slot"], reference_record=548)
            else:
                action = translate(source, exact, roles)
            row.update(source_sl=sl, source=source, **action)
            sl += 1
        rows.append(row)
    assert sl == mode["sl_end"]
    assert [r["record"] for r in rows if r["kind"] == "test"] == list(conditions)
    return rows


def build(raw, main, retained, worker):
    session = build_startup(raw, main, retained, worker)
    all_rows = [row for mode in MODES for row in build_rows(raw, main, mode)]
    plan = session["runtime_plan"]
    by_pc = {row["record"]: row for row in plan["actions"]}
    for mode in MODES:
        row = by_pc[mode["sdk_branch"]]
        assert row["kind"] == "if_zero_unresolved"
        row.update(kind="if_zero", target=mode["retry"])
    plan["actions"].extend(all_rows)
    assert {r["record"] for r in session["prefix"]["rows"] + plan["actions"]} == set(raw["missing_records"])
    assert len(all_rows) == 283
    return session, all_rows


def verify(session, retained, main, worker, fixture):
    cases = []
    # Model the name/minimap/SDK thresholds from zero across full loops.
    scenarios = (("icon", 1), ("second_miss", 1), ("second_miss_alternate", 1),
                 ("name", 6), ("minimap", 11), ("empty", 1), ("sdk_miss", 3))
    skip_checks = []
    for number, mode in enumerate(MODES):
        first_icon, second_icon, name, name_count, minimap, walks, sdk_count = mode["conditions"]
        back = mode["skips"][-2]
        for scenario, cycles in scenarios:
            variant = session
            if scenario == "second_miss_alternate":
                variant = deepcopy(session)
                row = next(row for row in variant["runtime_plan"]["actions"] if row["record"] == second_icon + 1)
                row["target"] = row["alternative_target"]
            _, parent, _ = prepare(variant, retained, main, worker,
                remaining_initial={key: fixture["initial"][key] for key in session["remaining_initial_inputs"]},
                simulation_mode=0, startup_inputs=dict(
                    version="7.2450", mode=number, repair=7, completion=2, vigor=1, durability=0,
                    worker_id=4321, random_values=(0.1, 0.5), sdk_value="A1B2C3"))
            observations = {mode["sdk_branch"] - 2: scenario != "sdk_miss",
                            mode["start"] - 7: False, first_icon - 1: scenario.startswith(("icon", "second_miss")),
                            second_icon - 1: scenario == "icon", name - 1: scenario == "name",
                            minimap - 1: scenario == "minimap"}
            tool_repair = number == 1 and scenario == "icon"
            observations[mode["start"] - 7] = tool_repair
            events = []
            finished = 0
            for _ in range(15000):
                event = parent.step()
                events.append(event)
                at, kind = event["record"], event["kind"]
                if kind in ("find_pic", "find_color", "builtin_color"):
                    l, t, _, _ = event["rect"]
                    x, y = (l + 1, t + 2) if observations.get(at, True) else (-1, -1)
                    parent.supply_query(x, y, x * 8192 + y if kind == "builtin_color" else int(x < 0))
                elif kind == "random_int":
                    parent.supply_random(fixture["random_values"][event["role"]])
                if at == back:
                    finished += 1
                    if finished == cycles:
                        break
                assert not parent.done, (scenario, at, parent.reason)
            else:
                raise AssertionError((scenario, parent.pc))
            records = [event["record"] for event in events]
            keys = [event["arguments"][0] for event in events if event["kind"] == "key_press"
                    and mode["start"] <= event["record"] < mode["end"]]
            assert parent.pc == mode["loop"] and len(parent.frames) == 1
            assert (916 in records) == tool_repair
            assert (mode["second_miss"] in records) == (scenario in ("icon", "second_miss"))
            assert (mode["frame"] in records and 689 in records) == (scenario == "minimap")
            assert (name_count + 2 in records) == (scenario == "name")
            assert (walks + 2 in records) == (scenario == "minimap")
            assert (sdk_count + 2 in records) == (scenario == "sdk_miss")
            assert keys.count("Esc") == (scenario == "sdk_miss")
            assert keys.count("Space") == (scenario == "minimap")
            if scenario == "name":
                assert parent.values[mode["name_count"]] == 0 and keys == list("QFEADRS")
            if scenario == "minimap":
                assert parent.values["walk_repeats"] == 5
            cases.append(dict(mode=number, scenario=scenario, cycles=cycles, records=records,
                              inferred_keys=keys, next_record=parent.pc))
        # These two inferred top-level skips are outside the fixed-true
        # loops. Check their joins separately from ordinary entry playback.
        parent.pc = mode["skips"][-1]
        chain = [parent.step()["record"] for _ in range(7)]
        assert chain == [mode["skips"][-1], 688, 889, 915, 1276, 1343, 1621]
        assert parent.step()["record"] == 1625 and parent.pc == 1626 and parent.done
        skip_checks.append(chain + [1625])
    observed = {pc for case in cases for pc in case["records"]}
    return dict(cases=cases, steps=sum(len(c["records"]) for c in cases),
                observed_new_positions=sorted(observed & {pc for mode in MODES for pc in range(mode["start"], mode["end"])}),
                independently_entered_skip_chains=skip_checks,
                original_prefix_executed=False, real_actions_sent=False)


def main():
    raw = load("programs/08.json")
    main = load("data/gathering-main-suffix.json")
    retained = load("data/gathering-retained.json")
    worker = load("data/gathering-worker.json")
    assert hashlib.sha256((PROJECT / "programs/08.json").read_bytes()).hexdigest() == main["source_program_sha256"]
    session, rows = build(raw, main, retained, worker)
    report = verify(session, retained, main, worker, load("data/gathering-main-cases.json")["cases"][0])
    plan = dict(session=session, actions=rows, variants=MODES, original_values_recovered=0)
    for name, data in (("gathering-single-modes", plan), ("gathering-single-modes-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(rows)} inferred positions; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
