"""Align the common battle setup without running legacy file or DLL operations."""
import hashlib
import json
import re

from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier

SPECS = {
    1: dict(entry=62, worker_reference=1655, worker_body=11725, boundary=163, last_sl=153),
    3: dict(entry=40, worker_reference=858, worker_body=5885, boundary=122, last_sl=112),
    6: dict(entry=56, worker_reference=1503, worker_body=8621, boundary=164, last_sl=147),
}
SDK = "V8186B4D47378756D"
ROOT_QUALIFIER = "F2730835_2229_445E_97C7_l3F7612771DA."


def build(program, inventory, bindings, digest):
    module = program["module"]
    spec = SPECS[module]
    code, strings = program["code"], program["strings"]
    pool = inventory["prefix_pool"]
    pc, sl = spec["entry"], spec["entry"] - 1
    rows, settings = [], []
    loader = sl - 1
    missing = set(program["missing_records"])

    def add(op, kind, ref=None, **extra):
        nonlocal pc
        assert pc in missing and code[pc][0] == 255
        if ref is not None:
            assert pool[ref]["index"] == ref and pool[ref]["value"] == strings[ref]
        rows.append(dict(record=pc, location=code[pc][1], field_3=code[pc][3],
                         candidate_opcode=op, kind=kind, source_sl=ref,
                         source=strings[ref] if ref is not None else None, inferred=True, **extra))
        pc += 1

    def text(ref, kind="intent", **extra):
        add(30 if pool[ref]["kind"] == "decoded-text" else 2, kind, ref, **extra)

    def consume(kind="intent", **extra):
        nonlocal sl
        text(sl, kind, **extra)
        sl += 1

    def group(size):
        assert len({code[at][1] for at in range(pc, pc + size)}) == 1
        assert code[pc + size][1] != code[pc][1]

    add(None, "unknown_entry")
    group(2)
    assert strings[loader].startswith("FILE\nIf IsEmpty(FILE)")
    add(31, "load_file_intent", loader)
    consume("create_folder_intent")
    consume("delay")
    worker = pc
    ref = spec["worker_reference"]
    width = 7 if module == 3 else 9
    group(width)
    ops = [r[0] for r in code[ref:ref + width]]
    assert ops == [24, 16, 2, 12, 23, 2] + ([2] if module == 3 else [2, 2, 28])
    assert code[ref][2] == 2 and code[ref + 1][2] == 4 and code[ref + 3][2] == spec["worker_body"]
    add(24, "worker_start", target=worker + 2)
    add(16, "jump", target=worker + 5)
    assert strings[sl] == strings[code[ref + 2][2]]
    worker_class = strings[sl].split("=New ", 1)[1].split(":", 1)[0]
    assert decode_identifier(worker_class.rsplit("_V", 1)[1]) == "重启小功能"
    consume("worker_frame")
    add(12, "worker_call", target=spec["worker_body"])
    add(23, "worker_end")
    assert strings[sl] == strings[code[ref + 5][2]].replace(ROOT_QUALIFIER, "")
    consume("worker_id_slot")
    if module == 3:
        assert strings[sl] == strings[code[ref + 6][2]].replace(ROOT_QUALIFIER, "")
        consume("write_worker_id", key=strings[sl].split("=", 1)[0], shared=False)
    else:
        assert [strings[i] for i in (sl + 2, sl, sl + 1)] == [
            strings[code[at][2]].replace(ROOT_QUALIFIER, "") for at in range(ref + 6, ref + 9)]
        text(sl + 2, "copy_worker_id")
        text(sl, "read_worker_id")
        add(28, "write_worker_id", sl + 1, key=strings[sl + 1], shared=True)
        sl += 3
    consume("delay")
    consume("open_log_intent")
    consume("delay")
    callback = None
    if module == 6:
        assert (pc, sl) == (72, 65)
        add(16, "jump", target=87)
        callback = [dict(record=at, opcode=op, source_sl=arg if op != 13 else None,
                         source=strings[arg] if op != 13 else None)
                    for at, (op, _, arg, _) in enumerate(code[73:87], 73)]
        assert [row["opcode"] for row in callback] == [2] + [31, 30] * 5 + [30, 2, 13]
        assert all("FILE.DELETEFOLDER(" in row["source"] for row in callback[2:12:2])
        pc, sl = 87, 73
    while not strings[sl].startswith("Sgn("):
        consume()
    assert strings[sl] == "Sgn((VFD8CD4CB7378756D=7.2450))"
    version_at = pc
    group(2)
    add(4, "version_test", sl)
    sl += 1
    add(6, "if_version_mismatch", target=version_at + 4)
    consume("version_success")
    add(16, "jump", target=version_at + 5)
    consume("version_failure")
    while not strings[sl].startswith("Form1."):
        if strings[sl]:
            consume()
        else:
            add(None, "empty_source", sl)
            sl += 1

    known = {b["sl"]: b for b in bindings["bindings"]}

    def shared_write(index, prop=None, sdk=False):
        text(index + 2, "prepare_setting", property=prop)
        text(index, "read_setting")
        add(28, "sdk_write" if sdk else "setting_write", index + 1,
            key=strings[index + 1], property=prop, shared=True)

    while sl <= spec["last_sl"]:
        source = strings[sl]
        if source.startswith("Form1."):
            binding = known[sl]
            width = 5 if binding["classification"] == "direct_shared_dataflow" else 3
            group(width)
            add(37, "read_ui", sl, property=source)
            text(sl + 1, "ui_slot")
            if width == 5:
                shared_write(sl + 2, source)
            else:
                text(sl + 2, "setting_write", key=strings[sl + 2].split("=")[0], property=source, shared=False)
            settings.append(dict(property=source, source_sl=sl))
            sl += width
        elif "GetGlobalVar" in strings[sl + 2] and strings[sl + 1] == SDK:
            group(3)
            shared_write(sl, sdk=True)
            sl += 3
        elif module == 6 and "FORM1.COMBOBOX4.LISTINDEX" in strings[sl + 2]:
            group(3)
            prop = "Form1.ComboBox4.ListIndex"
            shared_write(sl, prop)
            settings.append(dict(property=prop, source_sl=sl + 2))
            sl += 3
        elif match := re.search(r"FORM1\.COMBOBOX(\d+)\.LISTINDEX", source):
            prop = f"Form1.ComboBox{match[1]}.ListIndex"
            consume("setting_write", key=source.split("=")[0], property=prop, shared=False)
            settings.append(dict(property=prop, source_sl=sl - 1))
        else:
            consume()
    assert pc == spec["boundary"] and sl == spec["last_sl"] + 1
    assert {r["record"] for r in rows} == missing & set(range(spec["entry"], pc))
    by_key = {r["property"]: r for r in rows if r["kind"] == "setting_write"}
    for setting in settings:
        key = by_key[setting["property"]]["key"]
        setting.update(key=key, original_name=decode_identifier(key[1:]), shared=by_key[setting["property"]]["shared"])
    root_unresolved = [r["record"] for r in rows if r["kind"] in ("unknown_entry", "empty_source")]
    return dict(module=module, entry=spec["entry"], boundary=pc, rows=rows, settings=settings,
                version_at=version_at, worker_reference=ref, worker_record=worker,
                worker_class=worker_class, worker_entry=worker + 2, worker_body=spec["worker_body"],
                retained_callback=callback, unresolved=root_unresolved,
                source_program_sha256=digest, original_values_recovered=0)


