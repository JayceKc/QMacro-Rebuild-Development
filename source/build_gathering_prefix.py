"""Map preserved module 08 SL data to an explicitly inferred initialization path."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT if (ROOT / "programs/08.json").is_file() else ROOT / "outputs/QMacro-Rebuild-Development"
OUTPUT = ROOT / "analysis/gathering" if PROJECT == ROOT else ROOT / "outputs/gathering-recovery"
INVENTORY = ROOT / ("analysis/initialization" if PROJECT == ROOT else "outputs/initialization-recovery")


def build():
    path = PROJECT / "programs/08.json"
    program = json.loads(path.read_text("utf8"))
    code = program["code"]
    strings = program["strings"]
    inventory = json.loads((INVENTORY / "08-prefix-inventory.json").read_text("utf8"))
    pool = inventory["prefix_pool"]
    rows = []

    def emit(kind, sl=None, target=None):
        pc = len(rows) + 7
        assert pc in program["missing_records"] and code[pc][0] == 255
        row = dict(record=pc, location=code[pc][1], kind=kind)
        if sl is not None:
            assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
            row.update(sl=sl, readable=pool[sl]["readable"])
        if target is not None:
            row["target"] = target
        rows.append(row)

    def text(sl):
        emit("empty_string_slot" if pool[sl]["kind"] == "empty" else "statement", sl)

    def branch(sl, target):
        emit("condition", sl)
        emit("if_zero", target=target)

    def ui(sl, count):
        emit("ui_read", sl)
        for extra in range(1, count):
            text(sl + extra)

    for sl in range(6, 21):
        text(sl)
    branch(21, 26)
    text(22)
    emit("jump", target=27)
    for sl in range(23, 32):
        text(sl)
    for sl in (32, 36, 40):
        ui(sl, 3)
        text(sl + 3)
    text(46)
    text(44)
    emit("shared_write", 45)
    text(47)
    for sl, false_pc, join_pc in ((48, 57, 58), (54, 65, 66)):
        ui(sl, 2)
        branch(sl + 2, false_pc)
        text(sl + 3)
        emit("jump", target=join_pc)
        text(sl + 4)
        text(sl + 5)
    for sl in range(60, 70):
        text(sl)
    emit("condition", 70)
    emit("if_zero_unresolved")  # Branch ends in the erased continuation.
    text(71)
    emit("worker_start", target=82)
    emit("jump", target=85)
    text(72)
    emit("worker_body_candidate", target=890)
    emit("worker_iteration_end")
    text(73)
    text(76)
    text(74)
    emit("shared_write", 75)

    assert [row["record"] for row in rows] == list(range(7, 89))
    assert Counter(row["sl"] for row in rows if "sl" in row) == Counter(range(6, 77))
    for start, end, location in ((22, 23, 23), (35, 37, 36), (39, 41, 38), (43, 45, 40),
                                 (51, 54, 44), (59, 62, 50), (77, 78, 68), (80, 89, 70)):
        assert {code[pc][1] for pc in range(start, end + 1)} == {location}
    expected_template = [24, 16, 2, 12, 23, 2, 2, 2, 28]
    template = json.loads((PROJECT / "programs/07.json").read_text("utf8"))
    assert [row[0] for row in template["code"][717:726]] == expected_template
    assert len({row[1] for row in template["code"][717:726]}) == 1
    frame_class = strings[72].split("=New ", 1)[1].split(":", 1)[0]
    assert code[5][2] == 5 and frame_class in strings[5]
    assert code[889][0] == 16 and code[914][0] == 13
    assert code[917][0] == 27 and strings[code[917][2]] == strings[75]
    assert code[599][0] == 27 and strings[code[599][2]] == strings[45]
    consumers = {34: 593, 38: 921, 42: 1391, 51: 1435, 57: 1152}
    for sl, pc in consumers.items():
        assert code[pc][0] == 4 and strings[sl].split("=", 1)[0] in strings[code[pc][2]]

    evidence = {
        "version_condition": {"reference": "09 reconstructed L26-L30",
                              "limit": "Matching string order and line widths; branch targets inferred."},
        "ui_read": {"reference": "10 original L67-L71 and 09 reconstructed L37-L39",
                    "limit": "Preserved UI read and temp template; module08 property labels from its own SL."},
        "worker_start": {"reference": "07 original L717-L725; 08 declaration L5, body L890-L914, ID read L917",
                         "limit": "Template fits L80-L88 of a ten-record group; L89 remains unresolved."},
        "downstream_settings": consumers,
        "downstream_shared_color_reads": [599, 897],
    }
    return {"module": 8, "source_program_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "entry": 7, "worker_wrapper_entry": 82, "worker_body_candidate": 890,
            "unresolved": [78, 89], "rows": rows, "evidence": evidence,
            "original_records_recovered": 0, "original_records_overwritten": 0}


def replay(plan, *, version, mode, repair, completion, vigor, durability, worker_id, random_values,
           sdk_value=0):
    """Follow inferred branches with explicit inputs and record effect intents."""
    if any(type(value) is not int or not 0 <= value <= 10 for value in (mode, repair, completion)):
        raise ValueError("Expected an index in the retained 0..10 table")
    if any(value not in (0, 1) for value in (vigor, durability)):
        raise ValueError("Expected checkbox values 0 or 1")
    x_sample, y_sample = random_values
    if not (0 <= x_sample < 1 and 0 <= y_sample < 1):
        raise ValueError("Expected two bounded random samples")
    ui = {32: mode, 36: repair, 40: completion, 48: vigor, 54: durability}
    conditions = {21: version == "7.2450", 50: vigor == 1, 56: durability == 1, 70: mode in (1, 2, 3)}
    setting = {34: ("mode", mode), 38: ("repair", repair), 42: ("completion", completion),
               51: ("home_when_no_vigor", 1), 52: ("home_when_no_vigor", 0),
               57: ("home_when_no_durability", 1), 58: ("home_when_no_durability", 0)}
    rows = {row["record"]: row for row in plan["rows"]}
    pc = plan["entry"]
    events = []
    selected = {}
    condition = None
    while pc in rows:
        row = rows[pc]
        event = dict(row)
        events.append(event)
        sl = row.get("sl")
        kind = row["kind"]
        next_pc = pc + 1
        if kind == "condition":
            condition = conditions[sl]
            event["value"] = condition
        elif kind in ("if_zero", "if_zero_unresolved"):
            if not condition:
                if "target" not in row:
                    break
                next_pc = row["target"]
        elif kind == "jump":
            next_pc = row["target"]
        elif kind == "ui_read":
            event["value"] = ui[sl]
        elif kind == "worker_start":
            event["simulated_worker_id"] = worker_id
        elif kind == "initial_assignment":
            selected[row["role"]] = row["value"]
        elif kind == "delay":
            event["milliseconds"] = row["milliseconds"]
        elif sl == 75:
            selected["g_worker_id"] = worker_id
        elif sl == 45:
            selected["sdk_color_candidate"] = sdk_value
        elif sl in setting:
            name, value = setting[sl]
            selected[name] = value
        elif sl == 65:
            event["simulated_coordinates"] = [int(5 * x_sample + 35), int(10 * y_sample + 10)]
        pc = next_pc
    return {"events": events, "settings": selected, "stop_at": pc}


def verify(plan):
    runs = []
    observed = set()
    for mode in range(11):
        for match in (False, True):
            for vigor, durability in ((0, 0), (0, 1), (1, 0), (1, 1)):
                result = replay(plan, version="7.2450" if match else "other", mode=mode,
                                repair=1, completion=2, vigor=vigor, durability=durability,
                                worker_id=4321, random_values=(0.99, 0.0), sdk_value="A1B2C3")
                trace = {event["record"]: event for event in result["events"]}
                assert set(trace).isdisjoint((82, 83, 84))
                assert (24 in trace, 26 in trace) == (match, not match)
                assert result["settings"] == dict(mode=mode, repair=1, completion=2,
                    home_when_no_vigor=vigor, home_when_no_durability=durability, sdk_color_candidate="A1B2C3",
                    **({"g_worker_id": 4321} if mode in (1, 2, 3) else {}))
                assert result["stop_at"] == (89 if mode in (1, 2, 3) else 78)
                move = next(event for event in result["events"] if event.get("sl") == 65)
                assert move["simulated_coordinates"] == [39, 10]
                observed.update(trace)
                runs.append({"mode": mode, "version_match": match, "vigor": vigor, "durability": durability,
                             "stop_at": result["stop_at"], "records": list(trace)})
    return {"cases": runs, "parent_records_observed": len(observed),
            "unexecuted_worker_wrapper": [82, 83, 84],
            "original_runner_prefix_executed": False, "real_effects_sent": False}


def main():
    plan = build()
    report = verify(plan)
    for name, data in (("gathering-prefix-inference", plan), ("gathering-prefix-inference-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['rows'])} mapped positions; {len(report['cases'])} synthetic cases; "
          f"{report['parent_records_observed']} distinct parent records")


if __name__ == "__main__":
    main()
