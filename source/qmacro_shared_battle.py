"""Event model for the separately preserved 01, 03 and 06 battle families."""
from datetime import datetime

from qmacro_cube import CubeDependencyMissing
from qmacro_cube_workers import CubeWorkerMachine


class SharedBattleMachine(CubeWorkerMachine):
    def __init__(self, plan, entry, read_global, values, *, control=None, clock=None, frame_fields=None, root_slots=None):
        routines = plan['routines'] + (control['routines'] if control else [])
        wrappers = {w['worker_entry'] for w in control['worker_wrappers']} if control else set()
        checkpoints = set(control.get('reviewed_checkpoints',())) if control else set()
        root_entry = control is not None and entry in control.get('root_entries',())
        if plan['module'] not in (1,3,6,9,10) or not (root_entry or entry in wrappers|checkpoints|{r['entry'] for r in routines}):
            raise ValueError('Unreviewed battle routine entry')
        if control and control['module']!=plan['module']:
            raise ValueError('Battle and coordinator module differ')
        self._initialize_state(entry,read_global,values,{})
        expected = {at for r in routines for at in range(r['entry'],r['last']+1)}
        if control:
            expected.update(control.get('host_records',()))
        self.boundaries = {int(k):v for k,v in control['boundaries'].items()} if control else {}
        actions = plan['actions'] + (control['actions'] if control else [])
        self._configure_linked({'actions':actions},expected,entry,frame_base=int(entry not in wrappers and not root_entry),
                               external_targets=self.boundaries)
        self.root_slots = {int(k):v for k,v in (root_slots or {}).items()}
        if root_entry and not set(control['root_required_slots']) <= self.root_slots.keys():
            raise CubeDependencyMissing('Missing explicit retained root slots at L'+str(entry))
        self.clock = datetime(*clock) if clock is not None else None
        if self.frames:
            self.frames[-1]['fields'] = dict(frame_fields or {})
        elif frame_fields:
            raise ValueError('Worker entry has no initial caller frame')

    def read(self, name):
        if name.startswith('BATTLE_FIELD_'):
            return self.frames[-1]['fields'].get(name.removeprefix('BATTLE_FIELD_'))
        return super().read(name)

    def expr(self, node):
        if 'frame_field' in node:
            return self.frames[-1]['fields'].get(node['frame_field'])
        return super().expr(node)

    def step(self):
        action = self.actions.get(self.pc, {})
        kind = action.get('kind')
        if self.done or self.pending is not None or kind not in (
                'builtin_picture','builtin_color','open_log_intent','capture_clock','screenshot_intent',
                'mouse_move','capture_intent','assign_frame_field','assign_frame_return','assign_ui_text'):
            event = super().step()
            if event['kind']=='frame_enter':
                self.frames[-1]['fields'] = {name:self.expr(node) for name,node in action.get('initial_fields',{}).items()}
            if event['kind']=='exit_script' and event['arguments']==[1]:
                self.reason = 'restart_requested'
            return event
        event = {'record':self.pc,'kind':kind}
        if kind=='capture_clock':
            if self.clock is None:
                raise CubeDependencyMissing('Explicit capture clock required')
            clock = self.clock
            timestamp = ''.join(str(part) for part in (clock.year,clock.month,clock.day,clock.hour,clock.minute,clock.second))
            self.frames[-1]['fields'][action['field']] = timestamp
        elif kind=='assign_ui_text':
            value = self.expr(action['value'])
            if type(value) not in (str, int):
                raise CubeDependencyMissing('Explicit string or integer UI assignment required')
            path = action['path']
            self.ui_values[path] = str(value)
            event.update(path=path, value=self.ui_values[path])
        elif kind=='assign_frame_field':
            self.frames[-1]['fields'][action['field']] = self.expr(action['value'])
        elif kind=='assign_frame_return':
            self.frames[-1]['return_value'] = self.expr(action['value'])
        elif kind in ('open_log_intent','screenshot_intent','mouse_move'):
            if kind=='screenshot_intent' and 'PIC' not in self.loaded:
                raise CubeDependencyMissing('PIC intent service not declared')
            event['arguments'] = [self.expr(node) for node in action['arguments']]
        elif kind=='capture_intent':
            event.update(rect=action['rect'],path=self.expr(action['path']))
            self.pending = event.copy()
        else:
            rect = action['rect'] if 'rect' in action else [self.expr(node) for node in action['rect_expressions']]
            similarity = action['similarity'] if 'similarity' in action else self.expr(action['similarity_expression'])
            event.update(rect=rect,spec=self.expr(action['spec']),similarity=similarity)
            if kind=='builtin_color':
                event['direction'] = action['direction']
            self.pending = event.copy()
        self.pc += 1
        return event

    def supply_capture_return(self, value):
        if self.pending is None or self.pending['kind']!='capture_intent':
            raise CubeDependencyMissing('No pending capture intent')
        if type(value) is not int:
            raise TypeError('Explicit integer capture result required')
        self.values['DM_RET'] = value
        self.pending = None

    def supply_builtin(self, x, y):
        request = self.pending
        if not request or request['kind'] not in ('builtin_picture','builtin_color'):
            raise CubeDependencyMissing('No pending Runner builtin query')
        if type(x) is not int or type(y) is not int:
            raise TypeError('Builtin coordinates must be integers')
        left, top, right, bottom = request['rect']
        if (x,y)!=(-1,-1) and not(left<=x<=right and top<=y<=bottom):
            raise ValueError('Coordinates outside Runner builtin rectangle')
        self.values.update(zip(self.actions[request['record']]['out_names'],(x,y)))
        self.pending = None

    def supply_query(self, x, y, return_value):
        action = self.actions[self.pending['record']] if self.pending else {}
        comparison = action.get('return_comparison')
        alternate = action.get('out_names')
        previous_xy = {n:self.values.get(n) for n in ('INTX','INTY')} if alternate else {}
        if comparison is None:
            super().supply_query(x,y,return_value)
            if alternate:
                self.values.update(previous_xy)
                self.values.update(zip(alternate,(x,y)))
            return None
        previous = self.values.get('DM_RET')
        if previous is None:
            numeric = 0
        elif isinstance(previous,bool):
            numeric = -1 if previous else 0
        elif type(previous) is int:
            numeric = previous
        else:
            raise CubeDependencyMissing('Unreviewed Variant type for DM_RET comparison')
        super().supply_query(x,y,return_value)
        if alternate:
            self.values.update(previous_xy)
            self.values.update(zip(alternate,(x,y)))
        self.values['DM_RET'] = previous
        result = numeric == return_value
        self.values[comparison] = result
        return result
