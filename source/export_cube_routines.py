"""Closed, non-executing translation of three preserved module07 routines.

No original source is evaluated. Unknown syntax fails rather than becoming a nop.
The output is a reviewable event plan, not proof of native/runtime equivalence.
"""
import hashlib,json,re
from pathlib import Path
from export_fishing_routines import arguments
from qmacro_gathering_walk import Expression

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/07.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
RANGES=((857,1493,'接周任務'),(5020,6442,'換角色'),(6740,6814,'完成後的操作'))
FRAME='F2730835_2229_445E_97C7_l3F7612771DA'
ARRAY='F2730835_2229_445E_97C7_l3F761277lDA'
TEMP='F2730835_2229_445E_97C7_l3F76l2771DA'
SLOT=re.compile(re.escape(FRAME+'.'+ARRAY)+r'\((\d+)\)')
ROOT_SLOT=re.compile(re.escape(ARRAY)+r'\((\d+)\)')
FRAME_FIELD=re.compile(re.escape(FRAME)+r'\.(V[A-F0-9]+|[ABCD]1?|[HXYN])(?![A-Za-z_0-9])')
FRAME_RETURN='F273O835_2229_445E_97C7_l3F76l277lDA'
SCAN_OUTPUTS=('F278O335_2229_445E_97C7_l3F76l2771DA__6','F278O335_2229_445E_97C7_l3F76l2771DA__7')
CAPTURE_CLOCK_FIELD='V87DBD9917378756D'
CAPTURE_CLOCK_SOURCE=FRAME+'.'+CAPTURE_CLOCK_FIELD+'=YEAR(NOW) & MONTH(NOW) & DAY(NOW) & HOUR(NOW) & MINUTE(NOW) & SECOND(NOW)'
PIC_LOADER='PIC\nIf IsEmpty(PIC) Then Set PIC=CreateObject("QMPlugin.Pic")'
BUILTIN_OUTPUTS=(['INTX','INTY'],['INTXX','INTYY'],['INTX12','INTY12'],['INTX16','INTY16'],['INTX122','INTY122'])


def expression(text):
    text=text.strip()
    while text.startswith('(') and text.endswith(')'):
        try:arguments(text[1:-1])
        except ValueError:break
        text=text[1:-1].strip()
    if re.fullmatch(r'"(?:[^"]|"")*"',text):return {'const':text[1:-1].replace('""','"')}
    # Split only ampersands outside string literals. Retain numeric VBS And/Or.
    parts=re.split(r'\s+&\s+(?=(?:[^"]*"[^"]*")*[^"]*$)',text)
    if len(parts)>1:return {'concat':[expression(x) for x in parts]}
    slot=SLOT.fullmatch(text)
    if slot:return {'slot':int(slot[1])}
    root_slot=ROOT_SLOT.fullmatch(text)
    if root_slot:return {'root_slot':int(root_slot[1])}
    field=FRAME_FIELD.fullmatch(text)
    if field:return {'frame_field':field[1]}
    if text==TEMP:return {'temporary':True}
    text=SLOT.sub(lambda m:'CUBE_SLOT_'+m[1],text)
    text=ROOT_SLOT.sub(lambda m:'CUBE_ROOT_SLOT_'+m[1],text)
    text=FRAME_FIELD.sub(lambda m:'BATTLE_FIELD_'+m[1],text)
    if re.search(r'\bRND\b',text,re.I):raise ValueError('Random expression requires an explicit observation')
    return {'numeric':Expression(text).parse()}


