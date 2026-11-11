"""Route preserved 08 entries to host, main, or polling worker contexts."""
from qmacro_gathering_main import GatheringMainMachine
from qmacro_gathering_worker import GatheringGWorker


class GatheringHostMachine:
    def __init__(self, plan, entry):
        if entry not in (0,plan['form_entry'],plan['form_gate'],plan['form_gate']+1):
            raise ValueError('Unreviewed gathering host entry')
        domain = {plan['form_entry'],plan['program_end'],*plan['host_records']}
        self.actions = {a['record']:a for a in plan['actions'] if a['record'] in domain}
        self.missing = set(plan['missing_records'])
        self.end = plan['total_records']
        self.pc = entry
        self.done = False
        self.reason = None
        self.returns = ()
        self.message_ready = False
        self.ui_open = True
        self.continue_iteration = False

    def step(self):
        at = self.pc
        if self.done:
            return dict(record=at,kind='done',reason=self.reason)
        if at in self.missing or at==self.end:
            self.done = True
            self.reason = 'missing_original_record' if at in self.missing else 'program_end'
            return dict(record=at,kind=self.reason)
        action = self.actions[at]
        kind = action['kind']
        if kind=='runner_message' and not self.message_ready:
            return dict(record=at,kind='waiting_message')
        if kind=='ui_pump' and self.ui_open:
            return dict(record=at,kind='waiting_ui')
        if kind=='iteration_end' and not self.continue_iteration:
            self.done = True
            self.reason = kind
            return dict(record=at,kind=kind)
        self.pc = action['target'] if kind=='jump' else at+1
        if kind=='iteration_end':
            kind = 'continue_iteration'
        elif kind=='program_end':
            kind = 'final_record'
        return dict(record=at,kind=kind)


def make_context(plan, main, worker, entry, read_context, *, initial=None):
    if entry in plan['root_entries']:
        return GatheringMainMachine(main,read_context,initial or {},entry)
    if entry==plan['worker_entry']:
        return GatheringGWorker(worker,read_context)
    return GatheringHostMachine(plan,entry)
