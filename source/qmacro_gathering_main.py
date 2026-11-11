"""Joined retained suffix and subroutines, with explicit erased-prefix boundary."""
import copy,math
from qmacro_gathering_routines import GatheringRoutinesMachine
from qmacro_fishing import FishingDependencyMissing


class GatheringMainMachine(GatheringRoutinesMachine):
    external_roles=GatheringRoutinesMachine.external_roles|frozenset(('gather_mode','minimap_center_x','minimap_center_y','walk_pi'))
    def __init__(self,plan,read_context,initial,entry=593):
        if plan.get('original_record_count')!=1091 or entry not in plan['root_entries']:raise ValueError('Unreviewed main suffix entry')
        super().__init__(plan['routines_plan'],read_context,916)
        for name in plan['required_initial_values']:
            if name not in initial:raise FishingDependencyMissing('Explicit prefix-dependent initial value required: '+name)
        self.values.update(copy.deepcopy(initial));self.name_roles=copy.deepcopy(plan['name_roles'])
        self.actions={a['record']:copy.deepcopy(a) for a in plan['actions']};self.missing=set(plan['missing_records'])
        if len(self.actions)!=1091:raise ValueError('Joined main coverage differs')
        self.pc=entry;self.main_cycles=0;self.frames[0]['root_sentinel']=True
    def _role(self,name):
        if name in ('minimap_center_x','minimap_center_y','walk_pi'):
            value=self.read_context(name)
            if type(value) not in (int,float) or not math.isfinite(value):raise FishingDependencyMissing('Explicit numeric context required: '+name)
            return value
        return super()._role(name)
    def _expr(self,node):
        if set(node)=={'root_slot'}:return self.frames[0]['slots'].get(node['root_slot'])
        return super()._expr(node)
    def supply_query(self,x,y,return_value):
        if self._waiting is not None and self.actions[self._waiting['record']].get('out_roles')==['target_x','target_y']:
            if any(type(v) is not int for v in (x,y,return_value)):raise TypeError('Explicit integer outputs required')
            l,t,r,b=self._waiting['rect']
            if (x,y)!=(-1,-1) and not(l<=x<r and t<=y<b):raise ValueError('Outside requested exclusive DM ROI')
            self.values.update(target_x=x,target_y=y,query_return=return_value);self._waiting=None
        else:super().supply_query(x,y,return_value)
    def step(self):
        if self.done:return super().step()
        if self._waiting is not None:raise FishingDependencyMissing('Observation is still required')
        if self.pc in self.missing:
            self.done=True;self.reason='missing_original_record';return {'record':self.pc,'kind':'missing_original_record'}
        a=self.actions[self.pc];kind=a['kind'];e={'record':self.pc,'kind':kind}
        if kind=='call':
            if a['target'] not in (689,916,1277,1344) or len(self.frames)<2 or len(self.returns)>=8192:raise ValueError('Unreviewed joined call')
            self.returns.append(self.pc+1);self.pc=a['target'];e['target']=self.pc;return e
        if kind=='root_store_temp':self.frames[0]['slots'][a['slot']]=self.last_return;e.update(slot=a['slot'],value=self.last_return)
        elif kind=='dynamic_delay':
            value=self._expr(a['value'])
            if type(value) is not int or value<0:raise ValueError('Invalid dynamic delay')
            e.update(kind='delay',milliseconds=value)
        elif kind=='move_to_ex':e['arguments']=[self._expr(n) for n in a['arguments']]
        elif kind=='program_end':self.done=True;self.reason='program_end'
        else:
            before=self.pc;e=super().step()
            if e['kind']=='exit_script':self.pc=before  # VBS ExitScript raises before dispatcher PC++.
            if before==687:self.main_cycles+=1
            return e
        self.pc+=1;return e