def replay_startup(plan, ui, version, sdk, worker_id, *, assumed_fallthrough=()):
    rows = {r["record"]: r for r in plan["rows"]}
    pc, records, local, shared = plan["entry"], [], {}, {}
    for _ in rows:
        if pc == plan["boundary"]:
            break
        row = rows[pc]
        records.append(pc)
        if row["candidate_opcode"] is None and pc not in assumed_fallthrough:
            break
        pc += 1
        kind = row["kind"]
        if kind == "jump" or kind == "if_version_mismatch" and version != "7.2450":
            pc = row["target"]
        elif kind == "write_worker_id":
            (shared if row["shared"] else local)[row["key"]] = worker_id
        elif kind == "setting_write":
            (shared if row["shared"] else local)[row["key"]] = ui[row["property"]]
        elif kind == "sdk_write":
            shared[row["key"]] = sdk
    return dict(version=version, ui=ui, records=records, local=local, shared=shared, next_record=pc)


def verify(plan):
    cases = []
    rows = {r["record"]: r for r in plan["rows"]}
    for version in ("7.2450", "7.2400"):
        for offset in (0, 1, 3):
            ui = {s["property"]: (i + offset) % 4 for i, s in enumerate(plan["settings"])}
            case = replay_startup(plan, ui, version, "AB12CD", 415, assumed_fallthrough=plan["unresolved"])
            records, local, shared = (case[key] for key in ("records", "local", "shared"))
            assert case["next_record"] == plan["boundary"] and shared[SDK] == "AB12CD"
            traces = [rows[at]["kind"] for at in records if rows[at]["kind"] in ("version_success", "version_failure")]
            assert traces == ["version_success" if version == "7.2450" else "version_failure"]
            assert all(at not in records for at in range(plan["worker_record"] + 2, plan["worker_record"] + 5))
            assert plan["module"] != 6 or not set(records).intersection(range(73, 87))
            writes = {r["property"]: (shared if r["shared"] else local)[r["key"]]
                      for r in plan["rows"] if r["kind"] == "setting_write"}
            assert writes == ui
            cases.append(dict(version=version, ui=ui, records=records, local=local, shared=shared))
    child = plan["worker_entry"]
    assert [rows[at]["kind"] for at in range(child, child + 3)] == ["worker_frame", "worker_call", "worker_end"]
    assert rows[child + 1]["target"] == plan["worker_body"]
    return dict(cases=cases, fallthrough_assumptions=plan["unresolved"],
                child_wrapper=list(range(child, child + 3)), original_effects_run=False)


