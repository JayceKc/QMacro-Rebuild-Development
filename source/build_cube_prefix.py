"""Rebuild the cube startup/settings as a traceable, inert event plan."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT if (ROOT / "programs/07.json").is_file() else ROOT / "outputs/QMacro-Rebuild-Development"
INVENTORY = ROOT / ("analysis/initialization" if ROOT == PROJECT else "outputs/initialization-recovery")
OUTPUT = INVENTORY

COMBOS = (
    (1, 58, 61, "emote", ()), (2, 62, 65, "skill_mode", (4796,)),
    (3, 66, 69, "weekly_mode", (896, 935)), (4, 72, 75, "difficulty", (1734,)),
    (5, 78, 81, "run_count", (858, 870)), (6, 84, 87, "first_character", (1749,)),
    (7, 90, 93, "last_character", (5025,)), (8, 96, 99, "completion", (5047,)),
    (9, 102, 105, "potion_mode", (4868,)), (99, 106, 109, "party_mode", (535, 574, 576, 578)),
)
CHECKBOXES = (
    (1, 138, 148, "awakening", 4399), (2, 148, 160, "emote_enabled", 3308),
    (3, 158, 172, "find_head_back", 3614), (4, 168, 184, "guild_task", 915),
)


def build():
    path = PROJECT / "programs/07.json"
    raw = json.loads(path.read_text("utf8"))
    code, strings = raw["code"], raw["strings"]
    pool = json.loads((INVENTORY / "07-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    bindings = json.loads((INVENTORY / "07-ui-bindings.json").read_text("utf8"))["bindings"]
    rows, settings = [], []

    def add(kind, sl=None, **fields):
        pc = 31 + len(rows)
        assert code[pc][0] == 255 and pc in raw["missing_records"]
        action = dict(record=pc, location=code[pc][1], kind=kind, **fields)
        if sl is not None:
            assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
            action.update(sl=sl, source=strings[sl], readable=pool[sl]["readable"])
        rows.append(action)

    def text(sl):
        source = strings[sl]
        delay = re.fullmatch(r"Call QMLibrary.Delay\(\(?(\d+)\)?\)", source)
        if delay:
            add("delay", sl, milliseconds=int(delay[1]))
        else:
            add("statement_intent" if source else "empty_string_slot", sl)

    def same_location(start, width):
        assert len({code[pc][1] for pc in range(start, start + width)}) == 1
        assert code[start - 1][1] != code[start][1] != code[start + width][1]

    def shared_value(rhs_sl, temp_sl, key_sl, role, **fields):
        add("rhs_value", rhs_sl)
        add("set_return_value", temp_sl)
        add("shared_write", key_sl, key=strings[key_sl], role=role, **fields)

    for sl in range(30, 47):
        text(sl)
    same_location(48, 2)
    add("test", 47, condition="version_match")
    add("if_zero", target=52)
    text(48)
    add("jump", target=53)
    for sl in range(49, 58):
        text(sl)
    assert strings[56].split("=", 1)[1] == "ARRAY(" + ",".join(map(str, range(31))) + ")"

    for combo, sl, pc, role, consumers in COMBOS:
        prop = f"Form1.ComboBox{combo}.ListIndex"
        binding = next(b for b in bindings if b["sl"] == sl)
        assert binding["control_exists"] and binding["property"] == strings[sl] == prop
        shared = len(binding["sources"]) == 5
        order = (0, 1, 4, 2, 3) if shared else (0, 1, 2)
        assert binding["sources"] == [sl + index for index in order]
        assert len(rows) + 31 == pc
        same_location(pc, 5 if shared else 3)
        add("ui_read", sl, property=prop)
        add("store_ui_result", sl + 1)
        if shared:
            shared_value(sl + 4, sl + 2, sl + 3, role, from_property=prop)
            key = strings[sl + 3]
        else:
            add("local_write", sl + 2, role=role, from_property=prop)
            key = strings[sl + 2].split("=", 1)[0]
        for use in consumers:
            assert key in strings[code[use][2]]
        settings.append(dict(property=prop, role=role, key=key, shared=shared,
                             source_record=pc, consumer_records=consumers))
        text(sl + (5 if shared else 3))

    assert len(rows) + 31 == 115
    same_location(115, 3)
    shared_value(114, 112, 113, "sdk_marker", supplied_sdk=True)
    sdk_key = strings[113]
    assert code[557][0] == 27 and strings[code[557][2]] == sdk_key
    text(115)
    text(116)
    for pc, sl, label, target in ((120, 117, "sdk_empty", 132), (133, 127, "sdk_sentinel", 147)):
        assert len(rows) + 31 == pc
        same_location(pc, 4)
        add("shared_read", sl, key=sdk_key)
        add("store_shared_result", sl + 1)
        add("test", sl + 2, condition=label)
        add("if_zero", target=target)
        if label == "sdk_sentinel":
            text(130)
            add("unresolved_control")
        loop = len(rows) + 31
        assert loop == (124 if label == "sdk_empty" else 139)
        same_location(loop, 2)
        loop_sl = 120 if label == "sdk_empty" else 131
        add("test", loop_sl, condition="always")
        add("if_zero", target=target, unreachable_with_current_condition=True)
        for delay_sl in range(loop_sl + 1, loop_sl + 6):
            text(delay_sl)
        add("jump", target=loop)
        text(loop_sl + 6)

    for number, sl, pc, role, consumer in CHECKBOXES:
        prop = f"Form1.CheckBox{number}.Value"
        assert strings[sl] == prop and len(rows) + 31 == pc
        same_location(pc, 4)
        same_location(pc + 4, 3)
        same_location(pc + 8, 3)
        add("ui_read", sl, property=prop)
        add("store_ui_result", sl + 1)
        add("test", sl + 2, condition="checked")
        add("if_zero", target=pc + 8)
        shared_value(sl + 5, sl + 3, sl + 4, role, value=1)
        add("jump", target=pc + 11)
        shared_value(sl + 8, sl + 6, sl + 7, role, value=0)
        text(sl + 9)
        key = strings[sl + 4]
        assert key == strings[sl + 7] and code[consumer][0] == 27 and strings[code[consumer][2]] == key
        settings.append(dict(property=prop, role=role, key=key, shared=True,
                             source_record=pc, consumer_records=[consumer]))
    same_location(196, 3)
    same_location(199, 3)
    shared_value(180, 178, 179, "completed_count", value=0)
    shared_value(183, 181, 182, "cleared_count", value=0)
    add("local_write", 184, role="needs_exit", value=0)

    assert [row["record"] for row in rows] == list(range(31, 203))
    assert Counter(row["sl"] for row in rows if "sl" in row) == Counter(range(30, 185))
    assert [code[pc][0] for pc in (723, 724, 725)] == [2, 2, 28]
    return dict(module=7, entry=31, boundary=203, sdk_key=sdk_key, rows=rows, settings=settings,
                source_program_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                unresolved_positions=[57, 138], original_values_recovered=0)


def replay(plan, values, *, version, sdk_value, max_steps=200):
    rows = {row["record"]: row for row in plan["rows"]}
    local, shared, events = {}, {}, []
    pc, condition, ui_value = plan["entry"], False, None
    reason = "step_limit"
    for _ in range(max_steps):
        if pc == plan["boundary"]:
            reason = "next_missing_record"
            break
        row = rows[pc]
        kind = row["kind"]
        event = dict(row)
        events.append(event)
        next_pc = pc + 1
        if kind == "unresolved_control":
            reason = kind
            break
        if kind == "ui_read":
            prop = row["property"]
            ui_value = values[prop]
            upper = 30 if prop.endswith(".ListIndex") else 1
            if type(ui_value) is not int or not 0 <= ui_value <= upper:
                raise ValueError("Invalid input for " + prop)
            event["value"] = ui_value
        elif kind in ("local_write", "shared_write"):
            value = (sdk_value if row.get("supplied_sdk") else
                     values[row["from_property"]] if "from_property" in row else row["value"])
            if kind == "shared_write":
                shared[row["key"]] = value
            else:
                local[row["role"]] = value
            event["value"] = value
        elif kind == "test":
            tests = {"version_match": version == "7.2450", "checked": ui_value == 1, "always": True,
                     "sdk_empty": shared.get(plan["sdk_key"]) == "",
                     "sdk_sentinel": shared.get(plan["sdk_key"]) == "4AD733"}
            condition = tests[row["condition"]]
            event["value"] = condition
        elif kind == "jump" or (kind == "if_zero" and not condition):
            next_pc = row["target"]
        pc = next_pc
    return dict(events=events, local=local, shared=shared, reason=reason, next_record=pc)


def verify(plan):
    cases = []
    for sdk in ("AB12CD", "", "4AD733"):
        for match in (False, True):
            for bits in range(16):
                values = {f"Form1.ComboBox{n}.ListIndex": i for i, (n, *_) in enumerate(COMBOS)}
                values.update({f"Form1.CheckBox{n}.Value": (bits >> (n - 1)) & 1 for n in range(1, 5)})
                run = replay(plan, values, version="7.2450" if match else "other", sdk_value=sdk)
                records = [event["record"] for event in run["events"]]
                assert (50 in records, 52 in records) == (match, not match)
                assert run["shared"][plan["sdk_key"]] == sdk
                if sdk == "":
                    assert run["reason"] == "step_limit" and records.count(124) > 2
                    assert 133 not in records
                elif sdk == "4AD733":
                    assert run["reason"] == "unresolved_control" and run["next_record"] == 138
                    assert 148 not in records
                else:
                    assert run["reason"] == "next_missing_record" and run["next_record"] == 203
                    assert 124 not in records and 138 not in records
                for setting in plan["settings"]:
                    prop = setting["property"]
                    if not prop.endswith(".ListIndex") and sdk != "AB12CD":
                        continue
                    state, key = ((run["shared"], setting["key"]) if setting["shared"]
                                  else (run["local"], setting["role"]))
                    assert state[key] == values[prop]
                cases.append(dict(sdk_case="empty" if not sdk else "sentinel" if sdk == "4AD733" else "fixture",
                                  version_match=match, checkbox_bits=bits, next_record=run["next_record"],
                                  reason=run["reason"], records=records))
    return dict(cases=cases, steps=sum(len(case["records"]) for case in cases),
                original_prefix_executed=False, real_actions_sent=False)


def verify_retained_consumers(plan):
    from replay_cube_retained import build_cases, replay as replay_retained

    tail, main, workers, child = (
        json.loads((PROJECT / "data" / f"{name}.json").read_text("utf8"))
        for name in ("cube-retained-tail", "cube-main", "cube-workers", "cube-routines")
    )
    fixtures = build_cases(tail, workers)
    root = replay_retained(tail, main, workers, child, fixtures[0])
    assert root["records"] == list(range(32)) and root["reason"] == "missing_original_record"
    results = []
    for mode in range(4):
        values = {setting["property"]: 0 for setting in plan["settings"]}
        values["Form1.ComboBox99.ListIndex"] = mode
        prefix = replay(plan, values, version="7.2450", sdk_value="AB12CD")
        fixture = next(item for item in fixtures if item["label"] == f"entry-suffix-mode-{mode}-0")
        # The missing interval has not been executed. Supply its explicit
        # slot/worker fixture values, and observe known retained consumers.
        shared = dict(fixture["shared"], **prefix["shared"])
        suffix = replay_retained(tail, main, workers, child, dict(fixture, shared=shared))
        reads = {event["record"]: event["value"] for event in suffix["events"]
                 if event["kind"] == "read_global"}
        assert reads[574] == reads[576] == reads[578] == mode and reads[557] == "AB12CD"
        results.append(dict(party_mode=mode, shared_reads={pc: reads[pc] for pc in (557, 574, 576, 578)},
                            fixture_root_slot_11=fixture["root_slots"]["11"],
                            retained_records=suffix["records"], boundary=suffix["next_record"]))
    return {"preserved_root_records": root["records"], "controlled_suffix_cases": results,
            "missing_interval_executed": False}


def main():
    plan = build()
    report = verify(plan)
    report["retained_consumer_checks"] = verify_retained_consumers(plan)
    for name, data in (("cube-prefix-inference", plan), ("cube-prefix-inference-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} inferred positions; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
