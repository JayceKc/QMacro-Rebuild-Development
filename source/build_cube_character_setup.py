"""Infer the cube's character validation and party setup from retained SL data."""
from collections import Counter
import json

from build_cube_lucky_bridge import machine_for
from build_cube_prefix import INVENTORY, OUTPUT, PROJECT, build as build_prefix, replay as replay_prefix
from export_cube_routines import translate
from replay_cube_retained import build_cases

ENTRY, END = 203, 301


def build(raw, prefix):
    code = raw["code"]
    pool = json.loads((INVENTORY / "07-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    inferred = []

    def emit(op, operand, sl=None):
        pc = ENTRY + len(inferred)
        assert code[pc][0] == 255 and pc in raw["missing_records"]
        inferred.append(([op, code[pc][1], operand, code[pc][3]], sl))

    def text(sl):
        assert pool[sl]["index"] == sl and pool[sl]["value"] == raw["strings"][sl]
        emit(30 if pool[sl]["kind"] == "decoded-text" else 2, sl, sl)

    def texts(start, stop):
        for sl in range(start, stop):
            text(sl)

    def same(start, width):
        assert ENTRY + len(inferred) == start
        assert len({code[pc][1] for pc in range(start, start + width)}) == 1
        assert code[start - 1][1] != code[start][1] != code[start + width][1]

    def control(op, target):
        emit(op, target - (ENTRY + len(inferred)))

    def read(sl):
        emit(27, sl, sl)
        text(sl + 1)

    def shared(sl):
        text(sl + 2)
        text(sl)
        emit(28, sl + 1, sl + 1)

    def condition(sl, target):
        emit(4, sl, sl)
        control(6, target)

    for pc, sl in ((203, 185), (206, 188), (209, 191)):
        same(pc, 3)
        shared(sl)
    text(194)
    for pc, sl, target in ((213, 195, 221), (222, 203, 230)):
        same(pc, 6)
        read(sl)
        read(sl + 2)
        condition(sl + 4, target)
        texts(sl + 5, sl + 8)
    same(231, 6)
    read(211)
    read(213)
    condition(215, 243)
    text(216)
    same(238, 5)
    read(217)
    shared(219)
    text(222)
    same(244, 6)
    read(223)
    read(225)
    condition(227, 254)
    text(228)
    same(251, 3)
    shared(229)
    text(232)
    same(255, 4)
    read(233)
    condition(235, 275)
    text(236)
    same(260, 3)
    shared(237)
    same(263, 3)
    shared(240)
    same(266, 4)
    read(243)
    condition(245, 274)
    text(246)
    same(271, 3)
    shared(247)
    control(16, 279)
    text(250)
    same(276, 3)
    shared(251)
    texts(254, 256)
    for pc, sl in ((281, 256), (284, 259), (287, 262)):
        same(pc, 3)
        read(sl)
        text(sl + 2)
    texts(265, 276)
    assert len(inferred) == END - ENTRY
    assert Counter(sl for _, sl in inferred if sl is not None) == Counter(range(185, 276))

    # Translate only an in-memory candidate. The archived program and all
    # missing markers in the original JSON are preserved.
    candidate = dict(raw, code=list(code), missing_records=set(raw["missing_records"]) - set(range(ENTRY, END)))
    for pc, (candidate_row, _) in enumerate(inferred, ENTRY):
        candidate["code"][pc] = candidate_row
    actions = translate(candidate, ((ENTRY, END - 1, "角色與組隊"),))["actions"]
    for action in actions:
        action["candidate_opcode"] = action.pop("opcode")
        action.pop("operand")
        action["inferred"] = True
    roles = {setting["role"]: setting["key"] for setting in prefix["settings"]}
    for sl, role in ((195, "last_character"), (197, "first_character"), (233, "party_mode"),
                     (243, "weekly_mode")):
        assert raw["strings"][sl] == roles[role]
    return dict(module=7, entry=ENTRY, boundary=END, actions=actions, roles=roles,
                keys={name: raw["strings"][sl] for name, sl in
                      (("switch_character", 220), ("one_floor", 241), ("floor", 186),
                       ("lucky", 189), ("entry_movement", 192))},
                source_program_sha256=prefix["source_program_sha256"], original_values_recovered=0,
                alternative_edges=[{"record": 269, "target": 279, "same_visible_state": True}])


def verify(plan, plans, prefix):
    fixture = build_cases(plans[0], plans[2])[1]
    cases = []
    roles, keys = plan["roles"], plan["keys"]
    for first, last in ((0, 0), (1, 0), (0, 3), (2, 5), (5, 2)):
        for mode in range(5):
            for weekly in range(3):
                options = {setting["property"]: 0 for setting in prefix["settings"]}
                options.update({"Form1.ComboBox6.ListIndex": first, "Form1.ComboBox7.ListIndex": last,
                                "Form1.ComboBox99.ListIndex": mode, "Form1.ComboBox3.ListIndex": weekly})
                init = replay_prefix(prefix, options, version="7.2450", sdk_value="AB12CD")
                assert init["next_record"] == ENTRY
                # Seed the otherwise unknown prior shared character selector
                # so tests can check when this segment does or does not write it.
                shared = dict(fixture["shared"], **init["shared"])
                shared[keys["switch_character"]] = 17
                machine = machine_for(dict(plan, worker_entry=-1), plans, shared, fixture["values"], ENTRY)
                events = []
                for _ in range(120):
                    event = machine.step()
                    events.append(event)
                    if event["kind"] == "write_global":
                        shared[event["key"]] = event["value"]
                    elif event["kind"] == "random_int":
                        machine.supply_random(event["lower"] + event["span"] - 1)
                    if machine.done:
                        break
                records = [event["record"] for event in events]
                assert all(shared[keys[name]] == 0 for name in ("floor", "lucky", "entry_movement"))
                if bool(first) != bool(last):
                    assert machine.reason == "script_stop" and machine.pc == (220 if first else 229)
                    assert 255 not in records and shared[keys["switch_character"]] == 17
                else:
                    assert machine.reason == "missing_original_record" and machine.pc == END
                    assert shared[keys["switch_character"]] == (first or 17)
                    assert shared[roles["party_mode"]] == (2 if mode == 4 else mode)
                    assert shared[keys["one_floor"]] == int(mode == 4)
                    assert shared[roles["weekly_mode"]] == (1 if mode == 4 and weekly == 0 else weekly)
                    assert next(e for e in events if e["record"] == 297)["arguments"] == [39, 19]
                    assert [e["record"] for e in events if e["kind"] == "trace"] == [280, 283, 286, 289]
                cases.append(dict(first=first, last=last, party=mode, weekly=weekly,
                                  records=records, reason=machine.reason, boundary=machine.pc,
                                  final_party=shared[roles["party_mode"]],
                                  final_weekly=shared[roles["weekly_mode"]]))
    observed = {pc for case in cases for pc in case["records"]} & set(range(ENTRY, END))
    return dict(cases=cases, steps=sum(len(c["records"]) for c in cases),
                observed_inferred_positions=sorted(observed), original_prefix_executed=False,
                real_actions_sent=False)


def main():
    raw = json.loads((PROJECT / "programs/07.json").read_text("utf8"))
    plans = tuple(json.loads((PROJECT / "data" / f"{name}.json").read_text("utf8")) for name in
                  ("cube-retained-tail", "cube-main", "cube-workers", "cube-routines"))
    prefix = build_prefix()
    result = build(raw, prefix)
    report = verify(result, plans, prefix)
    for name, data in (("cube-character-setup", result), ("cube-character-setup-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(result['actions'])} inferred positions; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
