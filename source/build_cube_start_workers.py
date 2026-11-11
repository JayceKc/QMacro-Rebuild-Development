"""Infer the cube's initial party and emote worker dispatch."""
from collections import Counter
import json
import re

from build_cube_character_setup import build as build_setup
from build_cube_character_wait import build as build_wait
from build_cube_lucky_bridge import machine_for
from build_cube_prefix import INVENTORY, OUTPUT, PROJECT, build as build_prefix, replay as replay_prefix
from export_cube_routines import translate

ENTRY, END = 343, 444
PARTY = ((343, 307, 4635, 16), (359, 317, 4635, 16),
         (375, 327, 1495, 29), (391, 337, 1495, 29))
EMOTE = ((405, 346, 3488, 27), (419, 354, 3510, 22), (433, 362, 3538, 17))


def decode_identifier(encoded):
    key = bytes.fromhex("4d6a65757378756d")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(bytes.fromhex(encoded))).rstrip(b"\0").decode("gb18030")


def build(raw):
    code, strings = raw["code"], raw["strings"]
    pool = json.loads((INVENTORY / "07-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    missing = set(raw["missing_records"])
    candidate = dict(raw, code=list(code), missing_records=missing - set(range(ENTRY, END)))
    pc, used, sites = ENTRY, Counter(), []
    template_ops = [row[0] for row in code[717:726]]
    assert template_ops == [24, 16, 2, 12, 23, 2, 2, 2, 28]
    assert code[717][2] == 2 and code[718][2] == 4

    def emit(op, operand):
        nonlocal pc
        assert pc in missing and code[pc][0] == 255
        candidate["code"][pc] = [op, code[pc][1], operand, code[pc][3]]
        if op in (2, 4, 27, 28, 30):
            used[operand] += 1
        pc += 1

    def text(sl):
        assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
        emit(30 if pool[sl]["kind"] == "decoded-text" else 2, sl)

    def condition(sl, target):
        emit(4, sl)
        emit(6, target - pc)

    def launch(site):
        start, sl, callee, declaration = site
        assert pc == start and len({row[1] for row in code[start:start + 9]}) == 1
        assert code[start - 1][1] != code[start][1] != code[start + 9][1]
        class_name = re.search(r"=New (\w+):", strings[sl])[1]
        assert strings[code[declaration][2]].startswith(f"Class {class_name}:")
        name = decode_identifier(class_name.rsplit("_V", 1)[1])
        id_name = decode_identifier(strings[sl + 3][1:])
        emit(24, 2)
        emit(16, 4)
        text(sl)
        emit(12, callee)
        emit(23, 0)
        text(sl + 1)
        text(sl + 4)
        text(sl + 2)
        emit(28, sl + 3)
        assert [row[0] for row in candidate["code"][start:pc]] == template_ops
        sites.append(dict(record=start, worker_entry=start + 2, callee=callee, class_declaration=declaration,
                          name=name, id_name=id_name, id_key=strings[sl + 3], inferred_callee=True))

    for i, site in enumerate(PARTY):
        _, sl, _, _ = site
        if i:
            emit(27, sl - 4)
            text(sl - 3)
            condition(sl - 2, PARTY[i + 1][0] - 5 if i < 3 else 401)
            text(sl - 1)
        launch(site)
        text(sl + 5)
        if i < 3:
            emit(16, 401 - pc)
    assert pc == 401
    text(343)
    for i, site in enumerate(EMOTE):
        _, sl, _, _ = site
        condition(sl - 2, EMOTE[i + 1][0] - 3 if i < 2 else 443)
        text(sl - 1)
        launch(site)
        text(sl + 5)
        if i < 2:
            emit(16, 443 - pc)
    text(368)
    assert pc == END and used == Counter(range(307, 369))
    assert [s["name"] for s in sites] == ["全局找图"] * 2 + ["点确定"] * 2 + [
        "二分钟一次表情", "三分钟一次表情", "四分钟一次表情"]
    assert [s["id_name"] for s in sites] == ["全局找图ID"] * 2 + ["点确定ID"] * 2 + ["表情ID"] * 3
    actions = translate(candidate, ((ENTRY, END - 1, "組隊與表情工作"),),
                        external_targets=(END, *(s["callee"] for s in sites)))["actions"]
    for action in actions:
        action["candidate_opcode"] = action.pop("opcode")
        action.pop("operand")
        action["inferred"] = True
    return dict(entry=ENTRY, boundary=END, actions=actions, sites=sites,
                preserved_wrapper=[717, 725], original_values_recovered=0)


def verify(plan, raw, prefix, plans):
    setup = build_setup(raw, prefix)
    wait = build_wait(raw, setup)
    combined = dict(entry=setup["entry"], worker_entry=-1,
                    actions=setup["actions"] + wait["actions"] + plan["actions"])
    sites = {s["record"]: s for s in plan["sites"]}
    emote_key = next(s["key"] for s in prefix["settings"] if s["role"] == "emote")
    parents, children = [], []
    for mode in range(5):
        for emote in range(4):
            options = {s["property"]: 0 for s in prefix["settings"]}
            options.update({"Form1.ComboBox99.ListIndex": mode, "Form1.ComboBox1.ListIndex": emote})
            init = replay_prefix(prefix, options, version="7.2450", sdk_value="AB12CD")
            shared = dict(init["shared"])
            shared[setup["keys"]["switch_character"]] = 17  # Explicit prior selector for the zero-range fixture.
            values = {emote_key: init["local"]["emote"], "g_iSimulateModeInVBSBlock": 0}
            machine = machine_for(combined, plans, shared, values, setup["entry"])
            records, starts, writes = [], [], []
            for _ in range(240):
                if machine.done:
                    break
                event = machine.step()
                at, kind = event["record"], event["kind"]
                records.append(at)
                if kind == "write_global":
                    shared[event["key"]] = event["value"]
                    if at >= ENTRY:
                        writes.append((at, event["key"], event["value"]))
                elif kind == "random_int":
                    machine.supply_random(event["lower"])
                elif kind == "find_color":
                    assert at == 306 and event["spec"] == "AB12CD-151515"
                    machine.supply_query(161, 3, 0)
                elif kind == "worker_start":
                    assert event["target"] == sites[at]["worker_entry"]
                    worker_id = 1000 + at
                    starts.append(at)
                    machine.supply_worker_id(worker_id)
            assert (machine.reason, machine.pc) == ("missing_original_record", END)
            expected = [{0: 343, 1: 375, 2: 359, 3: 391, 4: 359}[mode]]
            if emote:
                expected.append(EMOTE[emote - 1][0])
            assert starts == expected
            assert writes == [(at + 8, sites[at]["id_key"], 1000 + at) for at in expected]
            assert all(sites[at]["worker_entry"] not in records for at in expected)
            parents.append(dict(mode=mode, emote=emote, records=records, starts=starts, writes=writes))

    for site in plan["sites"]:
        entry, callee = site["worker_entry"], site["callee"]
        machine = machine_for(dict(plan, worker_entry=entry), plans, {"V8186B4D47378756D": "AB12CD"},
                              {"g_iSimulateModeInVBSBlock": 0}, entry)
        frame, call = machine.step(), machine.step()
        assert frame["kind"] == "frame_enter" and call["kind"] == "call" and machine.pc == callee
        events = []
        if callee in (1495, 4635):
            for _ in range(20):
                event = machine.step()
                events.append(event)
                if event["kind"] in ("find_pic", "find_color"):
                    assert event["record"] == {1495: 1507, 4635: 4641}[callee]
                    break
                if event["kind"] == "dm_real_mouse_intent":
                    machine.supply_dm_return(1)
            else:
                raise AssertionError("Expected retained search")
        else:
            for _ in range(34):
                event = machine.step()
                events.append(event)
                if event["kind"] == "key_press":
                    assert event["arguments"][0] == "5"
                    break
            else:
                raise AssertionError("Expected retained emote")
            assert sum(e.get("arguments") == [10000] for e in events) == {3488: 12, 3510: 18, 3538: 24}[callee]
        children.append(dict(site=site["record"], frame=frame, call=call, events=events))
    return dict(parent_cases=parents, worker_cases=children, real_actions_sent=False,
                original_prefix_executed=False)


def main():
    raw = json.loads((PROJECT / "programs/07.json").read_text("utf8"))
    plans = tuple(json.loads((PROJECT / "data" / f"{name}.json").read_text("utf8")) for name in
                  ("cube-retained-tail", "cube-main", "cube-workers", "cube-routines"))
    prefix = build_prefix()
    plan = build(raw)
    report = verify(plan, raw, prefix, plans)
    for name, data in (("cube-start-workers", plan), ("cube-start-workers-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['actions'])} inferred positions; {len(report['parent_cases'])} parent cases; "
          f"{len(report['worker_cases'])} worker cases")


if __name__ == "__main__":
    main()
