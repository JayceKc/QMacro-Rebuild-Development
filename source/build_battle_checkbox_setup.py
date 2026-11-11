"""Infer battle checkbox assignments, SDK waits and module 06 mode defaults."""
import hashlib
import json

from build_battle_startup import SDK, SPECS, build as build_startup, verify as verify_startup
from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier

START_SL = {1: 154, 3: 113, 6: 148}
STOP = {1: 270, 3: 163, 6: 261}


def build(raw, inventory, startup):
    module = raw["module"]
    code, strings, pool = raw["code"], raw["strings"], inventory["prefix_pool"]
    entry, sl = startup["boundary"], START_SL[module]
    pc = entry
    rows, settings = [], []

    def add(op, kind, ref=None, **extra):
        nonlocal pc
        assert pc in raw["missing_records"] and code[pc][0] == 255
        if ref is not None:
            assert pool[ref]["index"] == ref and pool[ref]["value"] == strings[ref]
        rows.append(dict(record=pc, location=code[pc][1], field_3=code[pc][3], candidate_opcode=op,
                         kind=kind, source_sl=ref, source=strings[ref] if ref is not None else None,
                         inferred=True, **extra))
        pc += 1

    def text(ref, kind="statement", **extra):
        add(30 if pool[ref]["kind"] == "decoded-text" else 2, kind, ref, **extra)

    def delay():
        nonlocal sl
        assert strings[sl].startswith("Call QMLibrary.Delay(")
        text(sl, "delay")
        sl += 1

    def group(width):
        assert len({code[at][1] for at in range(pc, pc + width)}) == 1
        assert code[pc + width][1] != code[pc][1]

    def test(ref, kind, target, **extra):
        assert strings[ref].startswith("Sgn(")
        add(4, kind, ref, **extra)
        add(6, "if_zero", target=target)

    def write_group(ref, value):
        group(3)
        assert strings[ref + 2].endswith(f"={value}")
        text(ref + 2, "prepare_shared")
        text(ref, "read_shared_slot")
        add(28, "write", ref + 1, key=strings[ref + 1], shared=True, value=value)

    def local(ref, value=None):
        key, encoded_value = strings[ref].split("=", 1)
        assert value is None or str(value) == encoded_value
        text(ref, "write", key=key, shared=False, value=int(encoded_value))

    def checkbox(*, shared=False, direct=False):
        nonlocal sl
        base = pc
        group(2 if direct else 4)
        if direct:
            assert strings[sl] == "Sgn(FORM1.CHECKBOX2.VALUE=1)"
            prop, cond = "Form1.CheckBox2.Value", sl
        else:
            prop, cond = strings[sl], sl + 2
            assert prop.startswith("Form1.CheckBox") and prop.endswith(".Value")
            add(37, "read_ui", sl, property=prop)
            text(sl + 1, "store_ui")
        true_width = 3 if shared else 1
        false_pc = base + (2 if direct else 4) + true_width + 1
        test(cond, "test_checkbox", false_pc, property=prop)
        first_write = cond + 1
        if shared:
            key = strings[first_write + 1]
            assert key == strings[first_write + 4]
            write_group(first_write, 1)
        else:
            key = strings[first_write].split("=")[0]
            assert strings[first_write + 1] == f"{key}=0"
            local(first_write, 1)
        add(16, "jump", target=false_pc + true_width)
        if shared:
            write_group(first_write + 3, 0)
        else:
            local(first_write + 1, 0)
        settings.append(dict(property=prop, key=key, shared=shared, record=base,
                             original_name=decode_identifier(key[1:])))
        sl = first_write + (6 if shared else 2)

    checkbox(shared=True)
    if module == 1:
        delay()
        delay()
        for _ in range(9):
            checkbox()
            delay()
    elif module == 3:
        checkbox()
        delay()
    else:
        delay()
        checkbox(direct=True)
        delay()
        for i in range(4):
            checkbox()
            if i != 2:
                delay()
        group(4)
        mode_key = strings[sl]
        add(27, "read_shared", sl, key=mode_key)
        text(sl + 1, "store_shared")
        assert strings[sl + 2].endswith("(1)=5)")
        test(sl + 2, "test_value", 224, key=mode_key, shared=True, value=5)
        sl += 3
        delay()
        assert strings[sl + 1] == mode_key
        write_group(sl, 1)
        write_group(sl + 3, 1)
        sl += 6
        delay()
        weekly_key = next(s["key"] for s in startup["settings"] if s["property"] == "Form1.ComboBox6.ListIndex")
        for index, (threshold, next_gate) in enumerate(zip((6, 10, 15, 20), (230, 235, 240, 245))):
            group(2)
            assert strings[sl] == f"Sgn({weekly_key}={index})"
            test(sl, "test_value", next_gate, key=weekly_key, shared=False, value=index)
            sl += 1
            delay()
            local(sl, threshold)
            sl += 1
            add(16, "jump", target=247)
        delay()
        local(sl, 6)
        sl += 1
        delay()

    if module != 6:
        local(sl, 0)
        write_group(sl + 1, 0)
        write_group(sl + 4, 0)
        local(sl + 7, 1)
        sl += 8
        delay()
    group(4)
    assert strings[sl] == SDK and strings[sl + 2].endswith('(1)="")')
    add(27, "read_shared", sl, key=SDK)
    text(sl + 1, "store_shared")
    test(sl + 2, "test_value", STOP[module], key=SDK, shared=True, value="")
    sl += 3
    group(2)
    loop = pc
    assert strings[sl] == "Sgn(vbTrue)"
    test(sl, "test_true", STOP[module])
    sl += 1
    for _ in range(6):
        delay()
    add(16, "jump", target=loop)
    assert pc == STOP[module] and strings[sl] == "Randomize"
    assert sorted(r["source_sl"] for r in rows if r["source_sl"] is not None) == list(range(START_SL[module], sl))
    for setting in settings:
        key = setting["key"]
        matches = [at for at, (op, _, arg, _) in enumerate(code)
                   if op in (2, 4, 27, 30) and key in strings[arg]]
        setting.update(retained_reference_count=len(matches), retained_reference_examples=matches[:6])
    return dict(module=module, entry=entry, boundary=pc, rows=rows, settings=settings,
                sdk_wait_loop=loop, source_program_sha256=startup["source_program_sha256"], original_values_recovered=0)


