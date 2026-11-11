"""Link the cube startup and retained outer loop while preserving L445 uncertainty."""
from collections import Counter
import json

from build_cube_character_setup import build as build_setup
from build_cube_character_wait import build as build_wait
from build_cube_lucky_bridge import build as build_bridge, machine_for
from build_cube_prefix import INVENTORY, OUTPUT, PROJECT, build as build_prefix, replay as replay_prefix
from build_cube_start_workers import build as build_workers, decode_identifier
from export_cube_routines import translate
from replay_cube_main import build_cases as battle_cases
from replay_cube_retained import build_cases as tail_cases

ENTRY, GATE, VISUAL, END = 444, 445, 451, 467
FIRST_BATTLE, LOOP_BACK, LOOP_EXIT = 1677, 853, 854


def build(raw):
    code, strings = raw["code"], raw["strings"]
    pool = json.loads((INVENTORY / "07-prefix-inventory.json").read_text("utf8"))["prefix_pool"]
    missing = set(raw["missing_records"])
    positions = set(range(ENTRY, END)) - {GATE}
    assert all(at in missing and code[at][0] == 255 for at in positions | {GATE})
    candidate = dict(raw, code=list(code), missing_records=missing - positions)

    def emit(at, op, arg):
        candidate["code"][at] = [op, code[at][1], arg, code[at][3]]
        if op in (2, 4, 27, 30):
            assert pool[arg]["index"] == arg and pool[arg]["value"] == strings[arg]

    frame_name = strings[370].split("=New ", 1)[1].split(":", 1)[0]
    assert strings[code[24][2]].startswith(f"Class {frame_name}:")
    assert decode_identifier(frame_name.rsplit("_V", 1)[1]) == "第一次打怪"
    assert code[446][1] == code[447][1] == code[448][1] == 227
    for at, sl in ((444, 369), (446, 370), (448, 371), (449, 372), (450, 373)):
        emit(at, 30 if pool[sl]["kind"] == "decoded-text" else 2, sl)
    emit(447, 12, FIRST_BATTLE)
    assert code[LOOP_BACK][0] == 16 and LOOP_BACK + code[LOOP_BACK][2] == VISUAL
    assert strings[code[1685][2]] == "Sgn(vbTrue)" and code[1686][:3:2] == [6, 1675]
    assert code[3363][0] == 13
    incoming_tail = [(at, op) for at, (op, _, arg, _) in enumerate(code)
                     if (op in (6, 16, 24) and at + arg in (3361, 3362, 3363))
                     or (op in (5, 12) and arg in (3361, 3362, 3363))]
    assert incoming_tail == [(1686, 6)]

    sl = 374
    for at in range(VISUAL, END):
        op, location, operand, _ = code[at + 4185]
        assert location - code[at][1] == 3812
        if op == 6:
            assert at + 4185 + operand == {452: 4686, 458: 4685, 462: 4685, 466: 4668}[at]
            emit(at, op, (LOOP_EXIT if at == 452 else LOOP_BACK) - at)
        else:
            qualifier = "F2730835_2229_445E_97C7_l3F7612771DA."
            assert strings[sl] == strings[operand].replace(qualifier, "")
            emit(at, op, sl)
            sl += 1
    assert sl == 386
    actions = translate(candidate, ((444, 444, "入場延遲"), (446, 466, "首次入場與視覺迴圈")),
                        external_targets=(FIRST_BATTLE, LOOP_BACK, LOOP_EXIT))["actions"]
    assert Counter(a["source_sl"] for a in actions if a["source_sl"] is not None) == Counter(range(369, 386))
    for action in actions:
        action["candidate_opcode"] = action.pop("opcode")
        action.pop("operand")
        action["inferred"] = True
    return dict(module=7, entry=ENTRY, actions=actions, original_values_recovered=0,
                unresolved_gate=dict(record=GATE, location=code[GATE][1], alternatives=[446, 449]),
                battle_entry=FIRST_BATTLE, battle_return_record=3363, battle_tail_only_branch=1686,
                preserved_visual=[4636, 4651], preserved_loop_back=LOOP_BACK,
                direction_miss_alternative=480)


