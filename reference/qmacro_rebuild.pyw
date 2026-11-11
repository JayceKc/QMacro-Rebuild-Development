"""Independent Traditional Chinese skill-loop reconstruction. Python stdlib only.

No original EXE, DLL, SDK, registration or game-memory interface is loaded.
Source records are compiled into a closed, validated action vocabulary by the builder.
"""
from pathlib import Path
import argparse, ast, ctypes, json, operator, random, time
from ctypes import wintypes

ROOT=Path(__file__).resolve().parent

class Unresolved(RuntimeError): pass

def evaluate(expression, values):
    """Closed numeric grammar; never eval/exec preserved VBScript."""
    def visit(n):
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float,bool)):return n.value
        if isinstance(n,ast.Name) and n.id in values:return values[n.id]
        if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='slot':
            return values['slot'][visit(n.slice)]
        if isinstance(n,ast.BinOp) and type(n.op) in (ast.Add,ast.Mult):
            return {ast.Add:operator.add,ast.Mult:operator.mul}[type(n.op)](visit(n.left),visit(n.right))
        if isinstance(n,ast.BoolOp) and isinstance(n.op,ast.Or):return any(visit(x) for x in n.values)
        if isinstance(n,ast.Compare) and len(n.ops)==1 and type(n.ops[0]) in (ast.Eq,ast.GtE):
            return {ast.Eq:operator.eq,ast.GtE:operator.ge}[type(n.ops[0])](visit(n.left),visit(n.comparators[0]))
        raise Unresolved('未支援表達式：'+expression)
    return visit(ast.parse(expression,mode='eval').body)

class Machine:
    def __init__(self,plan,entry,speed=1,press_g=False,g_seconds=1,seed=None,rng=None):
        if speed not in range(4):raise ValueError('speed must be 0..3')
        if not 0<=g_seconds<=60:raise ValueError('G wait must be 0..60 seconds')
        self.actions={x['record']:x for x in plan['actions']}
        self.pc=entry;self.entry=entry;self.rng=rng or random.Random(seed)
        self.state={'YC':100,'SJ':0,'cycle':0,'value':0,'slot':[0]*257}
        self.globals={'speed':speed,'press_g':int(press_g),'g_seconds':g_seconds}
        self.stack=[];self.flag=False;self.done=False;self.steps=0;self.cycles=0;self.key_count=0
    def step(self):
        if self.done:return {'kind':'done','record':self.pc}
        if self.steps>=10000000:raise Unresolved('已達單次執行指令上限')
        if self.pc not in self.actions:raise Unresolved('缺少指令 L%05d'%self.pc)
        a=self.actions[self.pc];at=self.pc;self.pc+=1;self.steps+=1;k=a['kind']
        result={'kind':'step','record':at}
        if k=='test':self.flag=bool(evaluate(a['expression'],self.state))
        elif k=='if_zero':
            if not self.flag:self.pc=a['target']
        elif k=='jump':
            if a['target']<=at and not self.stack:self.cycles+=1
            self.pc=a['target']
        elif k=='call':
            self.stack.append((self.pc,self.state['slot']));self.state['slot']=[0]*257;self.pc=a['target']
        elif k=='return':
            if self.stack:self.pc,self.state['slot']=self.stack.pop()
            else:self.done=True;result['kind']='done'
        elif k=='global':self.state['value']=self.globals[a['name']]
        elif k=='assign':
            v=evaluate(a['expression'],self.state);d=a['destination']
            if d.startswith('slot['):self.state['slot'][int(d[5:-1])]=v
            else:self.state[d]=v
        elif k=='random':self.state[a['name']]=a['base']+int(self.rng.random()*a['width'])
        elif k=='delay':
            ms=int(evaluate(a['expression'],self.state))
            if not 0<=ms<=60000:raise Unresolved('無效等待時間：'+str(ms))
            result.update(kind='delay',milliseconds=ms)
        elif k=='key':self.key_count+=1;result.update(kind='key',key=a['key'])
        elif k=='log':result.update(kind='log',text=a['text'])
        elif k=='frame_return_value':self.state['value']=0
        elif k in ('randomize','frame_prepare'):pass
        else:raise Unresolved('尚未支援：'+str(a))
        return result

