"""Run the preserved module05 root suffix and host transitions as events."""
from qmacro_fishing import FishingDependencyMissing, FishingMachine


class FishingRetainedMachine(FishingMachine):
    def __init__(self, routines, plan, read_context, entry=0, *, initial=None):
        if entry not in (0,504,541,879,924,925,926) or plan['module']!=5:
            raise ValueError('Unreviewed fishing entry')
        super().__init__(routines,read_context,entry if entry in (541,879) else 541)
        self.actions = {a['record']:a for a in plan['actions']}
        self.missing = set(plan['missing_records'])
        self.end = plan['total_records']
        if len(self.actions)!=len(plan['actions']) or set(self.actions)!=set(range(self.end))-self.missing:
            raise ValueError('Fishing retained domain differs')
        self.pc = entry
        self.values.update(initial or {})
        if entry==504 and not {'failure_count','rebait'} <= self.values.keys():
            raise FishingDependencyMissing('Explicit fishing suffix state required')
        if entry not in (541,879):
            self.frames.clear()
        self.message_ready = False
        self.ui_open = True
        self.continue_iteration = False

    def step(self):
        if self.done or self._waiting is not None:
            return super().step()
        at = self.pc
        if at in self.missing or at==self.end:
            self.done = True
            self.reason = 'missing_original_record' if at in self.missing else 'program_end'
            return dict(record=at,kind=self.reason)
        kind = self.actions[at]['kind']
        if kind=='runner_message' and not self.message_ready:
            return dict(record=at,kind='waiting_message')
        if kind=='ui_pump' and self.ui_open:
            return dict(record=at,kind='waiting_ui')
        if kind=='iteration_end' and not self.continue_iteration:
            self.done = True
            self.reason = kind
            return dict(record=at,kind=kind)
        if kind in ('declaration','entry_dispatch','runner_message','ui_pump','iteration_end','final_record'):
            self.pc += 1
            return dict(record=at,kind='continue_iteration' if kind=='iteration_end' else kind)
        event = super().step()
        if kind=='exit_script':
            self.pc = at
        return event
