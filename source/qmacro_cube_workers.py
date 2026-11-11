"""Cooperative event model for the retained worker coordinator and bodies."""
import copy
import re

from export_cube_workers import EXTERNAL_TARGETS, WORKER_RANGES
from qmacro_cube import CubeDependencyMissing, CubeMachine
from qmacro_cube_main import CubeMainMachine


class CubeWorkerMachine(CubeMainMachine):
    def __init__(self, plan, child_plan, entry, read_global, values, frame_slots, root_slots):
        CubeMachine.__init__(self, child_plan, 857, read_global, values, frame_slots)
        expected = {i for first,last,_ in WORKER_RANGES for i in range(first,last+1)}
        wrappers = {w['worker_entry'] for w in plan['worker_wrappers']}
        if entry not in wrappers | {first for first,_,_ in WORKER_RANGES}:
            raise ValueError('Unreviewed worker entry')
        self._configure_linked(plan, expected, entry, frame_base=int(entry not in wrappers and entry != 717),
                               external_targets=EXTERNAL_TARGETS)
        self.root_slots = dict(root_slots)
        self.boundaries = EXTERNAL_TARGETS

    def read(self, name):
        match = re.fullmatch(r'CUBE_ROOT_SLOT_(\d+)', name)
        if match:
            return self.root_slots.get(int(match[1]))
        return super().read(name)

    def expr(self, node):
        if 'root_slot' in node:
            return self.root_slots.get(node['root_slot'])
        return super().expr(node)

    def supply_worker_id(self, value):
        if self.pending is None or self.pending['kind'] != 'worker_start':
            raise CubeDependencyMissing('No pending worker start')
        if type(value) is not int or not -(2**31) <= value < 2**31:
            raise ValueError('Expected signed 32-bit worker ID')
        self.temporary = value
        self.pending = None

    def step(self):
        if self.done:
            return super().step()
        if self.pending is not None:
            raise CubeDependencyMissing('Reply required for L' + str(self.pending['record']))
        if self.pc in self.boundaries:
            self.done = True
            self.reason = self.boundaries[self.pc]
            return {'record': self.pc, 'kind': self.reason}
        action = self.actions[self.pc]
        kind = action['kind']
        event = {'record':self.pc, 'kind':kind}
        if kind == 'iteration_end':
            self.done = True
            self.reason = 'iteration_end'
            return event
        if kind == 'worker_start':
            event['target'] = action['target']
            self.pending = dict(event)
        elif kind == 'assign_root_slot':
            value = self.expr(action['value'])
            self.root_slots[action['slot']] = value
            event.update(slot=action['slot'], value=value)
        elif kind in ('find_color', 'find_pic') and 'rect_expressions' in action:
            rect = [self.expr(node) for node in action['rect_expressions']]
            if any(type(v) is not int for v in rect) or rect[0]>=rect[2] or rect[1]>=rect[3]:
                raise CubeDependencyMissing('Invalid dynamic query rectangle')
            event.update(rect=rect, spec=self.expr(action['spec']), similarity=action['similarity'], direction=action['direction'])
            if kind == 'find_pic':
                event['delta'] = self.expr(action['delta'])
            self.pending = copy.deepcopy(event)
        else:
            return super().step()
        self.pc += 1
        return event