# Correct SendInput structure sizes on both 32-bit and 64-bit Python.
ULONG_PTR=ctypes.c_size_t
class MOUSEINPUT(ctypes.Structure):
    _fields_=[('dx',wintypes.LONG),('dy',wintypes.LONG),('mouseData',wintypes.DWORD),
              ('dwFlags',wintypes.DWORD),('time',wintypes.DWORD),('dwExtraInfo',ULONG_PTR)]
class KEYBDINPUT(ctypes.Structure):
    _fields_=[('wVk',wintypes.WORD),('wScan',wintypes.WORD),('dwFlags',wintypes.DWORD),
              ('time',wintypes.DWORD),('dwExtraInfo',ULONG_PTR)]
class HARDWAREINPUT(ctypes.Structure):
    _fields_=[('uMsg',wintypes.DWORD),('wParamL',wintypes.WORD),('wParamH',wintypes.WORD)]
class INPUTUNION(ctypes.Union):_fields_=[('mi',MOUSEINPUT),('ki',KEYBDINPUT),('hi',HARDWAREINPUT)]
class INPUT(ctypes.Structure):_anonymous_=('u',);_fields_=[('type',wintypes.DWORD),('u',INPUTUNION)]

class KeyPulse:
    """Nonblocking key hold. Only the owned key is released on stop/focus loss."""
    def __init__(self,desktop,hold_ms=80):
        self.desktop=desktop;self.hold_ms=hold_ms;self.pending=None
    def begin(self,key,record,now):
        if self.pending is not None:raise Unresolved('上一個按鍵尚未放開')
        scan=self.desktop.begin_key(key)
        self.pending={'key':key,'record':record,'scan':scan,'started':now,'due':now+self.hold_ms/1000}
        return dict(self.pending)
    def release(self,now,force=False):
        p=self.pending
        if p is None or (not force and now<p['due']):return None
        self.desktop.end_key(p['scan'])
        self.pending=None
        return dict(p,hold_actual_ms=round((now-p['started'])*1000),cancelled=force)

