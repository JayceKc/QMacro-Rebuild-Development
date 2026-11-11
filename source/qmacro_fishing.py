"""Owned event state machine for intact module05 repair/home bodies.

This module never evaluates source, sleeps, sends input, loads COM or shuts down.
Read-context, image observations and original random values are explicit inputs.
"""
import copy,re


class FishingDependencyMissing(RuntimeError):pass


class FishingMachine:
    external_roles=frozenset(('repair_mode','completion_mode','slow_repair','return_home','sdk_marker',
                              'saved_cursor_x','saved_cursor_y','simulation_mode'))
    def __init__(self,plan,read_context,entry=541):
        if plan.get('module')!=5 or plan.get('original_record_count')!=382 or entry not in (541,879):
            raise ValueError('Unreviewed fishing routine plan/entry')
        if not callable(read_context):raise TypeError('Explicit context provider required')
        self.actions={a['record']:a for a in copy.deepcopy(plan['actions'])}
        expected=set(range(541,878))|set(range(879,924))
        if set(self.actions)!=expected or len(plan['actions'])!=382:raise ValueError('Fishing record coverage differs')
        for a in self.actions.values():
            if 'target' in a and a['target'] not in expected:raise ValueError('Fishing branch leaves reviewed bodies')
        self.read_context=read_context;self.pc=entry;self.values={};self.frames=[{'slots':{},'value':None}]
        self.returns=[];self.last_return=None;self.flag=False;self.done=False;self.reason=None
        self._waiting=None;self.loop_backs=0;self.loaded_services=set()

    @property
    def waiting(self):return copy.deepcopy(self._waiting)

    def stop(self):
        self.done=True;self.reason='cancelled';self._waiting=None

    def _role(self,name):
        if name in self.external_roles:
            value=self.read_context(name)
            if name=='sdk_marker':
                if not isinstance(value,str) or not re.fullmatch('[0-9a-fA-F]{6}',value):
                    raise FishingDependencyMissing('Missing verified SDK marker')
            elif type(value) is not int:raise FishingDependencyMissing('Missing integer context value: '+name)
            return value
        if name not in self.values:raise FishingDependencyMissing('Value has not been supplied/assigned: '+name)
        return self.values[name]

    def _expr(self,node):
        if set(node)=={'const'}:
            value=node['const']
            if not isinstance(value,(str,int,float,bool)):raise ValueError('Unreviewed literal type')
            return value
        if set(node)=={'role'}:return self._role(node['role'])
        if set(node)=={'add'}:
            values=[self._expr(n) for n in node['add']]
            if any(type(v) is not int for v in values):raise ValueError('Only reviewed integer addition supported')
            return sum(values)
        if set(node)=={'concat'}:
            values=[self._expr(n) for n in node['concat']]
            if any(not isinstance(v,str) for v in values):raise ValueError('Only reviewed string concatenation supported')
            return ''.join(values)
        if set(node) in ({'ge'},{'gt'},{'equals'}):
            kind=next(iter(node));args=node[kind]
            if len(args)!=2:raise ValueError('Condition arity')
            a,b=[self._expr(n) for n in args]
            if type(a) is not int or type(b) is not int:raise ValueError('Only reviewed integer comparisons supported')
            return {'ge':a>=b,'gt':a>b,'equals':a==b}[kind]
        if set(node)=={'all'}:
            values=[self._expr(term) for term in node['all']]
            if any(type(value) is not bool for value in values):raise ValueError('Expected fishing predicates')
            return all(values)
        raise ValueError('Unknown closed expression')

    def _request(self,event,**private):
        self._waiting=dict(copy.deepcopy(event),**private)
        if 'rect' in self._waiting:self._waiting['rect']=tuple(self._waiting['rect'])

    def supply_query(self,x,y,return_value):
        pending=self._waiting
        if pending is None or pending['kind'] not in ('find_color','find_pic'):raise FishingDependencyMissing('No outstanding query')
        if any(type(v) is not int for v in (x,y,return_value)):raise TypeError('Explicit integer query outputs required')
        l,t,r,b=pending['rect']
        if (x,y)!=(-1,-1) and not (l<=x<r and t<=y<b):raise ValueError('Query coordinates outside requested exclusive DM ROI')
        self.values.update(query_x=x,query_y=y,query_return=return_value);self._waiting=None

    def supply_builtin_color(self, x, y):
        pending = self._waiting
        if pending is None or pending["kind"] != "builtin_color":
            raise FishingDependencyMissing("No outstanding built-in color query")
        if type(x) is not int or type(y) is not int:
            raise TypeError("Explicit integer built-in coordinates required")
        left, top, right, bottom = pending["rect"]
        if (x, y) != (-1, -1) and not (left <= x <= right and top <= y <= bottom):
            raise ValueError("Built-in coordinates outside inclusive ROI")
        self.values.update(query_x=x, query_y=y)
        self._waiting = None

    def supply_random(self,value):
        pending=self._waiting
        if pending is None or pending['kind']!='random_int':raise FishingDependencyMissing('No outstanding random request')
        if type(value) is not int or not pending['lower']<=value<pending['lower']+pending['span']:
            raise ValueError('Random result outside original INT(RND) interval')
        self.values[pending['role']]=value;self._waiting=None

    def step(self):
        if self.done:return {'kind':'done','record':self.pc,'reason':self.reason}
        if self._waiting is not None:raise FishingDependencyMissing('Reply still required for L'+str(self._waiting['record']))
        a=self.actions[self.pc];kind=a['kind'];event={'kind':kind,'record':self.pc};next_pc=self.pc+1
        if kind=='test':self.flag=bool(self._expr(a['condition']));event['result']=self.flag
        elif kind=='if_zero':
            if not self.flag:next_pc=a['target']
        elif kind=='jump':
            next_pc=a['target']
            if next_pc<=self.pc:self.loop_backs+=1
        elif kind=='assign':
            value=self._expr(a['value']);self.values[a['role']]=value;event.update(role=a['role'],value=value)
        elif kind=='delay':event['milliseconds']=a['milliseconds']
        elif kind in ('key_press','key_down','key_up','mouse_click','move_to'):
            event['arguments']=[self._expr(n) for n in a['arguments']]
        elif kind=='trace':event['text']=self._expr(a['value'])
        elif kind=='randomize':pass  # Native time/RNG source is intentionally not fabricated.
        elif kind=='random_int':
            event.update(role=a['role'],lower=a['lower'],span=a['span']);self._request(event)
        elif kind in ('find_color','find_pic'):
            event.update(rect=list(a['rect']),similarity=a['similarity'],direction=a['direction'])
            event['color' if kind=='find_color' else 'path']=self._expr(a['spec'])
            if kind=='find_pic':event['delta']=self._expr(a['delta'])
            self._request(event)
        elif kind == "builtin_color":
            event.update(rect=list(a["rect"]), color=a["color"], direction=a["direction"],
                         similarity=a["similarity"], bounds="inclusive")
            self._request(event)
        elif kind=='frame_enter':
            if not self.frames:raise ValueError('No parent frame')
            self.frames.append({'slots':{},'value':None});event['name']=a['name']
        elif kind=='call':
            if a['target'] not in (541,879) or a['target'] not in self.actions or len(self.frames)<2 or len(self.returns)>=8192:raise ValueError('Unreviewed routine call')
            self.returns.append(next_pc);next_pc=a['target'];event['target']=next_pc
        elif kind=='frame_restore':
            if not self.frames:raise ValueError('No frame to restore')
            frame=self.frames.pop();self.last_return=frame['value'];event['value']=self.last_return
        elif kind=='store_return':
            if not self.frames:raise ValueError('No caller frame for return slot')
            self.frames[-1]['slots'][a['slot']]=self.last_return;event.update(slot=a['slot'],value=self.last_return)
        elif kind=='return':
            if self.returns:next_pc=self.returns.pop();event['target']=next_pc
            else:self.done=True;self.reason='routine_return';event['value']=self.last_return
        elif kind=='exit_script':self.done=True;self.reason='script_stop';event['restart']=a['restart']
        elif kind=='load_service_intent':self.loaded_services.add(a['name']);event['name']=a['name']
        elif kind=='os_exit_intent':
            if 'SYS' not in self.loaded_services:raise FishingDependencyMissing('System intent adapter not declared')
            event['flags']=a['flags']
        else:raise ValueError('Unknown closed fishing action '+kind)
        self.pc=next_pc;return event
