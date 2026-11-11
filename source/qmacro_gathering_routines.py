"""Owned event port of module08's intact repair, home and vitality bodies."""
import copy,re
from qmacro_fishing import FishingMachine,FishingDependencyMissing
from qmacro_gathering_walk import evaluate


class GatheringRoutinesMachine(FishingMachine):
    external_roles=frozenset(('repair_strategy','vitality_finish_mode','home_on_no_vitality','home_on_no_durability','sdk_marker','worker_id','simulation_mode'))
    def __init__(self,plan,read_context,entry=916):
        if plan.get('module')!=8 or plan.get('original_record_count')!=703 or entry not in (916,1277,1344):raise ValueError('Unreviewed gathering entry')
        if not callable(read_context):raise TypeError('Explicit context required')
        self.actions={a['record']:copy.deepcopy(a) for a in plan['actions']};expected=set(range(916,1276))|set(range(1277,1343))|set(range(1344,1621))
        if set(self.actions)!=expected or len(plan['actions'])!=703:raise ValueError('Gathering coverage differs')
        for a in self.actions.values():
            if 'target' in a and a['target'] not in expected:raise ValueError('Gathering target outside reviewed bodies')
        self.name_roles=copy.deepcopy(plan['name_roles']);self.read_context=read_context;self.pc=entry
        self.values={name:None for name in plan['local_roles']};self.frames=[{'slots':{},'value':None}]
        self.returns=[];self.last_return=None;self.flag=False;self.done=False;self.reason=None;self._waiting=None;self.loop_backs=0;self.loaded_services=set()

    def _role(self,name):
        if name in self.external_roles:
            value=self.read_context(name)
            if name=='sdk_marker':
                if not isinstance(value,str) or not re.fullmatch('[0-9a-fA-F]{6}',value):raise FishingDependencyMissing('Missing verified SDK marker')
            elif type(value) is not int:raise FishingDependencyMissing('Missing integer context: '+name)
            return value
        if name not in self.values:raise FishingDependencyMissing('Unassigned gathering value: '+name)
        return self.values[name]

    def _expr(self,node):
        if set(node)=={'numeric'}:return evaluate(node['numeric'],lambda name:self._role(self.name_roles.get(name,name)))
        if set(node)=={'slot'}:return self.frames[-1]['slots'].get(node['slot'])
        return super()._expr(node)

    def supply_query(self,x,y,return_value):
        if self._waiting is not None and self._waiting['kind']=='builtin_color':
            if any(type(v) is not int for v in (x,y,return_value)):raise TypeError('Explicit integer builtin outputs required')
            l,t,r,b=self._waiting['rect']
            if (x,y)!=(-1,-1) and not(l<=x<=r and t<=y<=b):raise ValueError('Outside inclusive builtin ROI')
            self.values.update(query_x=x,query_y=y,query_return=return_value);self._waiting=None
        else:super().supply_query(x,y,return_value)

    def step(self):
        if self.done:return super().step()
        if self._waiting is not None:raise FishingDependencyMissing('Observation is still required')
        a=self.actions[self.pc];kind=a['kind'];e={'record':self.pc,'kind':kind}
        if kind=='read_global':self.last_return=self._role(a['role']);e.update(role=a['role'],value=self.last_return)
        elif kind=='store_temp':self.frames[-1]['slots'][a['slot']]=self.last_return;e.update(slot=a['slot'],value=self.last_return)
        elif kind=='thread_control':e['arguments']=[self._expr(n) for n in a['arguments']]
        elif kind=='call':
            if a['target']!=1277 or len(self.frames)<2 or len(self.returns)>=8192:raise ValueError('Unreviewed gathering call')
            self.returns.append(self.pc+1);self.pc=a['target'];e['target']=self.pc;return e
        elif kind=='builtin_color':
            e.update(rect=list(a['rect']),color=self._expr(a['spec']),direction=a['direction'],similarity=a['similarity'],right_bottom_inclusive=True);self._request(e)
        else:return super().step()
        self.pc+=1;return e