class Desktop:
    def __init__(self):
        self.user=ctypes.WinDLL('user32',use_last_error=True)
        self.user.GetForegroundWindow.restype=wintypes.HWND
        self.user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
        self.user.IsWindowVisible.argtypes=[wintypes.HWND]
        self.user.IsIconic.argtypes=[wintypes.HWND]
        self.user.GetAsyncKeyState.argtypes=[ctypes.c_int];self.user.GetAsyncKeyState.restype=ctypes.c_short
        self.user.SendInput.argtypes=[wintypes.UINT,ctypes.POINTER(INPUT),ctypes.c_int]
        self.user.SendInput.restype=wintypes.UINT
        self.user.MapVirtualKeyW.argtypes=[wintypes.UINT,wintypes.UINT]
        self.user.MapVirtualKeyW.restype=wintypes.UINT
        self.kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        self.kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        self.kernel.OpenProcess.restype=wintypes.HANDLE
        self.kernel.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
        self.kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    def is_admin(self):
        shell=ctypes.WinDLL('shell32')
        shell.IsUserAnAdmin.restype=wintypes.BOOL
        return bool(shell.IsUserAnAdmin())
    def observe(self):
        h=self.user.GetForegroundWindow();pid=wintypes.DWORD()
        result={'ready':False,'reason':'沒有可用的前景視窗','pid':0,'process':''}
        if not h or not self.user.IsWindowVisible(h) or self.user.IsIconic(h):return result
        self.user.GetWindowThreadProcessId(h,ctypes.byref(pid))
        result['pid']=pid.value
        process=self.kernel.OpenProcess(0x1000,False,pid.value)
        if not process:
            result.update(reason='無法查詢前景程式',windows_error=ctypes.get_last_error());return result
        try:
            n=wintypes.DWORD(32768);b=ctypes.create_unicode_buffer(n.value)
            if not self.kernel.QueryFullProcessImageNameW(process,0,b,ctypes.byref(n)):
                result.update(reason='無法取得前景程式名稱',windows_error=ctypes.get_last_error());return result
            result['process']=Path(b.value).name
            result['ready']=result['process'].casefold()=='lostark.exe'
            result['reason']='遊戲前景已確認' if result['ready'] else '前景不是 LOSTARK.exe：'+result['process']
            return result
        finally:self.kernel.CloseHandle(process)
    def ready(self):return self.observe()['ready']
    def down(self,vk):return bool(self.user.GetAsyncKeyState(vk)&0x8000)
    def send_scan(self,scan,up=False):
        event=(INPUT*1)()
        event[0].type=1;event[0].ki=KEYBDINPUT(0,scan,8|(2 if up else 0),0,0)
        ctypes.set_last_error(0)
        sent=self.user.SendInput(1,event,ctypes.sizeof(INPUT))
        if sent!=1:raise Unresolved('Windows 未接受'+('放開' if up else '按下')+'事件；SendInput=%d，錯誤=%d'%(sent,ctypes.get_last_error()))
    def begin_key(self,key):
        if key not in 'QWERASDFGZX' or len(key)!=1:raise Unresolved('未允許的技能鍵')
        if not self.ready():raise Unresolved('遊戲已離開前景，停止送出按鍵')
        scan=self.user.MapVirtualKeyW(ord(key),0)
        if not 0<scan<256:raise Unresolved('無法取得標準技能鍵的掃描碼')
        self.send_scan(scan);return scan
    def end_key(self,scan):self.send_scan(scan,up=True)
    def key(self,key):
        if not self.ready():raise Unresolved('遊戲已離開前景，停止送出按鍵')
        events=(INPUT*2)()
        events[0].type=1;events[0].ki=KEYBDINPUT(ord(key),0,0,0,0)
        events[1].type=1;events[1].ki=KEYBDINPUT(ord(key),0,2,0,0)
        sent=self.user.SendInput(2,events,ctypes.sizeof(INPUT))
        if sent!=2:
            # If only key-down succeeded, attempt release rather than leaving a held key.
            release=(INPUT*1)(events[1]);self.user.SendInput(1,release,ctypes.sizeof(INPUT))
            raise Unresolved('Windows 未完整接受按鍵；已停止。SendInput='+str(sent))

def load_plan():return json.loads((ROOT/'data/skill-plan.json').read_text(encoding='utf-8'))

