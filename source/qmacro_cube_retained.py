"""Link all retained cube records, with explicit missing and host-wait boundaries."""
from qmacro_cube import CubeDependencyMissing, CubeMachine
from qmacro_cube_workers import CubeWorkerMachine


class CubeRetainedMachine(CubeWorkerMachine):
    def __init__(self, tail, main, workers, child, entry, read_global, values, root_slots, *, frame_slots=None):
        CubeMachine.__init__(self,child,857,read_global,values,frame_slots or {})
        actions = main['actions'] + workers['actions'] + tail['actions']
        missing = set(tail['missing_records'])
        retained = set(range(tail['total_records'])) - missing
        wrappers = {w['worker_entry'] for w in workers['worker_wrappers']}
        routines = {r['entry'] for p in (main,workers) for r in p['routines']}
        routines.update((3488,3510,3538,6444))
        root_entries = {0,531,717,854,6815,6816,6817}
        if entry not in routines | wrappers | root_entries:
            raise ValueError('Unreviewed retained entry')
        if entry==531 and 11 not in root_slots:
            raise CubeDependencyMissing('L531 needs root slot 11 from the missing prefix')
        if entry==0 and root_slots:
            raise ValueError('Normal root declaration starts with Empty slots')
        self._configure_linked({'actions':actions},retained,entry,frame_base=int(entry not in wrappers|root_entries),external_targets=missing)
        self.root_slots = dict(root_slots)
        self.boundaries = dict.fromkeys(missing,'missing_original_record')
        self.end_pc = tail['total_records']
        self.runner_message_ready = False
        self.ui_open = None

    def supply_capture_return(self, value):
        if self.pending is None or self.pending['kind']!='capture_intent':
            raise CubeDependencyMissing('No pending capture intent')
        if type(value) is not int:
            raise TypeError('Explicit integer capture result required')
        self.values['DM_RET'] = value
        self.pending = None

    def step(self):
        if self.done or self.pc in self.boundaries:
            return super().step()
        if self.pending is not None:
            raise CubeDependencyMissing('Reply required for L'+str(self.pending['record']))
        if self.pc==self.end_pc:
            self.done = True
            self.reason = 'program_end'
            return {'record':self.pc,'kind':self.reason}
        action = self.actions[self.pc]
        kind = action['kind']
        event = {'record':self.pc,'kind':kind}
        if kind=='runner_message' and not self.runner_message_ready:
            return dict(event,kind='waiting_message',form=action['source'])
        if kind=='ui_pump':
            if self.ui_open is None:
                raise CubeDependencyMissing('Explicit Form1 state required')
            if self.ui_open:
                return dict(event,kind='waiting_ui',form=action['source'])
        if kind=='capture_intent':
            event.update(rect=action['rect'],path=self.expr(action['path']))
            self.pending = dict(event)
        elif kind not in ('declare_root','declare_class','entry_dispatch','runner_message','ui_pump','final_record'):
            return super().step()
        self.pc += 1
        return event
