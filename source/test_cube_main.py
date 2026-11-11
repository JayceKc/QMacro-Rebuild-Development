import json
import unittest

from export_cube_routines import PROJECT
from export_cube_main import build
from qmacro_cube_main import CubeMainMachine


def load(relative):
    return json.loads((PROJECT / relative).read_text(encoding='utf8'))


PLAN = load('data/cube-main.json')
CHILD = load('data/cube-routines.json')
FIRST = 'VF0ADACDECCD2BFD14D6A65757378756D'
LAST = 'VF0ADACDECE99BF954D6A65757378756D'
NEXT = 'V9FC0A2A5CEBFBCC64D6A65757378756D'
COUNTER = 'V8080D6BCC7B6BF904D6A65757378756D'
WORKER = 'V9BBAD991CA85B8D1042E65757378756D'


def scalar_names(node):
    if isinstance(node, dict):
        if set(node) == {'name'} and not node['name'].startswith('CUBE_SLOT_'):
            yield node['name']
        for value in node.values():
            yield from scalar_names(value)
    elif isinstance(node, list):
        for item in node:
            yield from scalar_names(item)


def replay(overrides=None, misses=(), stop_after=None, limit=3000):
    # Explicit synthetic prefix state, used only by the controlled fixture.
    shared = {a['key']: 0 for a in PLAN['actions'] if a['kind'] in ('read_global', 'write_global')}
    shared.update({FIRST: 1, LAST: 24, NEXT: 1, WORKER: 4567, 'V8186B4D47378756D': '123456'})
    shared.update(overrides or {})
    values = {name: 0 for name in scalar_names(PLAN['actions'])}
    machine = CubeMainMachine(PLAN, CHILD, lambda key, record: shared[key], values, {5: 777, 255: 913})
    events = []
    for _ in range(limit):
        if machine.done:
            break
        event = machine.step()
        events.append(event)
        kind = event['kind']
        if kind == 'write_global':
            shared[event['key']] = event['value']
        if kind == 'dm_real_mouse_intent':
            machine.supply_dm_return(1)
        if kind in ('find_pic', 'find_color'):
            hit = event['record'] not in (*misses, 5153)
            x, y = (event['rect'][0] + 1, event['rect'][1] + 2) if hit else (-1, -1)
            machine.supply_query(x, y, 0)
        if kind == 'random_int':
            machine.supply_random(event['lower'])
        if event['record'] == stop_after:
            break
    return machine, shared, events


class CubeMainTests(unittest.TestCase):
    def test_saved_original_nested_calls_and_all_three_ui_writes(self):
        from compare_cube_main import compare
        native = load('verification/original-cube-main.json')
        cases = load('data/cube-main-cases.json')['cases']
        result = compare(native, cases, PLAN, CHILD)
        self.assertEqual((result['cases'], result['external_events'], result['frame_restorations']), (31, 5151, 70))
        self.assertEqual(result['ui_write_records'], [2363, 2705, 3014])
        self.assertEqual(result['covered_call_sites'], [1755, 1760, 2159, 2241, 2250, 3377, 3425])

    def test_all_parent_and_helper_call_sites_match_original_frames(self):
        original = load('programs/07.json')
        rebuilt = build(original)
        self.assertEqual(rebuilt['actions'], PLAN['actions'])
        self.assertEqual(len(PLAN['actions']), 3977)
        self.assertEqual(len(rebuilt['joined_calls']), 43)
        self.assertEqual(sum(1677 <= c['record'] <= 3363 for c in rebuilt['joined_calls']), 41)
        self.assertEqual([a for a in rebuilt['actions'] if any(r['entry'] <= a['record'] <= r['last'] for r in CHILD['routines'])], CHILD['actions'])

    def test_nested_button_and_altq_return_to_two_distinct_parents(self):
        machine, _, events = replay(stop_after=2242)
        self.assertEqual([(e['record'], e['target']) for e in events if e['kind'] == 'call'], [(2241, 3365), (3377, 6657)])
        self.assertEqual([(e['record'], e['target']) for e in events if e['kind'] == 'return'], [(6689, 3378), (3486, 2242)])
        self.assertEqual(machine.slots[255], 913)
        self.assertEqual(machine.returns, [])
        self.assertEqual(len(machine.frames), 1)
        self.assertIsNone(events[-1]['value'])

    def test_character_and_weekly_children_return_then_parent_requests_worker_resume(self):
        machine, shared, events = replay({'V89BBD3BD7378756D': 1, 'VF4C1DE94BBB6BB9C4D6A65757378756D': 1}, misses=(1743,), stop_after=2169)
        self.assertIn((1755, 5020), [(e['record'], e['target']) for e in events if e['kind'] == 'call'])
        self.assertIn((2159, 857), [(e['record'], e['target']) for e in events if e['kind'] == 'call'])
        self.assertEqual(shared[NEXT], 2)
        self.assertEqual(shared[COUNTER], 0)
        self.assertIsNone(machine.slots[5])
        self.assertIsNone(machine.slots[47])
        self.assertEqual((len(machine.frames), machine.slots[255]), (1, 913))
        self.assertEqual(events[-1]['arguments'], [4567, 2])

    def test_completion_child_stops_before_parent_return_store(self):
        machine, _, events = replay({FIRST: 0, 'V89BBD3BD7378756D': 1}, misses=(1743,))
        self.assertEqual((machine.reason, machine.pc), ('script_stop', 6746))
        self.assertIn(1760, [e['record'] for e in events])
        self.assertNotIn(1761, [e['record'] for e in events])
        self.assertEqual(machine.returns, [1761])

    def test_counter_writeback_precedes_ui_text(self):
        machine, shared, events = replay(misses=(1694,), stop_after=2363)
        self.assertEqual(shared[COUNTER], 1)
        self.assertEqual(machine.ui_values['Form1.InputBox2.Text'], '1')
        self.assertEqual([e['record'] for e in events if e['record'] in (2352, 2357, 2363)], [2352, 2357, 2363])

    def test_missing_sdk_observation_retries_without_calling_children(self):
        machine, _, events = replay(misses=(1690,), limit=150)
        self.assertFalse(machine.done)
        self.assertGreater(sum(e['record'] == 1690 for e in events), 1)
        self.assertFalse(any(e['kind'] == 'call' for e in events))
