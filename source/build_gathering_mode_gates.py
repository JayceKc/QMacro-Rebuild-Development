"""Align inferred gathering mode gates against the module's intact mode 3 gate."""
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path

from qmacro_gathering_mode_gates import GatheringModeGateMachine

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT if (ROOT / "programs/08.json").is_file() else ROOT / "outputs/QMacro-Rebuild-Development"
OUTPUT = PROJECT / "analysis/gathering" if PROJECT == ROOT else ROOT / "outputs/gathering-recovery"
STARTS = ((100, 88), (263, 232), (429, 379))
REFERENCE = 593


def load(name):
    return json.loads((PROJECT / name).read_text("utf8"))


def build(program, source_plan):
    code, strings = program["code"], program["strings"]
    template = {row["record"]: row for row in source_plan["root_actions"]
                if REFERENCE <= row["record"] <= 615}
    groups = [(rows[0][0], len(rows)) for _, run in itertools.groupby(
        enumerate(code), lambda pair: pair[1][1]) if (rows := list(run))]
    size_by_pc = dict(groups)
    widths = [size_by_pc[at] for at in range(593, 616) if at in size_by_pc]
    assert widths == [2, 1, 2, 1, 3, 2, 1, 3, 1, 1, 2, 1, 3]
    matches = [at for index, (at, _) in enumerate(groups) if 7 <= at < 507
               and [size for _, size in groups[index:index + len(widths)]] == widths]
    assert matches == [at for at, _ in STARTS]
    assert code[580][0] == 16 and 580 + code[580][2] == 591
    assert code[591][0] == 16 and 591 + code[591][2] == 432

    actions = []
    for mode, (start, sl_start) in enumerate(STARTS):
        offset = start - REFERENCE
        slot_offset = mode * 4 - 12
        for ref, original in template.items():
            action = deepcopy(original)
            pc = ref + offset
            assert code[pc][0] == 255 and pc in program["missing_records"]
            action.update(record=pc, reference_record=ref, location=code[pc][1],
                          field_3=code[pc][3], inferred=True)
            if action["source_sl"] is not None:
                sl = sl_start + action["source_sl"] - 524
                expected = original["source"]
                if ref == 593:
                    expected = expected.replace("=3)", f"={mode})")
                elif ref in (600, 601, 607, 615):
                    slot = {600: 13, 601: 13, 607: 14, 615: 15}[ref]
                    expected = expected.replace(f"({slot})", f"({slot + slot_offset})")
                assert expected == strings[sl], (mode, ref, sl)
                action.update(source_sl=sl, source=strings[sl])
            if ref == 593:
                action["condition"]["numeric"]["args"][0]["args"][1]["const"] = mode
            elif ref in (594, 597):
                # Mode 3 skips its entire block when its selection is false.
                # The following mode's guard is the inferred join here.
                action["target"] = STARTS[mode + 1][0] if mode < 2 else 593
            elif ref in (600, 607, 615):
                action["slot"] += slot_offset
            elif ref == 601:
                action["spec"]["concat"][0]["root_slot"] += slot_offset
            elif ref == 603:
                if mode == 2:
                    action["target"] = 581
                    action["target_basis"] = "Retained Else-like block L581..L590 and back-edge L591→L432"
                else:
                    action["kind"] = "if_zero_unresolved"
                    del action["target"]
            elif ref == 611:
                action["target"] = start + (23 if mode == 0 else 24)
                action["target_basis"] = "Mode 3 shape and the next matching delay; inferred"
            actions.append(action)
    assert len(actions) == 69
    return {"module": 8, "entries": [at for at, _ in STARTS], "actions": actions,
            "source_program_sha256": source_plan["source_program_sha256"],
            "reference_span": [593, 615], "call_reference": {"vitality": [605, 606, 1344],
                                                              "tool_red": [613, 614, 916]},
            "original_missing_instruction_values_recovered": 0,
            "limits": ["Separate inference over L100–122, L263–285 and L429–451.",
                       "Mode 0 and 1 SDK-miss targets remain unresolved.",
                       "Mode 2 SDK-miss edge to L581 is inferred; L591→L432 is preserved.",
                       "The inferred startup remains disconnected from the original missing entry."]}


