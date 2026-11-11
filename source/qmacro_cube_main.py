"""Owned linked cube event machine, keeping parent frame and call stacks separate.

No original source execution or native dependencies. Joined equivalence has not
yet been established in the fixed guest, even though child bodies have evidence.
"""
import copy
from qmacro_cube import CubeMachine,CubeDependencyMissing


class CubeMainMachine(CubeMachine):
    def __init__(self,plan,child_plan,read_global,values,frame_slots,entry=1677):
        super().__init__(child_plan,857,read_global,values,frame_slots)
        expected=set(range(1677,3364))|set(range(3365,3487))|set(range(6657,6690))|set(self.actions)
        if entry!=1677:raise ValueError('Only retained parent entry reviewed')
        self._configure_linked(plan, expected, entry)

    def _configure_linked(self, plan, expected, entry, *, frame_base=1, external_targets=()):
        if len(plan['actions'])!=len(expected) or {a['record'] for a in plan['actions']}!=expected:raise ValueError('Unreviewed joined cube plan')
        self.actions={a['record']:copy.deepcopy(a) for a in plan['actions']}
        for a in self.actions.values():
            if 'target' in a and a['target'] not in expected and a['target'] not in external_targets:raise ValueError('Joined branch leaves preserved bodies')
        self.pc = entry
        self.frame_base = frame_base
        self.frames = [{'slots': self.slots, 'return_value': None, 'class_name': 'explicit_parent_frame'}] if frame_base else []
        self.returns = []
        self.ui_values = {}
        self.pending_frame = False

    def supply_dm_return(self,value):
        if self.pending is None or self.pending['kind'] != 'dm_real_mouse_intent':
            raise CubeDependencyMissing('No pending DM configuration result')
        if type(value) is not int:
            raise TypeError('Explicit integer DM configuration result required')
        self.values[self.pending['name']] = value
        self.pending = None

    def step(self):
        if self.done:
            return {'record': self.pc, 'kind': 'done', 'reason': self.reason}
        if self.pending is not None:
            raise CubeDependencyMissing('Reply required for L' + str(self.pending['record']))
        a = self.actions[self.pc]
        k = a['kind']
        e = {'record': self.pc, 'kind': k}
        next_pc = self.pc + 1
        if k=='frame_enter':
            if (not self.frames and (self.frame_base or self.returns)) or self.pending_frame:
                raise CubeDependencyMissing('No active parent or previous uncalled frame')
            if len(self.frames) >= 8192:
                raise ValueError('Frame bound exceeded')
            self.frames.append({'slots': {}, 'return_value': None, 'class_name': a['class_name']})
            self.slots = self.frames[-1]['slots']
            self.pending_frame = True
            e.update(class_name=a['class_name'], depth=len(self.frames))
        elif k=='call':
            if not self.pending_frame or len(self.frames) != len(self.returns) + self.frame_base + 1:
                raise CubeDependencyMissing('Call without reviewed frame setup')
            self.pending_frame = False
            self.returns.append(next_pc)
            next_pc = a['target']
            e.update(target=next_pc, depth=len(self.frames))
        elif k=='frame_restore_intent':
            if not self.frames:
                raise CubeDependencyMissing('Frame already restored')
            frame = self.frames.pop()
            self.temporary = frame['return_value']
            self.slots = self.frames[-1]['slots'] if self.frames else {}
            self.frame_restore_requested = True
            e.update(value=self.temporary, depth=len(self.frames))
        elif k=='return':
            if len(self.frames) != len(self.returns) + self.frame_base - 1:
                raise CubeDependencyMissing('Return before caller frame restoration')
            if self.returns:
                next_pc = self.returns.pop()
                e['target'] = next_pc
            else:
                self.done = True
                self.reason = 'routine_return'
            e['depth'] = len(self.frames)
        elif k=='ui_write':
            value = self.temporary
            if value is None:
                text = ''
            elif type(value) in (str, int):
                text = str(value)
            else:
                raise CubeDependencyMissing('Unreviewed CStr conversion for UI value')
            self.ui_values[a['path']] = text
            e.update(path=a['path'], value=text)
        elif k in ('key_down','key_up','thread_control_intent','dm_error_policy_intent'):
            e['arguments']=[self.expr(x) for x in a['arguments']]
        elif k=='create_dm_intent':pass
        elif k=='dm_real_mouse_intent':
            e.update(name=a['name'], arguments=[self.expr(x) for x in a['arguments']])
            self.pending = copy.deepcopy(e)
        else:return super().step()
        self.pc=next_pc
        return e
