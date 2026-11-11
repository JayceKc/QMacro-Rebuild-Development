"""Recover the fishing setup segment anchored by the version and UI groups."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from build_cube_start_workers import decode_identifier
from export_fishing_routines import PROJECT
from qmacro_fishing_retained import FishingRetainedMachine

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ("analysis/fishing" if ROOT == PROJECT else "outputs/fishing-recovery")
INVENTORY = ROOT / ("analysis/initialization" if ROOT == PROJECT else "outputs/initialization-recovery")
ENTRY, ANCHOR = 4, 115


def build(raw, alignment, pool, digest):
    assert alignment["source_sha256"] == digest
    code, strings = raw["code"], raw["strings"]
    rows, settings = [], []

    def add(op, kind, sl=None, **values):
        record = ENTRY + len(rows)
        assert record in raw["missing_records"] and code[record][0] == 255
        row = dict(record=record, location=code[record][1], field_3=code[record][3],
                   candidate_opcode=op, kind=kind, **values)
        if sl is not None:
            assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
            row.update(source_sl=sl, source=strings[sl])
            if op == "text":
                row["candidate_opcode"] = 30 if pool[sl]["kind"] == "decoded-text" else 2
        rows.append(row)

    def text(sl, kind="intent", **values):
        match = re.fullmatch(r"Call QMLibrary.Delay\(\(?(\d+)\)?\)", strings[sl])
        if match:
            kind, values = "delay", {"milliseconds": int(match[1])}
        add("text", kind, sl, **values)

    def condition(sl, test, target):
        add(4, "test", sl, condition=test)
        add(6, "if_zero", target=target)

    def bind(sl, assignment_sl):
        prop = strings[sl]
        key = strings[assignment_sl].split("=", 1)[0]
        assert re.fullmatch(r"V[A-F0-9]+", key)
        setting = dict(property=prop, key=key, original_name=decode_identifier(key[1:]))
        settings.append(setting)
        add(37, "read_ui", sl, property=prop)
        text(sl + 1, "store_ui_slot", slot=1)
        return key

    for sl in range(3, 11):
        kind = {4: "observe_cursor", 8: "observe_sdk"}.get(sl, "intent")
        text(sl, kind)
    condition(11, "sdk_empty", 23)
    condition(12, "always", 23)
    for sl in range(13, 19):
        text(sl)
    add(16, "jump", target=14)
    condition(19, "sdk_sentinel", 36)
    text(20)
    add(None, "unresolved_control")
    condition(21, "always", 36)
    for sl in range(22, 28):
        text(sl)
    add(16, "jump", target=27)
    for sl in range(28, 42):
        text(sl)
    condition(42, "version", 54)
    text(43, "trace", message="成功")
    add(16, "jump", target=55)
    text(44, "trace", message="失敗")
    for sl in range(45, 51):
        text(sl)
    for sl in (51, 55):
        key = bind(sl, sl + 2)
        text(sl + 2, "select", key=key)
        text(sl + 3)
    for i in range(5):
        sl, at = 59 + 6 * i, 69 + 8 * i
        assert ENTRY + len(rows) == at
        key = bind(sl, sl + 3)
        assert strings[sl + 3] == f"{key}=1" and strings[sl + 4] == f"{key}=0"
        condition(sl + 2, "checked", at + 6)
        text(sl + 3, "set", key=key, value=1)
        add(16, "jump", target=at + 7)
        text(sl + 4, "set", key=key, value=0)
        text(sl + 5)
    for sl in range(89, 95):
        if sl in (89, 91):
            key, value = strings[sl].split("=")
            text(sl, "set", key=key, value=int(value))
        else:
            text(sl)
    assert ENTRY + len(rows) == ANCHOR
    assert Counter(r["source_sl"] for r in rows if "source_sl" in r) == Counter(range(3, 95))
    by_record = {row["record"]: row for row in rows}
    source_cursor = 3
    for group in alignment["groups"]:
        if not ENTRY <= group["records"][0] < ANCHOR:
            continue
        expected = [by_record[at].get("source_sl") for at in group["records"]]
        next_cursor = source_cursor + sum(sl is not None for sl in expected)
        assert any(c["source_range"] == [source_cursor, next_cursor]
                   and [r["source_sl"] for r in c["instructions"]] == expected
                   for c in group["candidates"]), (group["records"], expected)
        source_cursor = next_cursor
    assert source_cursor == 95
    assert code[539][0] == 5 and code[539][2] == ANCHOR
    assert strings[95].startswith("DM_RET=DM.FINDCOLOR(956,466,963,499,")
    return dict(module=5, entry=ENTRY, boundary=ANCHOR, rows=rows, settings=settings,
                source_program_sha256=digest, original_values_recovered=0, unresolved_records=[26],
                retained_restart=dict(record=539, target=ANCHOR, candidate_first_statement_sl=95))


def replay(plan, ui, version, sdk, cursor, *, enter_sentinel_loop=False):
    rows = {row["record"]: row for row in plan["rows"]}
    pc, state, events = plan["entry"], {}, []
    reason = "step_limit"
    for _ in range(160):
        if pc == plan["boundary"]:
            reason = "candidate_boundary"
            break
        row = rows[pc]
        event, kind = dict(row), row["kind"]
        pc += 1
        if kind == "unresolved_control" and not enter_sentinel_loop:
            reason = kind
            pc -= 1
            events.append(event)
            break
        if kind == "observe_cursor":
            state.update(MX=cursor[0], MY=cursor[1])
        elif kind == "observe_sdk":
            state["V8186B4D47378756D"] = sdk
        elif kind == "read_ui":
            current = ui[row["property"]]
            upper = 10 if row["property"].endswith(".ListIndex") else 1
            if type(current) is not int or not 0 <= current <= upper:
                raise ValueError("Invalid fishing UI value")
        elif kind == "store_ui_slot":
            slot = current
        elif kind == "test":
            check = row["condition"]
            if check == "checked":
                flag = slot == 1
            else:
                flag = {"version": version == "7.2450", "sdk_empty": sdk == "",
                        "sdk_sentinel": sdk == "4AD733", "always": True}[check]
        elif kind == "jump" or (kind == "if_zero" and not flag):
            pc = row["target"]
        elif kind == "set":
            state[row["key"]] = row["value"]
        elif kind == "select":
            state[row["key"]] = slot  # Source array is exactly 0 through 10.
        events.append(event)
    return events, state, pc, reason


def verify(plan, routines, retained):
    rebait = plan["settings"][2]["key"]
    assert retained["suffix_roles"][rebait] == "rebait"
    cases, tail = [], {}
    for version in ("7.2450", "7.2400"):
        for mask in range(32):
            options = [mask % 11, (10 - mask) % 11] + [(mask >> i) & 1 for i in range(5)]
            ui = {s["property"]: value for s, value in zip(plan["settings"], options)}
            events, state, pc, reason = replay(plan, ui, version, "AB12CD", (314, 256))
            assert (pc, reason) == (ANCHOR, "candidate_boundary")
            assert [state[s["key"]] for s in plan["settings"]] == options
            assert state["CS"] == state["VF89CA4BECFC0C1A34D6A65757378756D"] == 0
            assert [e["record"] for e in events if e["kind"] == "trace"] == [52 if version == "7.2450" else 54]
            cases.append(dict(version=version, ui=ui, state=state, records=[e["record"] for e in events]))
            if state[rebait] in tail:
                continue
            context = {"saved_cursor_x": state["MX"], "saved_cursor_y": state["MY"], "simulation_mode": 0}
            # The missing intervening body is not executed. Carry only the
            # setup value that the preserved restart reads, plus explicit fixtures.
            machine = FishingRetainedMachine(routines, retained, context.get, 504,
                                             initial={"rebait": state[rebait], "failure_count": 0, "cycle_count": 13})
            trace = []
            for _ in range(40):
                event = machine.step()
                trace.append(event)
                if event["kind"] == "find_color":
                    x, y = event["rect"][:2]
                    machine.supply_query(x + 1, y + 1, 0)
                if machine.done:
                    break
            assert machine.pc == ANCHOR and machine.reason == "missing_original_record"
            assert any(e["record"] == 532 for e in trace) == bool(state[rebait])
            assert any(e["record"] == 535 and e["arguments"] == [314, 256] for e in trace)
            assert machine.values["cycle_count"] == 0
            tail[state[rebait]] = trace
    waits = []
    for sdk, assume, back in (("", False, 22), ("4AD733", False, None), ("4AD733", True, 35)):
        events, _, pc, reason = replay(plan, {}, "7.2450", sdk, (314, 256), enter_sentinel_loop=assume)
        records = [e["record"] for e in events]
        assert 36 not in records
        if back is None:
            assert (pc, reason) == (26, "unresolved_control")
        else:
            assert reason == "step_limit" and records.count(back) > 2
        waits.append(dict(sdk=sdk, assumed_l26_fallthrough=assume, records=records, next_record=pc, reason=reason))
    assert {at for c in cases + waits for at in c["records"]} == set(range(ENTRY, ANCHOR))
    return dict(cases=cases, wait_cases=waits, isolated_retained_restart=tail, original_values_recovered=0,
                intervening_original_body_executed=False, real_actions_sent=False)


def main():
    path = PROJECT / "programs/05.json"
    raw = json.loads(path.read_text("utf8"))
    alignment = json.loads((OUT / "prefix-structured-alignment.json").read_text("utf8"))
    pool = json.loads((INVENTORY / "05-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    plan = build(raw, alignment, pool, hashlib.sha256(path.read_bytes()).hexdigest())
    routines, retained = [json.loads((PROJECT / "data" / f"fishing-{name}.json").read_text("utf8"))
                          for name in ("routines", "retained")]
    report = verify(plan, routines, retained)
    for name, data in (("fishing-startup", plan), ("fishing-startup-verification", report)):
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows']) - len(plan['unresolved_records'])} candidate operations; "
          f"{len(plan['unresolved_records'])} unresolved; {len(report['cases'])} setup cases; "
          f"{len(report['wait_cases'])} wait cases; {len(report['isolated_retained_restart'])} retained restarts")


if __name__ == "__main__":
    main()