def verify(plan, gates, fixture):
    cases = []
    for mode in range(3):
        start = STARTS[mode][0]
        for marker, tool, strategy in ((False, False, 7), (True, False, 7),
                                       (True, True, 7), (True, True, 2)):
            context = dict(fixture["context"], gather_mode=mode, repair_strategy=strategy)
            machine = GatheringModeGateMachine(plan, gates, context.get, fixture["initial"])
            events = []
            for _ in range(2500):
                if machine.done:
                    break
                event = machine.step()
                events.append(event)
                if event["kind"] in ("find_color", "find_pic", "builtin_color"):
                    at = event["record"]
                    hit = marker if at == start + 8 else tool if at == start + 16 else True
                    # Deliberately decouple the supplied DM return code from X/Y.
                    l, t, _, _ = event["rect"]
                    x, y = (l + 1, t + 1) if hit else (-1, -1)
                    machine.supply_query(x, y, x * 8192 + y if event["kind"] == "builtin_color" else int(not hit))
                if machine.pc == 432 and not marker and any(e["record"] == 591 for e in events):
                    break
            else:
                raise AssertionError(f"Preview exceeded bound for mode {mode}")
            calls = [e["target"] for e in events if e["kind"] == "call"]
            assert calls == ([1344] if marker else []) + ([916] if marker and tool else [])
            assert len(machine.frames) == (2 if marker and tool and strategy == 2 else 1)
            root_slots = sorted(machine.frames[0]["slots"])
            slot = 1 + mode * 4
            assert root_slots == [slot] + ([slot + 1] if marker else []) + (
                [slot + 2] if marker and tool and strategy != 2 else [])
            reason = machine.reason
            if not marker:
                assert (machine.pc, reason) == ((432, None) if mode == 2 else (start + 10, "unresolved_sdk_miss_edge"))
            elif tool and strategy == 2:
                assert reason == "script_stop"
            else:
                assert reason == "missing_original_record"
                assert machine.pc == start + (24 if mode and not tool else 23)
            cases.append({"mode": mode, "sdk_hit": marker, "tool_hit": tool,
                          "repair_strategy": strategy, "calls": calls, "root_slots": root_slots,
                          "records": [e["record"] for e in events], "stop_at": machine.pc,
                          "reason": reason or "fixture_stop_after_preserved_back_edge"})
    context = dict(fixture["context"], gather_mode=2)
    machine = GatheringModeGateMachine(plan, gates, context.get,
                                       dict(fixture["initial"], sdk_miss_count=2), entry=429)
    events = []
    for _ in range(40):
        event = machine.step()
        events.append(event)
        if event["kind"] == "find_color":
            machine.supply_query(-1, -1, 1)
        if event["record"] == 591:
            break
    assert machine.pc == 432 and machine.values["sdk_miss_count"] == 0
    assert [event["arguments"][0] for event in events if event["kind"] == "key_press"] == ["Esc"]
    cases.append({"mode": 2, "sdk_hit": False, "initial_sdk_misses": 2,
                  "records": [event["record"] for event in events], "stop_at": 432,
                  "reason": "preserved_esc_threshold_and_back_edge"})
    return {"cases": cases, "event_count": sum(len(case["records"]) for case in cases),
            "observed_inferred_records": sorted({pc for case in cases for pc in case["records"]}
                                                & {action["record"] for action in gates["actions"]}),
            "original_prefix_executed": False, "real_actions_sent": False}


def main():
    raw = load("programs/08.json")
    plan = load("data/gathering-main-suffix.json")
    assert hashlib.sha256((PROJECT / "programs/08.json").read_bytes()).hexdigest() == plan["source_program_sha256"]
    gates = build(raw, plan)
    report = verify(plan, gates, load("data/gathering-main-cases.json")["cases"][0])
    for name, data in (("gathering-mode-gates", gates), ("gathering-mode-gates-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(gates['actions'])} inferred rows; {len(report['cases'])} cases; {report['event_count']} events")


if __name__ == "__main__":
    main()
