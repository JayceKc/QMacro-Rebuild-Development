"""Map the initial dialog modes, Paradise weekly path and entry calls."""
import hashlib
import json

from build_battle_first_screen import BOUNDARY
from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier
from export_cube_routines import translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

START_SL = {1: 281, 3: 183, 6: 279}
END = {1: 352, 3: 218, 6: 344}
MODE = "VF68BB1C47378756D"
WEEKLY = "V9BB6D6D67378756D"


def build(raw, pool, digest):
    module = raw["module"]
    code, strings = raw["code"], raw["strings"]
    entry, end = BOUNDARY[module], END[module]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = entry, START_SL[module]
    calls, unresolved = [], []

    def emit(op, operand):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["missing_records"].remove(pc)
        candidate["code"][pc] = [op, code[pc][1], operand, code[pc][3]]
        pc += 1

    def text():
        nonlocal sl
        assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
        emit(30 if pool[sl]["kind"] == "decoded-text" else 2, sl)
        sl += 1

    def branch(target):
        nonlocal sl
        assert code[pc][1] == code[pc + 1][1] != code[pc + 2][1]
        emit(4, sl)
        emit(6, target - pc)
        sl += 1

    def jump(target):
        emit(16, target - pc)

    def call(target, refs=(), basis="retained frame and call"):
        start = pc
        assert code[start][1] == code[start + 1][1] == code[start + 2][1]
        frame = strings[sl]
        assert all(strings[code[at][2]] == frame and code[at + 1][0:3:2] == [12, target] for at in refs)
        assert refs or code[target - 1][0] == 16
        name = decode_identifier(frame.split("=New ", 1)[1].split(":", 1)[0].rsplit("_V", 1)[1])
        calls.append(dict(record=start + 1, target=target, name=name, source_sl=sl,
                          retained_references=list(refs), basis=basis))
        text()
        emit(12, target)
        text()

    if module == 3:
        assert strings[sl] == f"Sgn({WEEKLY}=1 or {WEEKLY}=2 or {WEEKLY}=3)"
        assert all(strings[code[at][2]] == f"Sgn({WEEKLY}={i})"
                   for i, at in enumerate((5505, 5637, 5763), 1))
        branch(212)
        text()
        text()
        call(5412, basis="retained weekly mode tests L5505/L5637/L5763")
        text()
        text()
        assert "按钮点击进本" in strings[code[529][2]]
        call(527, basis="retained entry trace L529")
        text()
    else:
        unresolved.append(pc)
        pc += 1
        text()
        join = 337 if module == 1 else 336
        branch(324 if module == 1 else 330)
        text()
        button_target, button_refs = (3642, (651, 665)) if module == 1 else (3458, (870, 892))
        call(button_target, button_refs)
        jump(join)
        branch(331 if module == 1 else join)
        text()
        dialog_target, dialog_refs = (3838, (658,)) if module == 1 else (3660, (877,))
        call(dialog_target, dialog_refs)
        if module == 1:
            jump(join)
            branch(join)
            text()
            call(3642, (651, 665))
        assert pc == join
        for _ in range(3 if module == 1 else 4):
            text()
        if module == 1:
            branch(end)
            text()
            text()
            call(8795, (638,))
            text()
            text()
            call(3623, (643, 1258))
        else:
            call(3329, (881,))
            text()
    assert pc == end and sl == {1: 306, 3: 193, 6: 295}[module]
    rows = translate(candidate, ((entry + len(unresolved), end - 1, "入場路由"),),
                     external_targets=(end, *(c["target"] for c in calls)))["actions"]
    for row in rows:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    return dict(module=module, entry=entry, boundary=end, rows=rows, unresolved=unresolved, calls=calls,
                source_program_sha256=digest, original_values_recovered=0)


def verify(plan, base, retained):
    source = base["actions"] + retained["actions"]
    shared_default = {a["key"]: 0 for a in source if a["kind"] in ("read_global", "write_global")}
    values = {n: 0 for n in scalar_names(source) if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    results = []
    module = plan["module"]
    start = plan["entry"] + len(plan["unresolved"])
    specs = [(start, mode) for mode in range({1: 4, 3: 5, 6: 3}[module])]
    if module == 1:
        specs.append((349, 0))
    for entry, mode in specs:
        shared = dict(shared_default, V8186B4D47378756D="AB12CD")
        machine = RetainedBattleMachine(base, retained, 0, lambda key, pc: shared[key],
                                        dict(values, **{MODE: mode, WEEKLY: mode}))
        machine.pc = entry
        for row in plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        records, root_calls, returned, notes = [], [], [], []
        for _ in range(2200):
            if machine.done:
                break
            event = machine.step()
            at, kind = event["record"], event["kind"]
            records.append(at)
            if kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                x, y = event["rect"][:2]
                if kind.startswith("builtin"):
                    machine.supply_builtin(x + 1, y + 1)
                else:
                    machine.supply_query(x + 1, y + 1, int(kind == "find_color"))
            elif kind == "random_int":
                machine.supply_random(event["lower"])
            elif kind == "write_global":
                shared[event["key"]] = event["value"]
            elif kind == "worker_start":
                machine.supply_worker_id(1000 + at)
            elif kind == "dm_real_mouse_intent":
                machine.supply_dm_return(1)
            elif kind == "call" and plan["entry"] <= at < plan["boundary"]:
                root_calls.append([at, event["target"]])
            elif kind == "return" and event.get("target") in {c["record"] + 1 for c in plan["calls"]}:
                returned.append(event["target"])
            elif kind == "trace":
                notes.append([at, event["arguments"]])
        if entry == 349:
            assert root_calls == [[350, 3623]] and returned == [351] and machine.pc == plan["boundary"]
        elif module == 1:
            initial = {0: [[321, 3642]], 1: [[328, 3838]], 2: [[335, 3642]]}.get(mode, [])
            assert root_calls == initial + [[345, 8795]]
            assert returned == [at + 1 for at, _ in initial]
        elif module == 3:
            assert root_calls == ([[210, 5412]] if mode in (1, 2, 3) else []) + [[215, 527]]
            assert returned == [at + 1 for at, _ in root_calls] and machine.pc == plan["boundary"]
        else:
            assert root_calls == {0: [[327, 3458]], 1: [[334, 3660]], 2: []}[mode] + [[341, 3329]]
            assert returned == [at + 1 for at, _ in root_calls] and machine.pc == plan["boundary"]
        results.append(dict(entry=entry, mode=mode, records=records, root_calls=root_calls, returned=returned,
                            notes=notes, reason=machine.reason or "step_limit", next_record=machine.pc))
    return results


def main():
    plans, checks = [], []
    for module in START_SL:
        tag = f"{module:02}"
        source = (PROJECT / "programs" / f"{tag}.json").read_bytes()
        pool = json.loads((INVENTORY / f"{tag}-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
        plan = build(json.loads(source), pool, hashlib.sha256(source).hexdigest())
        plans.append(plan)
        base, retained = [json.loads((PROJECT / "data" / f"{stem}-{tag}.json").read_text("utf8"))
                          for stem in ("battle", "battle-retained")]
        checks.append(dict(module=module, cases=verify(plan, base, retained)))
    for name, value in (("battle-entry-routes", plans), ("battle-entry-routes-verification", checks)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print([(p["module"], len(p["rows"]), [(c["next_record"], c["root_calls"], c["returned"]) for c in check["cases"]])
           for p, check in zip(plans, checks)])


if __name__ == "__main__":
    main()