def gui():
    import tkinter as tk
    from tkinter import ttk
    win=tk.Tk();win.geometry('760x540')
    plan=load_plan();desktop=Desktop();runtime={'machine':None,'due':0.0,'real':False,'last_f10':False,'last_f12':False,'armed_at':None,'countdown_display':None}
    admin=bool(getattr(desktop,'is_admin',lambda:False)())
    win.title('QMacro 繁體重建 v3（'+('管理員' if admin else '一般權限')+'）— 自動按技能')
    pulse=KeyPulse(desktop)
    root=ttk.Frame(win,padding=14);root.pack(fill='both',expand=True)
    ttk.Label(root,text='自動按技能：獨立重建版',font=('Microsoft JhengHei',16)).pack(anchor='w')
    ttk.Label(root,text='F10 開始／停止　F12 停止；切換離開遊戲會停止。').pack(anchor='w',pady=6)
    box=ttk.Frame(root);box.pack(fill='x',pady=6)
    ttk.Label(box,text='技能模式').grid(row=0,column=0,sticky='w')
    mode=ttk.Combobox(box,values=[x['name'] for x in plan['modes']],state='readonly',width=22);mode.current(1);mode.grid(row=0,column=1,padx=8)
    ttk.Label(box,text='按鍵速度').grid(row=1,column=0,sticky='w',pady=6)
    speed=ttk.Combobox(box,values=['快','中','慢','很慢'],state='readonly',width=22);speed.current(1);speed.grid(row=1,column=1,padx=8)
    press_g=tk.BooleanVar(value=False);ttk.Checkbutton(box,text='技能中途按 G',variable=press_g).grid(row=0,column=2,padx=15)
    ttk.Label(box,text='G 後等待秒數').grid(row=1,column=2)
    g_seconds=ttk.Spinbox(box,from_=0,to=60,width=7);g_seconds.set('1');g_seconds.grid(row=1,column=3)
    real=tk.BooleanVar(value=False);ttk.Checkbutton(root,text='送出實際按鍵（需保持 LOSTARK 遊戲在前景）',variable=real).pack(anchor='w',pady=8)
    status=tk.StringVar(value='已就緒；目前為模擬，不會送出按鍵。');ttk.Label(root,textvariable=status,wraplength=720).pack(anchor='w')
    log=tk.Text(root,height=13,font=('Consolas',10));log.pack(fill='both',expand=True,pady=8)
    logdir=ROOT/'logs';logdir.mkdir(exist_ok=True)
    logfile=logdir/(time.strftime('%Y%m%d-%H%M%S')+'-runtime.jsonl')
    def audit(event,**fields):
        with logfile.open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(time=time.strftime('%Y-%m-%dT%H:%M:%S'),event=event,**fields),ensure_ascii=False)+'\n')
    def say(text):
        log.insert('end',time.strftime('%H:%M:%S ')+text+'\n');log.see('end')
        if int(log.index('end-1c').split('.')[0])>300:log.delete('1.0','100.0')
    def stop(reason='已停止'):
        if runtime['machine'] is not None:audit('stop',reason=reason,record=runtime['machine'].pc)
        if runtime['armed_at'] is not None:audit('countdown_cancelled',reason=reason)
        runtime['armed_at']=None
        runtime['machine']=None
        try:
            released=pulse.release(time.monotonic(),force=True)
            if released:audit('key_up',**released,windows_input_accepted=True)
        except Exception as error:
            audit('key_release_error',error=str(error));reason+='；放開按鍵失敗：'+str(error)
        status.set(reason)
    def start(trigger='button'):
        if runtime['armed_at'] is not None:
            stop('已取消倒數');return
        if runtime['machine'] is not None:stop();return
        try:
            if pulse.pending is not None:raise Unresolved('先前按鍵尚未成功放開，請按停止後再試')
            observation=desktop.observe() if real.get() else None
            audit('start_request',trigger=trigger,real_input=bool(real.get()),foreground=observation)
            seconds=int(g_seconds.get())
            if real.get() and not observation['ready']:
                message='未啟動：'+observation['reason']
                audit('start_blocked',reason=message,foreground=observation)
                status.set(message);say(message);return
            runtime['real']=bool(real.get());runtime['machine']=Machine(plan,plan['modes'][mode.current()]['entry'],speed.current(),press_g.get(),seconds)
            runtime['due']=time.monotonic();say('開始：'+mode.get()+('／實際按鍵' if runtime['real'] else '／模擬'))
            audit('start',entry=runtime['machine'].entry,speed=speed.current(),press_g=press_g.get(),g_seconds=seconds,real_input=runtime['real'],version=3,input_elevated=admin,input_method='SendInput-scancode-80ms')
        except Exception as e:
            audit('start_error',error=str(e));stop(str(e));say(str(e))
    def arm():
        stop('準備倒數啟動');real.set(True)
        runtime['armed_at']=time.monotonic()+5
        runtime['countdown_display']=None
        audit('countdown_armed',seconds=5,real_input=True)
        say('請在 5 秒內切回遊戲；倒數結束才檢查前景並啟動。')
    buttons=ttk.Frame(root);buttons.pack(fill='x')
    ttk.Button(buttons,text='開始／停止（F10）',command=start).pack(side='left')
    ttk.Button(buttons,text='停止（F12）',command=stop).pack(side='left',padx=8)
    ttk.Button(buttons,text='倒數 5 秒啟動遊戲按鍵',command=arm).pack(side='left',padx=8)
    ttk.Label(root,text='本版已實作八個技能子程序；吃藥、復活與地牢辨識仍待重建。',wraplength=720).pack(anchor='w',pady=7)
    def tick():
        f10=desktop.down(0x79);f12=desktop.down(0x7b)
        if f12 and not runtime['last_f12']:stop('F12 已停止')
        elif f10 and not runtime['last_f10']:
            audit('hotkey',key='F10')
            if runtime['armed_at'] is not None:stop('F10 已取消倒數')
            else:start('F10')
        runtime['last_f10']=f10;runtime['last_f12']=f12
        if runtime['armed_at'] is not None:
            remaining=runtime['armed_at']-time.monotonic()
            if remaining<=0:
                runtime['armed_at']=None
                start('countdown')
            else:
                count=int(remaining)+1
                if count!=runtime['countdown_display']:
                    runtime['countdown_display']=count
                    status.set('倒數 %d 秒：請切回遊戲，F12 可取消'%count)
        m=runtime['machine']
        if m is not None:
            try:
                if runtime['real'] and not desktop.ready():stop('遊戲離開前景，已停止')
                else:
                    released=pulse.release(time.monotonic())
                    if released:
                        audit('key_up',**released,windows_input_accepted=True)
                        audit('key',record=released['record'],key=released['key'],windows_input_accepted=True,hold_actual_ms=released['hold_actual_ms'],game_response_verified=False)
                        say('按鍵 '+released['key']+'  L%05d，按住 %d ms'%(released['record'],released['hold_actual_ms']))
                if runtime['machine'] is not None and pulse.pending is None and time.monotonic()>=runtime['due']:
                    # Bound work per GUI tick; Delay never blocks the UI thread.
                    for _ in range(64):
                        event=m.step();k=event['kind'];record=event['record']
                        if k=='delay':
                            runtime['due']=time.monotonic()+event['milliseconds']/1000;break
                        if k=='key':
                            if runtime['real']:
                                pressed=pulse.begin(event['key'],record,time.monotonic())
                                audit('key_down',**pressed,windows_input_accepted=True,hold_ms=pulse.hold_ms)
                                break
                            audit('key',record=record,key=event['key'],windows_input_accepted=False,game_response_verified=False)
                            say('模擬 '+event['key']+'  L%05d'%record)
                        elif k=='log':say(event['text'])
                        elif k=='done':stop('子程序已結束');break
                    if runtime['machine'] is not None:status.set(('執行中' if runtime['real'] else '模擬中')+'  L%05d，累計按鍵 %d，循環 %d'%(m.pc,m.key_count,m.cycles))
            except Exception as e:stop('已停止：'+str(e));say(str(e))
        win.after(15,tick)
    win.protocol('WM_DELETE_WINDOW',lambda:(stop(),win.destroy()));win.after(15,tick);win.mainloop()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--trace',action='store_true');parser.add_argument('--entry',type=int,default=1054)
    parser.add_argument('--speed',type=int,default=1);parser.add_argument('--cycles',type=int,default=4);parser.add_argument('--seed',type=int,default=7)
    args=parser.parse_args()
    if args.trace:
        m=Machine(load_plan(),args.entry,args.speed,seed=args.seed)
        for _ in range(100000):
            event=m.step()
            if event['kind'] not in ('step','delay'):print(json.dumps(event,ensure_ascii=True))
            if m.done or m.cycles>=args.cycles:break
        else:raise Unresolved('追蹤超過指令上限')
        print(json.dumps({'cycles':m.cycles,'steps':m.steps,'keys':m.key_count,'actual_input_sent':False}))
    else:gui()

if __name__=='__main__':
    try:main()
    except Exception:
        import traceback
        detail=traceback.format_exc()
        errorpath=ROOT/'logs/startup-error.txt'
        try:
            errorpath.parent.mkdir(exist_ok=True);errorpath.write_text(detail,encoding='utf-8')
        except OSError:pass
        try:
            ctypes.WinDLL('user32').MessageBoxW(None,'程式未能啟動。錯誤記錄：\n'+str(errorpath)+'\n\n'+detail[-900:], 'QMacro 啟動錯誤',16)
        except Exception:pass
        raise
