"""Align battle startup screen operations and first Paradise calls."""
import hashlib
import json

from build_battle_checkbox_setup import STOP
from build_cube_prefix import INVENTORY, PROJECT
from build_cube_start_workers import decode_identifier
from export_cube_routines import translate
from qmacro_battle_retained import RetainedBattleMachine
from replay_cube_main import scalar_names

FIRST_SL = {1: 238, 3: 147, 6: 221}
BOUNDARY = {1: 315, 3: 205, 6: 321}
SDK_SEARCH = {1: 285, 6: 291}
PARADISE_CALLS = {
    174: (6099, [], "candidate from connection-marker search"),
    180: (2446, [546, 3195], "same frame and retained call target"),
    190: (3260, [], "candidate from character switching traces"),
    195: (2427, [743, 764, 2121, 2160, 2199, 2238, 3191, 3243], "same frame and retained call target"),
    201: (2446, [546, 3195], "same frame and retained call target"),
}


def build(raw, pool, digest):
    module = raw["module"]
    code, strings = raw["code"], raw["strings"]
    entry, boundary = STOP[module], BOUNDARY[module]
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]))
    pc, sl = entry, FIRST_SL[module]
    calls = []

    def emit(op, arg):
        nonlocal pc
        assert code[pc][0] == 255 and pc in candidate["missing_records"]
        candidate["missing_records"].remove(pc)
        candidate["code"][pc] = [op, code[pc][1], arg, code[pc][3]]
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

    if module in SDK_SEARCH:
        search = SDK_SEARCH[module]
        while pc < search - 2:
            text()
        assert code[pc][1] == code[pc + 1][1] == code[pc + 2][1]
        assert strings[sl] == "V8186B4D47378756D"
        emit(27, sl)
        sl += 1
        text()
        text()
        branch(boundary)
        text()
        text()
        branch(boundary)
        while pc < boundary:
            text()
        targets = (boundary,)
    else:
        while pc < boundary:
            if pc in PARADISE_CALLS:
                at, frame = pc, strings[sl]
                target, refs, evidence = PARADISE_CALLS[at]
                assert code[at][1] == code[at + 1][1] == code[at + 2][1]
                assert code[target - 1][0] == 16
                assert all(strings[code[r][2]] == frame and code[r + 1][0:3:2] == [12, target] for r in refs)
                name = decode_identifier(frame.split("=New ", 1)[1].split(":", 1)[0].rsplit("_V", 1)[1])
                calls.append(dict(record=at + 1, target=target, frame_sl=sl, name=name,
                                  retained_references=refs, evidence=evidence))
                text()
                emit(12, target)
                text()
            elif pc == 186:
                assert strings[sl] == "Sgn(vbTrue)"
                branch(boundary)
            else:
                text()
        targets = (boundary, *(site["target"] for site in calls))
    assert pc == boundary
    assert sl == {1: 281, 3: 183, 6: 279}[module]
    rows = translate(candidate, ((entry, boundary - 1, "首次畫面與呼叫"),), external_targets=targets)["actions"]
    for row in rows:
        row["candidate_opcode"] = row.pop("opcode")
        row.pop("operand")
        row["inferred"] = True
    return dict(module=module, entry=entry, boundary=boundary, rows=rows, call_sites=calls,
                original_values_recovered=0, source_program_sha256=digest)


