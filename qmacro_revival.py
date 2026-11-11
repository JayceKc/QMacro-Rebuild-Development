"""Readable event-driven translation of original L1551..1638. Never sends input."""
import re

class RevivalDependencyMissing(RuntimeError):pass

class RevivalMachine:
    def __init__(self,plan,read_global):
        if plan.get('entry')!=1551 or plan.get('original_record_count')!=88:raise ValueError('Unreviewed revival plan')
        if not callable(read_global):raise TypeError('Explicit shared-variable provider is required')
        self.plan=plan;self.read_global=read_global;self.actions={a['record']:a for a in plan['actions']}
        self.pc=plan['entry'];self.slot={};self.value=None;self.flag=False;self.cycles=0;self.done=False
        self.waiting=None;self.query_x=-1;self.query_y=-1;self.cursor=None;self.mouse_result=None
    def _pending(self,kind):
        if self.waiting is None or self.waiting['kind']!=kind:raise RevivalDependencyMissing('No outstanding '+kind+' request')
    def supply_mouse_configuration(self,result):
        self._pending('configure_mouse')
        if type(result) is not int:raise TypeError('Explicit integer mouse setup result required')
        self.mouse_result=result;self.waiting=None
    def supply_cursor(self,x,y):
        self._pending('read_cursor')
        if type(x) is not int or type(y) is not int:raise TypeError('Integer cursor coordinates required')
        self.cursor=(x,y);self.waiting=None
    def supply_query(self,x,y,return_value):
        if self.waiting is None or self.waiting['kind'] not in ('find_color','find_pic'):raise RevivalDependencyMissing('No outstanding picture/color request')
        if any(type(n) is not int for n in (x,y,return_value)):raise TypeError('Integer query outputs required')
        left,top,right,bottom=self.waiting['rect']
        if x>=0 and not (left<=x<right and top<=y<bottom):raise ValueError('Backend result outside requested rectangle')
        self.query_x=x;self.query_y=y;self.waiting=None
        # DM_RET is intentionally not used: original branches only test INTX.
    def step(self):
        if self.waiting is not None:raise RevivalDependencyMissing('Backend result still required for L'+str(self.waiting['record']))
        if self.done:return {'kind':'done','record':self.pc}
        a=self.actions[self.pc];kind=a['kind'];event={'kind':kind,'record':self.pc};next_pc=self.pc+1
        if kind=='global':
            value=self.read_global(a['role'])
            if a['role']=='sdk_marker' and (not isinstance(value,str) or not re.fullmatch('[0-9a-fA-F]{6}',value)):
                raise RevivalDependencyMissing('Missing verified SDK marker for '+a['original_name'])
            if a['role']!='sdk_marker' and type(value) is not int:raise RevivalDependencyMissing('Missing integer worker ID: '+a['role'])
            self.value=value;event.update(role=a['role'],value=value)
        elif kind=='store_slot':self.slot[a['slot']]=self.value
        elif kind=='test':self.flag=True if a['condition']=='always' else self.query_x>=0
        elif kind=='if_zero':
            if not self.flag:next_pc=a['target']
        elif kind=='jump':
            if a['target']<=self.pc:self.cycles+=1
            next_pc=a['target']
        elif kind=='delay':event['milliseconds']=a['milliseconds']
        elif kind=='configure_mouse':event['arguments']=list(a['arguments']);self.waiting=event
        elif kind=='set_error_display':event['value']=a['value']
        elif kind in ('find_color','find_pic'):
            event.update(rect=list(a['rect']),similarity=a['similarity'],direction=a['direction'])
            if kind=='find_pic':event.update(path=a['path'],delta=a['delta'])
            else:event['color']=self.slot[a['color_slot']]+a['suffix'] if 'color_slot' in a else a['color']
            self.waiting=dict(event,rect=tuple(event['rect']))
        elif kind=='read_cursor':self.waiting=event
        elif kind=='thread_control':event.update(worker_id=self.slot[a['id_slot']],mode=a['mode'])
        elif kind=='move_to':
            if self.cursor is None:raise RevivalDependencyMissing('Original cursor position has not been read')
            event.update(x=self.cursor[0] if a['x']=='MX' else a['x'],y=self.cursor[1] if a['y']=='MY' else a['y'])
        elif kind=='mouse_click':event.update(button=a['button'],count=a['count'])
        elif kind=='log':event['text']=a['text']+(str(self.mouse_result) if a['append_mouse_result'] else '')
        elif kind=='frame_return_value':self.value=None  # Unassigned class return field: VBScript Empty.
        elif kind=='return':self.done=True;event['kind']='done'
        elif kind!='require_vision_backend':raise ValueError('Unknown closed revival action '+kind)
        self.pc=next_pc;return event