def translate(program,ranges=RANGES,external_targets=()):
    code=program['code'];strings=program['strings'];actions=[]
    for first,last,name in ranges:
        for at in range(first,last+1):
            if at in program['missing_records']:raise ValueError(('Missing body record',at))
            op,location,arg,flags=code[at]
            source=strings[arg] if op in (2,4,27,28,30,31,38) else None
            a=dict(record=at,opcode=op,location=location,operand=arg,field_3=flags,source_sl=arg if source is not None else None,source=source)
            if op in (5,6,16):a.update(kind='if_zero' if op==6 else 'jump',target=arg if op==5 else at+arg)
            elif op==12:a.update(kind='call',target=arg)
            elif op==23:a['kind']='iteration_end'
            elif op==24:a.update(kind='worker_start',target=at+arg)
            elif op==38:
                if source!='Form1.InputBox2.Text':raise ValueError(('Unreviewed UI property',at,source))
                a.update(kind='ui_write',path=source)
            elif op==13:a['kind']='return'
            elif op in (27,28):a.update(kind='read_global' if op==27 else 'write_global',key=source)
            elif op==4:a.update(kind='test',value=expression(source))
            elif op==31:
                loaders=(PIC_LOADER,'SYS\nIf IsEmpty(SYS) Then Set SYS=CreateObject("QMPlugin.Sys")')
                if source.replace('\r\n','\n') not in loaders:raise ValueError((at,source))
                a.update(kind='load_service_intent',name=source[:3])
            elif op in (2,30):
                call=re.fullmatch(r'Call (QMLibrary|DM|SYS)\.([A-Za-z0-9_]+)\((.*)\)',source,re.I)
                query=re.fullmatch(r'(?:(V[A-F0-9_]+)=)?DM_RET=DM\.(FINDCOLOR|FINDPIC)\((.*)\)',source)
                capture=re.fullmatch(r'DM_RET=DM\.CAPTURE\((.*)\)',source)
                builtin=re.fullmatch(r'Call (FindPic|FindColorEx)\((.*)\)',source)
                open_log=re.fullmatch(r'Call QMLibrary\.OpenLog\(("[^"]+\.log")\)',source)
                screenshot=re.fullmatch(r'Call PIC\.PRINTSCREEN\((.*)\)',source)
                if builtin:
                    args=arguments(builtin[2])
                    is_picture=builtin[1]=='FindPic'
                    if is_picture and tuple(args[-2:])==SCAN_OUTPUTS and len(args)==8:
                        if args[:4]!=[FRAME+'.'+field for field in 'ABCD'] or not all(FRAME_FIELD.fullmatch(x) for x in args[4:6]):
                            raise ValueError(('Unreviewed dynamic builtin rectangle',at,args))
                        a.update(kind='builtin_picture',rect_expressions=[expression(x) for x in args[:4]],
                                 spec=expression(args[4]),similarity_expression=expression(args[5]),
                                 out_names=[x.upper() for x in args[-2:]])
                    elif len(args)!=(8 if is_picture else 9) or args[-2:] not in BUILTIN_OUTPUTS:
                        raise ValueError(('Unreviewed builtin outputs',at,args))
                    else:
                        a.update(kind='builtin_picture' if is_picture else 'builtin_color',
                                 rect=[int(x) for x in args[:4]],spec=expression(args[4]),
                                 similarity=float(args[-3]),out_names=args[-2:])
                        if not is_picture:a['direction']=int(args[5])
                elif open_log:
                    a.update(kind='open_log_intent',arguments=[expression(open_log[1])])
                elif screenshot:
                    args=arguments(screenshot[1])
                    if len(args)!=5 or not all(FRAME_FIELD.fullmatch(x) for x in args[:4]):
                        raise ValueError(('Unreviewed screenshot arguments',at,args))
                    a.update(kind='screenshot_intent',arguments=[expression(x) for x in args])
                elif source==CAPTURE_CLOCK_SOURCE:
                    a.update(kind='capture_clock',field=CAPTURE_CLOCK_FIELD)
                elif call:
                    lib,method=call[1].upper(),call[2].lower();args=arguments(call[3])
                    kinds={('QMLIBRARY','delay'):'delay',('QMLIBRARY','mouseclick'):'mouse_click',('QMLIBRARY','keypress'):'key_press',('QMLIBRARY','keydown'):'key_down',('QMLIBRARY','keyup'):'key_up',('QMLIBRARY','traceprint'):'trace',('QMLIBRARY','exitscript'):'exit_script',('QMLIBRARY','threadcontrol'):'thread_control_intent',('DM','setshowerrormsg'):'dm_error_policy_intent',('DM','moveto'):'move_to',('SYS','exitos'):'os_exit_intent'}
                    arities={'delay':1,'mouse_click':3,'key_press':3,'key_down':3,'key_up':3,'trace':1,'exit_script':1,'move_to':2,'os_exit_intent':1,'thread_control_intent':2,'dm_error_policy_intent':1}
                    if (lib,method)==('QMLIBRARY','mousemove'):
                        kinds[lib,method]='mouse_move'
                        arities['mouse_move']=4
                    a.update(kind=kinds[lib,method],arguments=[expression(x) for x in args])
                    if len(args)!=arities[a['kind']]:raise ValueError((at,args))
                    if a['kind']=='exit_script' and args not in (['0'],['1']):raise ValueError('Unreviewed restart')
                elif query:
                    args=arguments(query[3]);kind='find_pic' if query[2]=='FINDPIC' else 'find_color'
                    if len(args)!=(10 if kind=='find_pic' else 9) or args[-2:] not in (['INTX','INTY'],['INTXX','INTYY']):raise ValueError((at,args))
                    if all(re.fullmatch(r'-?\d+',x) for x in args[:4]):a.update(kind=kind,rect=[int(x) for x in args[:4]])
                    elif args[:4]==['X1','Y1','X2','Y2']:a.update(kind=kind,rect_expressions=[expression(x) for x in args[:4]])
                    else:raise ValueError(('Unreviewed query rectangle',at,args[:4]))
                    a.update(spec=expression(args[4]),similarity=float(args[-4]),direction=int(args[-3]))
                    if kind=='find_pic':a['delta']=expression(args[5])
                    if query[1]:a['return_comparison']=query[1]
                    if args[-2:]!=['INTX','INTY']:a['out_names']=args[-2:]
                elif capture:
                    args=arguments(capture[1])
                    if len(args)!=5 or not all(re.fullmatch(r'\d+',x) for x in args[:4]) or not re.fullmatch(r'"C:\\[Uu]sers\\mymacro\\[QWERASDF]\.bmp"',args[4]):
                        raise ValueError(('Unreviewed capture intent',at,source))
                    a.update(kind='capture_intent',rect=[int(x) for x in args[:4]],path=expression(args[4]))
                elif source=='Randomize':a['kind']='randomize'
                elif source=='SET DM=CREATEOBJECT("dm.dmsoft")':a['kind']='create_dm_intent'
                elif re.fullmatch(r'V[A-F0-9_]+=DM.ENABLEREALMOUSE\(2,10,60\)',source):
                    a.update(kind='dm_real_mouse_intent',name=source.split('=')[0],arguments=[expression(x) for x in ('2','10','60')])
                elif source.startswith('Set ') and '=New ' in source:
                    m=re.fullmatch(r'Set ([A-Za-z_0-9]+)=New ([A-Za-z_0-9]+)((?::\1\.V[A-F0-9]+=(?:\d+|"[^"]*"))*):Set \1\.([A-Za-z_0-9]+)='+re.escape(FRAME)+r':Set '+re.escape(FRAME)+r'=\1',source)
                    if not m:raise ValueError(('Unreviewed frame creation',at,source))
                    a.update(kind='frame_enter',class_name=m[2],parent_field=m[4])
                    if m[3]:
                        fields=re.findall(r'\.([A-FV0-9]+)=(\d+|"[^"]*")',m[3])
                        a['initial_fields']={name:expression(value) for name,value in fields}
                elif re.fullmatch(r'(X|Y|XX|YY|SJ|YC|GYC|YDX|YDY|XLX|XLY|XLXX|XLYY)=INT\((\d+)\*RND[+-]\d+\)',source):
                    m=re.fullmatch(r'(X|Y|XX|YY|SJ|YC|GYC|YDX|YDY|XLX|XLY|XLXX|XLYY)=INT\((\d+)\*RND([+-])(\d+)\)',source)
                    a.update(kind='random_int',name=m[1],span=int(m[2]),lower=expression(('-' if m[3]=='-' else '')+m[4]))
                elif re.fullmatch(r'(XXX|YYY)=INT\((\d+)\*RND\+(INTX|INTY)\)',source):
                    m=re.fullmatch(r'(XXX|YYY)=INT\((\d+)\*RND\+(INTX|INTY)\)',source)
                    a.update(kind='random_int',name=m[1],span=int(m[2]),lower=expression(m[3]))
                elif source.startswith(TEMP+'='+FRAME+'.F273O835_') and ':Set ' in source and source.endswith('=Nothing'):
                    # Keep this as an explicit lifecycle boundary; no guessed parent objects.
                    a['kind']='frame_restore_intent'
                else:
                    if '=' not in source:raise ValueError(('Unreviewed statement',at,source))
                    lhs,rhs=source.split('=',1);slot=SLOT.fullmatch(lhs);root_slot=ROOT_SLOT.fullmatch(lhs)
                    if slot:a.update(kind='assign_slot',slot=int(slot[1]),value=expression(rhs))
                    elif root_slot:a.update(kind='assign_root_slot',slot=int(root_slot[1]),value=expression(rhs))
                    elif lhs==TEMP:a.update(kind='assign_temporary',value=expression(rhs))
                    elif lhs==FRAME+'.'+FRAME_RETURN:a.update(kind='assign_frame_return',value=expression(rhs))
                    elif FRAME_FIELD.fullmatch(lhs):a.update(kind='assign_frame_field',field=FRAME_FIELD.fullmatch(lhs)[1],value=expression(rhs))
                    elif lhs in SCAN_OUTPUTS:a.update(kind='assign',name=lhs.upper(),value=expression(rhs))
                    elif re.fullmatch(r'(?:V[A-F0-9_]+|XXX|YYY|INTXX?|INTYY?|XX1|YY1|CLX|CLY|[XY][12]?)',lhs):a.update(kind='assign',name=lhs.upper(),value=expression(rhs))
                    else:raise ValueError((at,source))
            else:raise ValueError(('Unreviewed opcode',at,op))
            actions.append(a)
    records={a['record'] for a in actions}
    for a in actions:
        if 'target' in a and a['target'] not in records and a['target'] not in external_targets:raise ValueError(('Branch leaves preserved bodies',a))
    callers=[{'record':at,'target':arg,'location':loc,'frame_setup_record':at-1,'return_store_record':at+1}
             for at,(op,loc,arg,flags) in enumerate(code) if op==12 and arg in {x[0] for x in ranges}]
    return {'schema':1,'module':7,'name':'魔方保留子程序','routines':[{'entry':a,'last':b,'name':n} for a,b,n in ranges],
            'actions':actions,'original_record_count':len(actions),'callers':callers,'original_body_guest_verified':False,
            'frame_lifecycle_verified':False,'full_module_restored':False,'input_or_system_actions_enabled':False,
            'scope':'Preserved-body event translation; callers, missing prefix, UI and original timing remain separate.'}