def verify(plan, base, retained):
    shared_initial = {a["key"]: 0 for a in base["actions"] + retained["actions"]
                      if a["kind"] in ("read_global", "write_global")}
    values = {n: 0 for n in scalar_names(base["actions"] + retained["actions"])
              if not n.startswith(("CUBE_ROOT_SLOT_", "BATTLE_FIELD_"))}
    values.update(YC=100, DM_RET=0, g_iSimulateModeInVBSBlock=0)
    cases = []
    specs = [(plan["entry"], first, second) for first, second in
             ((False, False), (True, False), (True, True))] if plan["module"] in SDK_SEARCH else [
                 (plan["entry"], True, True), (195, True, True)]
    for entry, first, second in specs:
        shared = dict(shared_initial, V8186B4D47378756D="AB12CD")
        machine = RetainedBattleMachine(base, retained, 0, lambda key, pc: shared[key], values)
        machine.pc = entry
        for row in plan["rows"]:
            machine.actions[row["record"]] = row
            del machine.boundaries[row["record"]]
        records, events, calls, returns = [], [], [], []
        for _ in range(1200):
            if machine.done:
                break
            event = machine.step()
            at, kind = event["record"], event["kind"]
            records.append(at)
            if kind in ("find_color", "find_pic", "builtin_color", "builtin_picture"):
                left, top, _, _ = event["rect"]
                hit = (first if at == SDK_SEARCH.get(plan["module"]) else second
                       if at == SDK_SEARCH.get(plan["module"], -10) + 4 else True)
                coords = (left + 1, top + 1) if hit else (-1, -1)
                if kind.startswith("builtin"):
                    machine.supply_builtin(*coords)
                else:
                    machine.supply_query(*coords, int(not hit) if plan["module"] != 3 else
                                         (int(hit) if kind == "find_color" else 0))
            elif kind == "random_int":
                machine.supply_random(event["lower"])
            elif kind == "write_global":
                shared[event["key"]] = event["value"]
            elif kind == "call":
                calls.append((at, event["target"]))
            elif kind == "return":
                returns.append((at, event.get("target")))
            elif kind == "dm_real_mouse_intent":
                machine.supply_dm_return(1)
            elif kind in ("move_to", "mouse_click", "key_press", "trace"):
                events.append(event)
        if plan["module"] in SDK_SEARCH:
            assert machine.done and machine.pc == plan["boundary"]
            search = SDK_SEARCH[plan["module"]]
            assert (search + 4 in records) == first
            assert any(e.get("arguments") == [1904, 283] for e in events) == (first and second)
            assert sum(e.get("arguments", [None])[0] == "Enter" for e in events) == (2 if first and second else 0)
        elif entry == plan["entry"]:
            assert calls[0] == (175, 6099) and (181, 2446) in calls, (machine.pc, calls[:20], records[-20:])
            assert 176 in records and 182 in records and (191, 3260) in calls
        else:
            assert calls[0] == (196, 2427) and (202, 2446) in calls
            assert 197 in records and 203 in records
            assert machine.done and machine.pc == plan["boundary"]
        cases.append(dict(entry=entry, first_hit=first, second_hit=second, records=records, events=events,
                          calls=calls, returns=returns, next_record=machine.pc, reason=machine.reason or "step_limit"))
    return cases


def main():
    plans, checks = [], []
    for module in FIRST_SL:
        tag = f"{module:02}"
        source = (PROJECT / "programs" / f"{tag}.json").read_bytes()
        pool = json.loads((INVENTORY / f"{tag}-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
        plan = build(json.loads(source), pool, hashlib.sha256(source).hexdigest())
        plans.append(plan)
        base, retained = [json.loads((PROJECT / "data" / f"{stem}-{tag}.json").read_text("utf8"))
                          for stem in ("battle", "battle-retained")]
        checks.append(dict(module=module, cases=verify(plan, base, retained)))
    daily, chaos = plans[0], plans[2]
    for a, b in zip(daily["rows"][-32:], chaos["rows"][-32:]):
        assert (b["record"] - a["record"], b["location"] - a["location"]) == (6, 7)
        assert (a["candidate_opcode"], a["source"]) == (b["candidate_opcode"], b["source"])
    chaos["matching_daily_screen"] = dict(chaos=[289, 320], daily=[283, 314])
    for name, value in (("battle-first-screen", plans), ("battle-first-screen-verification", checks)):
        (INVENTORY / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")
    print([(p["module"], len(p["rows"]), [c["next_record"] for c in check["cases"]])
           for p, check in zip(plans, checks)])


if __name__ == "__main__":
    main()
