"""Preserved potion bytecode semantics with an explicit original-color backend boundary.

This module does not guess a color or send keys. Consumers must provide real color
results and an input scheduler; missing results stop execution instead of meaning low HP.
"""
import ast,operator

class MissingColorResult(RuntimeError):pass

def number(expression,state):
    def visit(n):
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float,bool)):return n.value
        if isinstance(n,ast.Name) and n.id in state:return state[n.id]
        if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='slot':return state['slot'][visit(n.slice)]
        if isinstance(n,ast.BinOp) and type(n.op) in (ast.Add,ast.Mult):return {ast.Add:operator.add,ast.Mult:operator.mul}[type(n.op)](visit(n.left),visit(n.right))
        if isinstance(n,ast.Compare) and len(n.ops)==1 and type(n.ops[0]) in (ast.Eq,ast.GtE):return {ast.Eq:operator.eq,ast.GtE:operator.ge}[type(n.ops[0])](visit(n.left),visit(n.comparators[0]))
        raise ValueError('Unsupported preserved potion expression: '+expression)
    return visit(ast.parse(expression,mode='eval').body)

class PotionMachine:
    def __init__(self,plan,use_f1=True,use_one=False):
        self.plan=plan;self.actions={a['record']:a for a in plan['actions']}
        self.pc=plan['entry'];self.flag=False;self.waiting=None;self.done=False;self.cycles=0
        self.state={'X1':0,'Y1':0,'X2':0,'Y2':0,'INTX':-1,'INTY':-1,'misses':0,'value':0,'slot':[0]*257}
        self.globals={'use_f1':int(use_f1),'use_one':int(use_one)}
    def supply_color_result(self,x,y,return_value=0):
        if self.waiting is None:raise MissingColorResult('No outstanding FindColor request')
        if not isinstance(x,int) or not isinstance(y,int):raise TypeError('FindColor outputs must be integer coordinates')
        if x>=0 and not (self.state['X1']<=x<self.state['X2'] and self.state['Y1']<=y<self.state['Y2']):
            raise ValueError('FindColor result outside requested rectangle')
        self.state.update(INTX=x,INTY=y,DM_RET=return_value);self.waiting=None
    def step(self):
        if self.waiting is not None:raise MissingColorResult('FindColor result is required; unknown capture must not trigger a potion')
        if self.done:return {'kind':'done','record':self.pc}
        a=self.actions[self.pc];at=self.pc;self.pc+=1;k=a['kind'];e={'kind':k,'record':at}
        if k=='assign':
            value=number(a['expression'],self.state);dest=a['destination']
            if dest.startswith('slot['):self.state['slot'][int(dest[5:-1])]=value
            else:self.state[dest]=value
        elif k=='test':self.flag=bool(number(a['expression'],self.state))
        elif k=='if_zero':
            if not self.flag:self.pc=a['target']
        elif k=='jump':
            if a['target']<=at:self.cycles+=1
            self.pc=a['target']
        elif k=='global':self.state['value']=self.globals[a['name']]
        elif k=='delay':e['milliseconds']=int(number(a['expression'],self.state))
        elif k=='find_color':
            self.waiting=at
            e.update(rect=[self.state[n] for n in ('X1','Y1','X2','Y2')],color=a['color'],similarity=a['similarity'],direction=a['direction'],output_names=['INTX','INTY'])
        elif k in ('key','key_down','key_up'):e['key']=a['key']
        elif k=='log':e['text']=a['text']
        elif k=='require_color_backend':e['original_constructor']='dm.dmsoft'
        elif k=='set_error_display':e['enabled']=False
        elif k=='frame_return_value':self.state['value']=0
        elif k=='return':self.done=True;e['kind']='done'
        else:raise ValueError('Unimplemented preserved action '+str(a))
        return e

class ColorBackedPotion:
    """Connect the preserved presence-only consumer to a screen/captured-image reader.

    Input actions remain events for the caller's scheduler. This class never sends keys.
    Capture errors keep the request pending and never increment the absent-color counter.
    """
    def __init__(self,plan,capture_region,use_f1=True,use_one=False):
        if not plan.get('coordinates_only_used_as_presence'):
            raise ValueError('Original coordinate-use audit is required')
        self.machine=PotionMachine(plan,use_f1,use_one)
        self.capture=capture_region;self.request=None
    def step(self):
        if self.request is not None:
            r=self.request
            image=self.capture(*r['rect'])
            ret,x,y=image.find_color(*r['rect'],r['color'],r['similarity'],r['direction'])
            self.machine.supply_color_result(x,y,ret);self.request=None
            return {'kind':'color_result','record':r['record'],'found':ret!=0,'x':x,'y':y,
                    'coordinate_priority':'native-fixture-checked FindColor scan order'}
        event=self.machine.step()
        if event['kind']=='find_color':
            if event['direction']!=0:raise ValueError('Potion adapter only audited for source direction 0')
            self.request=event
        return event