def verify(plan, raw, prefix, plans):
    setup = build_setup(raw, prefix)
    wait = build_wait(raw, setup)
    workers = build_workers(raw)
    bridge = build_bridge(raw, plans[0], plans[2])
    tail = tail_cases(plans[0], plans[2])[1]
    battle = battle_cases(plans[1])[0]
    combined = dict(entry=setup["entry"], worker_entry=-1,
                    actions=setup["actions"] + wait["actions"] + workers["actions"] +
                    plan["actions"] + bridge["actions"])
    emote_key = next(s["key"] for s in prefix["settings"] if s["role"] == "emote")
    cases = []
    scenarios = [(None, None, 0), (446, None, 0)]
    scenarios += [(449, miss, mode) for mode in range(5) for miss in (None, 456, 460, 464)]
    for assumption, miss, mode in scenarios:
        options = {s["property"]: 0 for s in prefix["settings"]}
        options.update({"Form1.ComboBox99.ListIndex": mode, "Form1.ComboBox1.ListIndex": 2})
        init = replay_prefix(prefix, options, version="7.2450", sdk_value="AB12CD")
        shared = dict(battle["shared"], **tail["shared"])
        shared.update(init["shared"])
        values = dict(battle["values"], **tail["values"])
        values[emote_key] = init["local"]["emote"]
        machine = machine_for(combined, plans, shared, values, setup["entry"])
        if assumption is not None:
            machine.actions[GATE] = dict(record=GATE, kind="jump", target=assumption)
            del machine.boundaries[GATE]
        records, calls, queries = [], [], []
        for _ in range(1100):
            if machine.done:
                break
            event = machine.step()
            at, kind = event["record"], event["kind"]
            records.append(at)
            if kind == "write_global":
                shared[event["key"]] = event["value"]
            elif kind == "call":
                calls.append((at, event["target"]))
            elif kind == "dm_real_mouse_intent":
                machine.supply_dm_return(1)
            elif kind == "worker_start":
                machine.supply_worker_id(1000 + at)
            elif kind == "random_int":
                machine.supply_random(event["lower"])
            elif kind in ("find_pic", "find_color"):
                found = at != miss or any(query[0] == at for query in queries)
                if at in (496, 5153, 563):
                    found = False
                x, y = (event["rect"][0] + 1, event["rect"][1] + 2) if found else (-1, -1)
                ret = int(not found) if at in (456, 460, 464) else (
                    int(found) if kind == "find_color" else (0 if found else -1))
                machine.supply_query(x, y, ret)
                queries.append((at, x, y, ret))
            if at == 557:
                assert event["value"] == "AB12CD"
                if records.count(557) == 2:
                    break
        if assumption is None:
            assert (machine.reason, machine.pc) == ("missing_original_record", GATE)
        elif assumption == 446:
            assert (447, FIRST_BATTLE) in calls and 1685 in records
            assert 3363 not in records and 448 not in records and VISUAL not in records
        else:
            assert records[-1] == 557 and 467 in records and 486 in records
            assert records.count(LOOP_BACK) == 1 + int(miss is not None)
            assert records.count(VISUAL) == 2 + int(miss is not None)
            assert [at for at in records if at in (557, 659, 852)] == [557, 659, 852, 557]
            assert (531 in records) == (mode in (0, 1, 3))
        cases.append(dict(gate_assumption=assumption, first_miss=miss, party=mode, records=records,
                          calls=calls, queries=queries, next_record=machine.pc, reason=machine.reason or "fixture_limit"))
    return dict(cases=cases, steps=sum(len(c["records"]) for c in cases),
                original_prefix_executed=False, real_actions_sent=False)


def main():
    raw = json.loads((PROJECT / "programs/07.json").read_text("utf8"))
    plans = tuple(json.loads((PROJECT / "data" / f"{name}.json").read_text("utf8")) for name in
                  ("cube-retained-tail", "cube-main", "cube-workers", "cube-routines"))
    prefix = build_prefix()
    plan = build(raw)
    plan["source_program_sha256"] = prefix["source_program_sha256"]
    report = verify(plan, raw, prefix, plans)
    for name, data in (("cube-visual-loop", plan), ("cube-visual-loop-verification", report)):
        (OUTPUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(f"{len(plan['actions'])} inferred positions; {len(report['cases'])} cases; {report['steps']} steps")


if __name__ == "__main__":
    main()
