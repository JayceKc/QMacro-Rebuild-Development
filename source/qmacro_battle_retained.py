"""Replay preserved battle records with explicit message, UI and missing-data boundaries."""
from collections import deque

from qmacro_builtin_color import unpack_coordinates
from qmacro_cube import CubeDependencyMissing
from qmacro_shared_battle import SharedBattleMachine


class RetainedBattleMachine(SharedBattleMachine):
    def __init__(self, base, control, entry, read_global, values, *, root_slots=None, clock=None,
                 message_ready=False, ui_open=True, continue_iteration=False):
        gate = control['form_gate']
        suffix = control.get('root_entries',())
        roots = {0,gate-1,gate,gate+1,*suffix}
        routines = {r['entry'] for r in base['routines']+control['routines']}
        wrappers = {w['worker_entry'] for w in control['worker_wrappers']}
        if entry not in roots|routines|wrappers:
            raise ValueError('Unreviewed retained root entry')
        root = dict(control,root_entries=[entry] if entry in roots else [],
                    root_required_slots=control.get('root_required_slots',[]) if entry in suffix else [])
        super().__init__(base,entry,read_global,values,control=root,root_slots=root_slots,clock=clock)
        self.end = control['total_records']
        self.callback_names = {row['event']:row['entry'] for row in control['callbacks']}
        self.callbacks = deque()
        self.message_ready = message_ready
        self.ui_open = ui_open
        self.continue_iteration = continue_iteration
        self.loaded_operands = set()

    def queue_ui_event(self, name):
        self.callbacks.append(self.callback_names[name])

    def supply_cursor(self, packed):
        if self.pending is None or self.pending['kind']!='builtin_cursor':
            raise CubeDependencyMissing('No pending Runner cursor query')
        x,y = unpack_coordinates(packed)
        outputs = self.actions[self.pending['record']]['out_names']
        self.values.update(zip(outputs,(x,y)))
        self.pending = None
        return x,y

    def step(self):
        if self.done or self.pending is not None or self.pc in self.boundaries:
            return super().step()
        if self.pc==self.end:
            self.done = True
            self.reason = 'program_end'
            return dict(record=self.pc,kind=self.reason)
        action = self.actions[self.pc]
        at,kind = self.pc,action['kind']
        event = dict(record=at,kind=kind)
        if kind=='runner_message' and not self.message_ready:
            return dict(event,kind='waiting_message')
        if kind=='ui_pump' and self.ui_open:
            if not self.callbacks:
                return dict(event,kind='waiting_ui')
            self.returns.append(at)
            self.pc = self.callbacks.popleft()
            return dict(event,kind='dispatch_ui_event',target=self.pc)
        if kind=='callback_frame_enter':
            if self.frames or len(self.returns)!=1:
                raise ValueError('Callback must enter from the root Form1 pump')
            self.frames.append(dict(slots={},fields={},return_value=None,class_name=action['class_name']))
            self.slots = self.frames[-1]['slots']
        elif kind=='delete_folder_intent':
            if 'FILE' not in self.loaded:
                raise ValueError('Missing FILE adapter declaration')
            event['path'] = action['path']
        elif kind=='message_notify':
            event.update(level=action['level'],message=action['message'])
        elif kind=='ui_read':
            self.temporary = self.ui_values[action['path']]
            event.update(path=action['path'],value=self.temporary)
        elif kind=='assign_right_text':
            value = self.slots.get(action['input_slot'])
            if not isinstance(value,str):
                raise CubeDependencyMissing('Explicit textbox string required')
            length = action['count']*2
            self.slots[action['slot']] = value.encode('utf-16-le','surrogatepass')[-length:].decode('utf-16-le','surrogatepass')
        elif kind=='builtin_cursor':
            self.pending = event.copy()
        elif kind=='load_service_intent':
            if action['operand'] not in self.loaded_operands:
                self.loaded_operands.add(action['operand'])
                return super().step()
            event['kind'] = 'reuse_service'
        elif kind=='iteration_end' and self.continue_iteration:
            event['kind'] = 'continue_iteration'
        elif kind not in ('declaration','entry_dispatch','runner_message','ui_pump','final_record'):
            return super().step()
        self.pc += 1
        return event