def replay_checkboxes(plan, ui, shared, local):
    rows = {r["record"]: r for r in plan["rows"]}
    shared, local = dict(shared), dict(local)
    records, pc = [], plan["entry"]
    for _ in range(220):
        if pc == plan["boundary"]:
            break
        row = rows[pc]
        records.append(pc)
        pc += 1
        kind = row["kind"]
        if kind == "test_checkbox":
            flag = ui[row["property"]] == 1
        elif kind == "test_value":
            flag = (shared if row["shared"] else local)[row["key"]] == row["value"]
        elif kind == "test_true":
            flag = True
        elif kind == "jump" or kind == "if_zero" and not flag:
            pc = row["target"]
        elif kind == "write":
            (shared if row["shared"] else local)[row["key"]] = row["value"]
    return dict(records=records, next_record=pc, shared=shared, local=local)


def verify(plan, startup):
    fixture = verify_startup(startup)["cases"][0]
    settings = plan["settings"]
    masks = [0, (1 << len(settings)) - 1] + [1 << i for i in range(len(settings))]
    specs = [(mask, "AB12CD", 0, 0) for mask in masks] + [(0, "", 0, 0), (0, "4AD733", 0, 0)]
    if plan["module"] == 6:
        specs += [(0, "AB12CD", mode, weekly) for mode in (4, 5, 6) for weekly in range(5)]
    cases = []
    for mask, sdk, mode, weekly in specs:
        ui = {s["property"]: (mask >> i) & 1 for i, s in enumerate(settings)}
        shared, local = dict(fixture["shared"]), dict(fixture["local"])
        shared[SDK] = sdk
        if plan["module"] == 6:
            for prop, state, value in (("Form1.ComboBox3.ListIndex", shared, mode), ("Form1.ComboBox6.ListIndex", local, weekly)):
                state[next(s["key"] for s in startup["settings"] if s["property"] == prop)] = value
        case = replay_checkboxes(plan, ui, shared, local)
        records, pc, shared, local = (case[key] for key in ("records", "next_record", "shared", "local"))
        assert {s["property"]: (shared if s["shared"] else local)[s["key"]] for s in settings} == ui
        assert (pc == plan["boundary"]) == bool(sdk)
        if not sdk:
            assert records.count(plan["sdk_wait_loop"]) >= 2
        if plan["module"] == 6:
            assert shared["VFD8CD4CBA2D9A19C4D6A65757378756D"] == (1 if mode == 5 else mode)
            assert shared.get("VFFD1D187A4B7B6A84D6A65757378756D") == (1 if mode == 5 else None)
            assert local["JCXL"] == {0: 6, 1: 10, 2: 15, 3: 20}.get(weekly, 6)
        cases.append(dict(ui=ui, sdk=sdk, mode=mode, weekly=weekly, records=records, next_record=pc,
                          shared=shared, local=local))
    return cases


def main():
    plans, checks = [], []
    for module in SPECS:
        tag = f"{module:02}"
        source = (PROJECT / "programs" / f"{tag}.json").read_bytes()
        raw = json.loads(source)
        inventory = json.loads((INVENTORY / f"{tag}-prefix-inventory.json").read_text("utf8"))
        bindings = json.loads((INVENTORY / f"{tag}-ui-bindings.json").read_text("utf8"))
        startup = build_startup(raw, inventory, bindings, hashlib.sha256(source).hexdigest())
        plan = build(raw, inventory, startup)
        plans.append(plan)
        checks.append(dict(module=module, cases=verify(plan, startup)))
    daily, paradise = plans[:2]
    pairs = zip(daily["rows"][-22:], paradise["rows"][-22:])
    for a, b in pairs:
        assert (a["record"] - b["record"], a["location"] - b["location"]) == (107, 60)
        assert (a["candidate_opcode"], a["source"]) == (b["candidate_opcode"], b["source"])
        if "target" in a:
            assert a["target"] - b["target"] == 107
    daily["matching_paradise_initialization"] = dict(daily=[248, 269], paradise=[141, 162])
    for name, value in (("battle-checkbox-setup", plans), ("battle-checkbox-setup-verification", checks)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print([(p["module"], len(p["rows"]), len(p["settings"]), len(c["cases"])) for p, c in zip(plans, checks)])


if __name__ == "__main__":
    main()