def main():
    path=PROJECT/'programs/07.json';plan=translate(json.loads(path.read_text(encoding='utf-8-sig')))
    plan['source_program_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    reportpath=PROJECT/'verification/cube-original-vs-rebuild.json'
    if reportpath.exists():
        report=json.loads(reportpath.read_text('utf8'))
        action_sha=hashlib.sha256(json.dumps(plan['actions'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
        files={'verification/original-cube-routines.json':report['original_guest_sha256'],'data/cube-cases.json':report['case_spec_sha256']}
        sources=dict(report['owned_source_sha256']);sources.update(report.get('guest_fixture_source_sha256',{}))
        valid=report.get('ok') and report['source_program_sha256']==plan['source_program_sha256'] and report['source_action_sha256']==action_sha
        valid=valid and all((PROJECT/n).exists() and hashlib.sha256((PROJECT/n).read_bytes()).hexdigest()==sha for n,sha in files.items())
        valid=valid and all(Path(__file__).with_name(n).exists() and hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()==sha for n,sha in sources.items())
        if valid:
            plan['original_body_guest_verified']=True
            plan['controlled_original_body_evidence']={'cases':report['cases'],'records_covered':report['records_covered'],'external_events':report['external_events'],
                'conditional_edges':report['conditional_edges'],'frame_scope':'Explicit new frame with Nothing parent only; full lifecycle unverified.',
                'original_rng_equivalent':False,'original_timing_verified':False,'full_module_restored':False}
    (PROJECT/'data/cube-routines.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':len(plan['actions']),'callers':len(plan['callers']),'kinds':sorted({a['kind'] for a in plan['actions']})}))


if __name__=='__main__':main()
