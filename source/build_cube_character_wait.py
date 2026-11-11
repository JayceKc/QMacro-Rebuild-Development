"""Connect the inferred cube entry wait to the preserved character routine."""
from collections import Counter
import json

from build_cube_cases import build as character_cases
from build_cube_character_setup import build as build_setup
from build_cube_lucky_bridge import machine_for
from build_cube_prefix import INVENTORY, OUTPUT, PROJECT, build as build_prefix, replay as replay_prefix
from export_cube_routines import translate

ENTRY, END, SWITCH = 301, 343, 5020


def build(raw, setup):
    code, strings = raw["code"], raw["strings"]
    pool = json.loads((INVENTORY / "07-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    missing = set(raw["missing_records"])
    candidate = dict(raw, code=list(code), missing_records=missing - set(range(ENTRY, END)))
    pc = ENTRY
    used = Counter()

    def emit(op, operand):
        nonlocal pc
        assert pc in missing and code[pc][0] == 255
        candidate["code"][pc] = [op, code[pc][1], operand, code[pc][3]]
        if op in (2, 4, 27, 30):
            used[operand] += 1
        pc += 1

    def text(sl):
        assert pool[sl]["index"] == sl and pool[sl]["value"] == strings[sl]
        emit(30 if pool[sl]["kind"] == "decoded-text" else 2, sl)

    def read(sl):
        emit(27, sl)
        text(sl + 1)

    def condition(sl, false_target):
        emit(4, sl)
        emit(6, false_target - pc)

    for start, width in ((301, 2), (304, 3), (307, 2), (313, 4), (318, 4),
                         (323, 3), (326, 2), (328, 4), (333, 3), (338, 4)):
        assert len({code[i][1] for i in range(start, start + width)}) == 1
        assert code[start - 1][1] != code[start][1] != code[start + width][1]

    assert strings[284] == setup["roles"]["first_character"]
    assert all(strings[sl] == setup["roles"]["party_mode"] for sl in (288, 295, 303))
    assert strings[292] == strings[299]
    frame_refs = [at for at, row in enumerate(code[:-1])
                  if row[0] in (2, 30) and strings[row[2]] == strings[292]
                  and code[at + 1][0] == 12]
    assert len(frame_refs) == 19 and {code[at + 1][2] for at in frame_refs} == {SWITCH}

    condition(276, 312)
    text(277)
    read(278)
    text(280)
    condition(281, 311)
    text(282)
    emit(16, 312 - pc)
    emit(16, ENTRY - pc)
    text(283)
    read(284)
    condition(286, 337)
    text(287)
    read(288)
    condition(290, 328)
    text(291)
    text(292)
    emit(12, SWITCH)
    text(293)
    text(294)
    emit(16, 337 - pc)
    read(295)
    condition(297, 337)
    text(298)
    text(299)
    emit(12, SWITCH)
    text(300)
    text(301)
    text(302)
    read(303)
    condition(305, 354)
    text(306)
    assert pc == END and used == Counter(range(276, 307))

    # The retained loop uses the same statements and opcodes, with a different
    # root slot and a longer success body. Both misses reach the back edge.
    for at in range(301, 310):
        op, _, arg, _ = candidate["code"][at]
        ref_op, _, ref_arg, _ = code[at + 253]
        assert op == ref_op
        if op == 6:
            assert at + 253 + ref_arg == {302: 658, 308: 657}[at]
        else:
            assert strings[arg] == strings[ref_arg].replace("(16)", "(1)")
    assert code[657][0] == 16 and 657 + code[657][2] == 554

    actions = translate(candidate, ((ENTRY, END - 1, "讀色等待與換角色"),),
                        external_targets=(END, 354, SWITCH))["actions"]
    for action in actions:
        action["candidate_opcode"] = action.pop("opcode")
        action.pop("operand")
        action["inferred"] = True
    return dict(module=7, entry=ENTRY, boundaries=[END, 354], actions=actions,
                original_values_recovered=0, source_program_sha256=setup["source_program_sha256"],
                preserved_frame_records=frame_refs, preserved_call_target=SWITCH,
                preserved_wait_reference=[554, 562, 657, 658])


def verify(plan, setup, prefix, plans):
    # Reuse the tested picture miss at L5153 to allow the retained role routine
    # to leave its initial polling loop. Other replies are synthetic.
    fixture = next(case for case in character_cases(plans[3]) if case["label"] == "character2-hit")
    entry = setup["entry"]
    combined = dict(entry=entry, worker_entry=-1, actions=setup["actions"] + plan["actions"])
    results = []
    for first, last in ((0, 0), (2, 5)):
        for mode in range(5):
            for misses in (0, 2, None):
                options = {setting["property"]: 0 for setting in prefix["settings"]}
                options.update({"Form1.ComboBox6.ListIndex": first, "Form1.ComboBox7.ListIndex": last,
                                "Form1.ComboBox99.ListIndex": mode})
                init = replay_prefix(prefix, options, version="7.2450", sdk_value="AB12CD")
                assert init["next_record"] == entry
                shared = dict(fixture["shared"], **init["shared"])
                machine = machine_for(combined, plans, shared, fixture["values"], entry)
                records, calls, replies = [], [], []
                tries = 0
                for _ in range(1000 if misses is not None else 150):
                    if machine.done:
                        break
                    event = machine.step()
                    at, kind = event["record"], event["kind"]
                    records.append(at)
                    if kind == "write_global":
                        shared[event["key"]] = event["value"]
                    elif kind == "random_int":
                        machine.supply_random(event["lower"])
                    elif kind == "call":
                        calls.append((at, event["target"]))
                    elif kind in ("find_color", "find_pic"):
                        if at == 306:
                            assert event["spec"] == "AB12CD-151515"
                            tries += 1
                            hit = misses is not None and tries > misses
                        else:
                            hit = str(at) not in fixture["miss_budget"]
                        x, y = (event["rect"][0] + 1, event["rect"][1] + 2) if hit else (-1, -1)
                        # A contradictory return for the first color verifies
                        # that this guard uses the X coordinate.
                        ret = int(not hit) if at == 306 else int(hit) if kind == "find_color" else (0 if hit else -1)
                        machine.supply_query(x, y, ret)
                        replies.append([at, x, y, ret])
                call_at = 324 if mode == 0 else 334 if mode in (2, 4) else None
                expected_calls = [(call_at, SWITCH)] if first and call_at and misses is not None else []
                assert [call for call in calls if call[1] == SWITCH] == expected_calls
                if misses is None:
                    assert not machine.done and tries >= 2 and 312 not in records
                else:
                    assert tries == misses + 1
                    assert (machine.reason, machine.pc) == ("missing_original_record", END if mode == 0 else 354)
                    if expected_calls:
                        assert records.index(call_at) < records.index(SWITCH) < records.index(call_at + 1)
                results.append(dict(first=first, last=last, party=mode, misses=misses,
                                    records=records, queries=replies, calls=calls, reason=machine.reason or "step_limit",
                                    next_record=machine.pc))
    observed = {at for case in results for at in case["records"]} & set(range(ENTRY, END))
    assert observed == set(range(ENTRY, END))
    return dict(cases=results, steps=sum(len(case["records"]) for case in results),
                observed_inferred_positions=sorted(observed), original_prefix_executed=False,
                real_actions_sent=False)


def main():
    raw = json.loads((PROJECT / "programs/07.json").read_text("utf8"))
    plans = tuple(json.loads((PROJECT / "data" / f"{name}.json").read_text("utf8")) for name in
                  ("cube-retained-tail", "cube-main", "cube-workers", "cube-routines"))
    prefix = build_prefix()
    setup = build_setup(raw, prefix)
    plan = build(raw, setup)
    report = verify(plan, setup, prefix, plans)
    for name, data in (("cube-character-wait", plan), ("cube-character-wait-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['actions'])} inferred positions; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
