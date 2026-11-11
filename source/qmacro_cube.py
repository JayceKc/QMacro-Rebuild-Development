"""Owned, closed event interpreter for module07's 2,135 preserved records.

Only data and events: no source eval, COM, input injection, real delay or OS exit.
Requires explicit observations and caller state. Native equivalence is unverified.
"""
import copy,re
from qmacro_gathering_walk import evaluate


class CubeDependencyMissing(RuntimeError):pass


class CubeMachine:
    def __init__(self,plan,entry,read_global,values,frame_slots):
        if plan.get('module')!=7 or plan.get('original_record_count')!=2135:raise ValueError('Unreviewed cube plan')
        self.actions={a['record']:copy.deepcopy(a) for a in plan['actions']}
        expected=set(range(857,1494))|set(range(5020,6443))|set(range(6740,6815))
        if set(self.actions)!=expected or len(plan['actions'])!=2135:raise ValueError('Cube coverage differs')
        if entry not in (857,5020,6740):raise ValueError('Unreviewed cube entry')
        self._initialize_state(entry,read_global,values,frame_slots)

    def _initialize_state(self,entry,read_global,values,frame_slots):
        if not callable(read_global):raise ValueError('Explicit global provider required')
        if not isinstance(values,dict) or not isinstance(frame_slots,dict):raise TypeError('Explicit caller values and frame slots required')
        self.values={k.upper():v for k,v in values.items()};self.slots=copy.deepcopy(frame_slots)
        self.read_global=read_global;self.global_writes=[];self.temporary=None;self.flag=None;self.pc=entry
        self.done=False;self.reason=None;self.pending=None;self.loaded=set();self.frame_restore_requested=False

    def read(self,name):
        m=re.fullmatch(r'CUBE_SLOT_(\d+)',name)
        if m:return self.slots.get(int(m[1])) # Caller explicitly supplied a frame; uninitialized VBS fields are Empty.
        if name not in self.values:raise CubeDependencyMissing('Missing caller value '+name+' at L'+str(self.pc))
        return self.values[name]

    def expr(self,node):
        if 'const' in node:return node['const']
        if 'slot' in node:return self.slots.get(node['slot'])
        if 'temporary' in node:return self.temporary
        if 'numeric' in node:return evaluate(node['numeric'],self.read)
        if 'concat' in node:
            def text(v):
                if v is None:return ''
                if isinstance(v,bool):return 'True' if v else 'False'
                if type(v) in (str,int):return str(v)
                raise CubeDependencyMissing('Unreviewed string conversion')
            return ''.join(text(self.expr(x)) for x in node['concat'])
        raise ValueError('Unreviewed cube expression')

    def supply_query(self,x,y,return_value):
        p=self.pending
        if p is None or p['kind'] not in ('find_pic','find_color'):raise CubeDependencyMissing('No pending query')
        if any(type(v) is not int for v in (x,y,return_value)):raise TypeError('Query outputs must be integers')
        l,t,r,b=p['rect']
        if (x,y)!=(-1,-1) and not(l<=x<r and t<=y<b):raise ValueError('Coordinates outside original exclusive DM ROI')
        self.values.update(INTX=x,INTY=y,DM_RET=return_value);self.pending=None

    def supply_random(self,value):
        p=self.pending
        if p is None or p['kind']!='random_int':raise CubeDependencyMissing('No pending random request')
        if type(value) is not int or not p['lower']<=value<p['lower']+p['span']:raise ValueError('Random sample outside original interval')
        self.values[p['name']]=value;self.pending=None

    def stop(self):self.done=True;self.reason='cancelled';self.pending=None

    def step(self):
        if self.done:return {'kind':'done','record':self.pc,'reason':self.reason}
        if self.pending is not None:raise CubeDependencyMissing('Reply required for L'+str(self.pending['record']))
        a=self.actions[self.pc];k=a['kind'];e={'record':self.pc,'kind':k};next_pc=self.pc+1
        if k=='test':self.flag=self.expr(a['value'])!=0;e['result']=self.flag
        elif k=='if_zero':
            if self.flag is None:raise CubeDependencyMissing('Original condition not set')
            if not self.flag:next_pc=a['target']
        elif k=='jump':next_pc=a['target']
        elif k=='read_global':self.temporary=self.read_global(a['key'],self.pc);e.update(key=a['key'],value=self.temporary)
        elif k=='write_global':self.global_writes.append((a['key'],self.temporary));e.update(key=a['key'],value=self.temporary)
        elif k=='assign':self.values[a['name']]=self.expr(a['value']);e.update(name=a['name'],value=self.values[a['name']])
        elif k=='assign_slot':self.slots[a['slot']]=self.expr(a['value']);e.update(slot=a['slot'],value=self.slots[a['slot']])
        elif k=='assign_temporary':self.temporary=self.expr(a['value']);e['value']=self.temporary
        elif k=='random_int':
            e.update(name=a['name'],lower=self.expr(a['lower']),span=a['span']);self.pending=copy.deepcopy(e)
        elif k in ('find_color','find_pic'):
            e.update(rect=a['rect'],spec=self.expr(a['spec']),similarity=a['similarity'],direction=a['direction'])
            if k=='find_pic':e['delta']=self.expr(a['delta'])
            self.pending=copy.deepcopy(e)
        elif k in ('delay','key_press','mouse_click','move_to','trace','exit_script','os_exit_intent'):
            e['arguments']=[self.expr(n) for n in a['arguments']]
            if k=='exit_script':self.done=True;self.reason='script_stop';next_pc=self.pc
            if k=='os_exit_intent' and 'SYS' not in self.loaded:raise CubeDependencyMissing('SYS intent service not declared')
        elif k=='load_service_intent':self.loaded.add(a['name']);e['name']=a['name']
        elif k=='randomize':pass # No manufactured clock/PRNG stream.
        elif k=='frame_restore_intent':self.frame_restore_requested=True
        elif k=='return':self.done=True;self.reason='routine_return'
        else:raise ValueError('Unreviewed cube action '+k)
        self.pc=next_pc
        return e