def main():
    plans, checks = [], []
    callback_report = json.loads((PROJECT / "verification/original-callback-vm-test.json").read_text("utf8"))
    callback = next(item for item in callback_report["callbacks"] if item["module"] == 6)
    assert callback_report["ok"] and callback["filesystem_deletions"] == 0
    for module in SPECS:
        tag = f"{module:02}"
        source = (PROJECT / "programs" / f"{tag}.json").read_bytes()
        inventory = json.loads((INVENTORY / f"{tag}-prefix-inventory.json").read_text("utf8"))
        bindings = json.loads((INVENTORY / f"{tag}-ui-bindings.json").read_text("utf8"))
        plan = build(json.loads(source), inventory, bindings, hashlib.sha256(source).hexdigest())
        plans.append(plan)
        verification = verify(plan)
        if module == 6:
            rows = plan["retained_callback"]
            paths = [row["source"].split('"')[1] for row in rows if row["source"] and "FILE.DELETEFOLDER(" in row["source"]]
            assert (callback["entry"], callback["last"]) == (rows[0]["record"], rows[-1]["record"])
            assert callback["delete_intents"] == paths * 2
            assert all(o["frame_restored"] and o["return_pc"] == 10254 for o in callback["observations"])
            verification["retained_callback"] = dict(records=[73, 86], prior_replays=len(callback["observations"]),
                                                      return_pc=10254, filesystem_deletions=0)
        checks.append(dict(module=module, **verification))
    for name, value in (("battle-startup", plans), ("battle-startup-verification", checks)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print([(p["module"], len(p["rows"]), len(p["settings"]), p["unresolved"]) for p in plans])


if __name__ == "__main__":
    main()
