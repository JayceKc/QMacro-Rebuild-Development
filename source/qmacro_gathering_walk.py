"""Owned numeric expression grammar and event port for original walk L689..888.

No eval/exec, Windows input, timing or native DLL. ATN division is preserved,
including the original coincident-target 0/0 overflow (VBScript 800a0006).
"""
import copy,math,re


class WalkDependencyMissing(RuntimeError):pass
class VbsNumericOverflow(OverflowError):pass


class Expression:
    token=re.compile(r'\s*(>=|<=|<>|[()+*/=<>-]|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z_0-9]*)')
    def __init__(self,text):
        self.tokens=[];at=0
        while at<len(text):
            m=self.token.match(text,at)
            if not m:raise ValueError('Unsupported numeric expression at '+str(at))
            self.tokens.append(m[1].upper());at=m.end()
        self.at=0
    def peek(self):return self.tokens[self.at] if self.at<len(self.tokens) else None
    def take(self):value=self.peek();self.at+=1;return value
    def chain(self,child,operators):
        node=child()
        while self.peek() in operators:node={'op':self.take(),'args':[node,child()]}
        return node
    def parse(self):
        node=self.boolean_or()
        if self.at!=len(self.tokens):raise ValueError('Trailing numeric expression tokens')
        return node
    def boolean_or(self):return self.chain(self.boolean_and,('OR',))
    def boolean_and(self):return self.chain(self.compare,('AND',))
    def compare(self):return self.chain(self.add,('=','<>','<','>','<=','>='))
    def add(self):return self.chain(self.multiply,('+','-'))
    def multiply(self):return self.chain(self.unary,('*','/'))
    def unary(self):
        if self.peek() in ('+','-'):return {'op':'UNARY'+self.take(),'args':[self.unary()]}
        return self.atom()
    def atom(self):
        token=self.take()
        if token=='(':
            node=self.boolean_or()
            if self.take()!=')':raise ValueError('Missing closing parenthesis')
            return node
        if token and re.fullmatch(r'\d+(?:\.\d+)?',token):return {'const':float(token) if '.' in token else int(token)}
        if token in ('VBTRUE','VBFALSE'):return {'const':-1 if token=='VBTRUE' else 0}
        if not token or not re.fullmatch('[A-Z_][A-Z_0-9]*',token):raise ValueError('Missing numeric atom')
        if self.peek()=='(':
            if token not in ('SGN','ATN','INT'):raise ValueError('Unsupported numeric function '+token)
            self.take();arg=self.boolean_or()
            if self.take()!=')':raise ValueError('Missing function parenthesis')
            return {'op':token,'args':[arg]}
        return {'name':token}


def number(value):
    if value is None:return 0  # VBScript Empty in numeric context.
    if isinstance(value,bool):return -1 if value else 0
    if type(value) not in (int,float) or not math.isfinite(value):raise ValueError('Expected finite numeric value')
    return value


def evaluate(node,read):
    if 'const' in node:return node['const']
    if 'name' in node:return number(read(node['name']))
    op=node['op'];args=[number(evaluate(n,read)) for n in node['args']]  # Eager, as VBS And/Or.
    if op=='SGN':return (args[0]>0)-(args[0]<0)
    if op=='ATN':return math.atan(args[0])
    if op=='INT':return math.floor(args[0])
    if op=='UNARY-':return -args[0]
    if op=='UNARY+':return args[0]
    a,b=args
    if op=='+':return a+b
    if op=='-':return a-b
    if op=='*':return a*b
    if op=='/':
        if a==0 and b==0:raise VbsNumericOverflow('VBScript 800a0006: 0/0 overflow')
        return a/b
    if op=='=':return a==b
    if op=='<>':return a!=b
    if op=='<':return a<b
    if op=='>':return a>b
    if op=='<=':return a<=b
    if op=='>=':return a>=b
    if op=='AND':return int(a)&int(b)
    if op=='OR':return int(a)|int(b)
    raise ValueError('Unreviewed numeric operator')


class GatheringWalkMachine:
    def __init__(self,plan,context):
        if plan.get('entry')!=689 or plan.get('last')!=888 or len(plan['actions'])!=200:raise ValueError('Unreviewed walk plan')
        self.actions={a['record']:a for a in copy.deepcopy(plan['actions'])}
        if set(self.actions)!=set(range(689,889)):raise ValueError('Walk record coverage differs')
        self.context={k.upper():v for k,v in context.items()};self.angle_name=plan['angle_name'].upper()
        self.values={self.angle_name:self.context.get(self.angle_name)};self.pc=689;self.flag=False;self.done=False;self.pending=None
    def read(self,name):
        if name in self.values:return self.values[name]
        if name not in self.context:raise WalkDependencyMissing('Missing original walk value '+name)
        return self.context[name]
    def supply_random(self,value):
        if self.pending is None:raise WalkDependencyMissing('No outstanding walk random request')
        if type(value) is not int or not -15<=value<0:raise ValueError('Expected original INT(15*RND-15) range')
        self.values[self.pending]=value;self.pending=None
    def step(self):
        if self.done:return {'kind':'done','record':self.pc}
        if self.pending is not None:raise WalkDependencyMissing('Walk random result not supplied')
        a=self.actions[self.pc];kind=a['kind'];e={'record':self.pc,'kind':kind};next_pc=self.pc+1
        if kind=='test':self.flag=evaluate(a['expr'],self.read)!=0
        elif kind=='if_zero':
            if not self.flag:next_pc=a['target']
        elif kind=='jump':next_pc=a['target']
        elif kind=='assign':self.values[a['name']]=evaluate(a['expr'],self.read)
        elif kind=='random_int':self.pending=a['name'];e.update(name=a['name'],lower=-15,span=15)
        elif kind=='delay':e['value']=a['milliseconds']
        elif kind in ('move_to','mouse_click'):e['value']=[evaluate(expr,self.read) for expr in a['arguments']]
        elif kind=='randomize':pass
        elif kind=='frame_restore':e['value']=None
        elif kind=='return':self.done=True
        else:raise ValueError('Unreviewed walk action')
        self.pc=next_pc;return e
