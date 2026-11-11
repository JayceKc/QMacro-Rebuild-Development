"""Explicit event port of module08 L890..914; no native code/input/timers.

This is a polling worker, not a function that normally returns. The unknown
SDK marker and every vision observation must be supplied by the caller.
"""
import copy,re


class GatheringDependencyMissing(RuntimeError):pass


class GatheringGWorker:
    def __init__(self,plan,read_context):
        if plan.get('module')!=8 or plan.get('entry')!=890:raise ValueError('Unreviewed worker plan')
        self.actions={a['record']:copy.deepcopy(a) for a in plan['actions']}
        if set(self.actions)!=set(range(890,915)):raise ValueError('Worker record coverage differs')
        if not callable(read_context):raise TypeError('Explicit context provider required')
        self.read_context=read_context;self.pc=890;self.done=False;self.reason=None
        self.waiting=None;self.values={};self.flag=False;self.loops=0

    def stop(self):
        self.done=True;self.reason='cancelled';self.waiting=None

    def supply_query(self,x,y,return_value):
        if self.waiting is None:raise GatheringDependencyMissing('No outstanding observation')
        if any(type(v) is not int for v in (x,y,return_value)):raise TypeError('Integer query outputs required')
        l,t,r,b=self.waiting['arguments'][:4]
        if (x,y)!=(-1,-1) and not (l<=x<r and t<=y<b):raise ValueError('Outside exclusive DM query rectangle')
        self.values.update(query_x=x,query_y=y,query_return=return_value);self.waiting=None

    def step(self):
        if self.done:return {'record':self.pc,'kind':'done','reason':self.reason}
        if self.waiting is not None:raise GatheringDependencyMissing('An observation is still required')
        a=self.actions[self.pc];kind=a['kind'];e={'record':self.pc,'kind':kind};next_pc=self.pc+1
        if kind=='delay':e['value']=a['milliseconds']
        elif kind=='load_vision_intent':e['value']='dm.dmsoft'
        elif kind=='set_show_error':e['value']=a['value']
        elif kind=='test':
            self.flag=True if a['condition']=='true' else self.values['query_x']>0 if a['condition']=='query_x>0' else self.values['query_x']>=0
            e['result']=self.flag
        elif kind=='if_zero':
            if not self.flag:next_pc=a['target']
        elif kind=='jump':
            next_pc=a['target'];self.loops+=int(next_pc<=self.pc)
        elif kind=='read_sdk':
            value=self.read_context('sdk_marker')
            if not isinstance(value,str) or not re.fullmatch('[0-9a-fA-F]{6}',value):raise GatheringDependencyMissing('Missing verified SDK marker')
            self.values['sdk_marker']=value;e['value']=value
        elif kind=='store_sdk':
            self.values['frame_slot_1']=self.values['sdk_marker'];e['value']=self.values['frame_slot_1']
        elif kind in ('find_color','find_pic'):
            args=copy.deepcopy(a['arguments'])
            if kind=='find_color':args[4]=self.values['frame_slot_1']+'-151515'
            e['arguments']=args;self.waiting=copy.deepcopy(e)
        elif kind=='key_press':
            mode=self.read_context('simulation_mode')
            if type(mode) is not int:raise GatheringDependencyMissing('Missing integer simulation mode')
            e['value']=['G',mode,1]
        elif kind=='frame_restore':raise ValueError('Unreachable cleanup reached without changing original loop')
        elif kind=='return':raise ValueError('Unreachable return reached without changing original loop')
        else:raise ValueError('Unreviewed action '+kind)
        self.pc=next_pc;return e
