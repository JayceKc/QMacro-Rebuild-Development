"""Closed translation of three intact module08 bodies, retaining raw provenance."""
import json,hashlib,re
from pathlib import Path
from export_fishing_routines import arguments
from qmacro_gathering_walk import Expression
from gathering_evidence_status import verification
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    path=PROJECT/'programs/08.json';p=json.loads(path.read_text(encoding='utf8'));s=p['strings'];code=p['code']
    roles={s[38].split('=')[0]:'repair_strategy',s[42].split('=')[0]:'vitality_finish_mode',s[51].split('=')[0]:'home_on_no_vitality',s[57].split('=')[0]:'home_on_no_durability',
           'INTX':'query_x','INTY':'query_y','XLX':'random_x','XLY':'random_y','XX':'move_x','YY':'move_y','g_iSimulateModeInVBSBlock':'simulation_mode'}
    for record,role in ((1017,'repair_silver_state'),(1278,'sdk_miss_count'),(1401,'vitality_miss_count')):
        roles[s[code[record][2]].split('=',1)[0]]=role
    def expr(t):
        # Only discard a pair enclosing the entire expression (never strip a call).
        while t.startswith('(') and t.endswith(')'):
            try:parts=arguments(t[1:-1])
            except ValueError:break
            if len(parts)!=1:break
            t=t[1:-1]
        slot=re.fullmatch(r'[A-Za-z0-9_]+\.[A-Za-z0-9_]+\((\d+)\)',t)
        if slot:return {'slot':int(slot[1])}
        if re.fullmatch(r'"(?:[^"]|"")*"',t):return {'const':t[1:-1].replace('""','"')}
        if ' & ' in t:return {'concat':[expr(x) for x in t.split(' & ')]}
        return {'numeric':Expression(t).parse()}
    actions=[];locals_=set()
    for entry,last in ((916,1275),(1277,1342),(1344,1620)):
        for at in range(entry,last+1):
            assert at not in p['missing_records'];op,loc,arg,flags=code[at];text=s[arg] if op in (2,4,27,30) else None
            a={'record':at,'opcode':op,'location':loc,'source_sl':arg if text is not None else None,'source':text}
            if op in (6,16):a.update(kind='if_zero' if op==6 else 'jump',target=at+arg)
            elif op==12:a.update(kind='call',target=arg)
            elif op==13:a['kind']='return'
            elif op==27:
                assert text in ('V8186B4D47378756D','V80B0DA86C3CC32BE83A5D23C3778756D')
                a.update(kind='read_global',global_key=text,role='sdk_marker' if text=='V8186B4D47378756D' else 'worker_id')
            elif op==4:
                assert text.startswith('Sgn(') and text.endswith(')');a.update(kind='test',condition=expr(text))
            elif op in (2,30):
                call=re.fullmatch(r'Call (QMLibrary|DM)\.([A-Za-z0-9_]+)\((.*)\)',text,re.I)
                query=re.fullmatch(r'DM_RET=DM\.(FINDCOLOR|FINDPIC)\((.*)\)',text)
                builtin=re.fullmatch(r'Call FindColorEx\((.*)\)',text)
                if call:
                    lib,method,args=call[1].upper(),call[2].lower(),arguments(call[3])
                    if lib=='QMLIBRARY' and method=='delay':a.update(kind='delay',milliseconds=int(re.fullmatch(r'\(*(\d+)\)*',args[0])[1]))
                    elif lib=='QMLIBRARY' and method in ('keypress','keydown','keyup','mouseclick'):
                        assert len(args)==3;a.update(kind={'keypress':'key_press','keydown':'key_down','keyup':'key_up','mouseclick':'mouse_click'}[method],arguments=[expr(x) for x in args])
                    elif lib=='QMLIBRARY' and method=='threadcontrol':
                        assert len(args)==2 and args[1] in ('1','2');a.update(kind='thread_control',arguments=[expr(x) for x in args])
                    elif lib=='QMLIBRARY' and method=='traceprint':a.update(kind='trace',value=expr(args[0]))
                    elif lib=='QMLIBRARY' and method=='exitscript':assert args==['0'];a.update(kind='exit_script',restart=0)
                    elif lib=='DM' and method=='moveto':a.update(kind='move_to',arguments=[expr(x) for x in args])
                    else:raise ValueError((at,text))
                elif query:
                    args=arguments(query[2]);kind='find_color' if query[1]=='FINDCOLOR' else 'find_pic'
                    assert len(args)==(9 if kind=='find_color' else 10) and args[-2:]==['INTX','INTY']
                    a.update(kind=kind,rect=[int(x) for x in args[:4]],spec=expr(args[4]),similarity=float(args[-4]),direction=int(args[-3]))
                    if kind=='find_pic':a['delta']=expr(args[5])
                elif builtin:
                    args=arguments(builtin[1]);assert len(args)==9 and args[-2:]==['INTX','INTY']
                    a.update(kind='builtin_color',rect=[int(x) for x in args[:4]],spec=expr(args[4]),direction=int(args[5]),similarity=float(args[6]),right_bottom_inclusive=True)
                elif text=='Randomize':a['kind']='randomize'
                elif '=INT(' in text and '*RND+' in text:
                    m=re.fullmatch(r'(XLX|XLY)=INT\((\d+)\*RND\+(\d+)\)',text);assert m
                    a.update(kind='random_int',role=roles[m[1]],span=int(m[2]),lower=int(m[3]));locals_.add(roles[m[1]])
                elif text.startswith('Set ') and '=New ' in text:a.update(kind='frame_enter',name='return_home')
                elif text.startswith('F2730835'):
                    slot=re.fullmatch(r'[A-Za-z0-9_]+\.[A-Za-z0-9_]+\((\d+)\)=[A-Za-z0-9_]+',text)
                    if slot:a.update(kind='store_temp',slot=int(slot[1]))
                    else:
                        assert ':Set ' in text and text.endswith('=Nothing');a['kind']='frame_restore'
                else:
                    name,expression=text.split('=',1);role=roles.get(name,name.upper());locals_.add(role)
                    a.update(kind='assign',role=role,value=expr(expression))
            else:raise ValueError((at,op,text))
            actions.append(a)
    assert len(actions)==703;records={a['record'] for a in actions}
    for a in actions:
        if 'target' in a:assert a['target'] in records,(a['record'],a['target'])
    plan={'module':8,'actions':actions,'original_record_count':703,'name_roles':{k.upper():v for k,v in roles.items()},'local_roles':sorted(locals_),
          'routines':[{'name':'tool_red','entry':916,'last':1275,'name_inferred':True},{'name':'return_home','entry':1277,'last':1342,'name_inferred':False},
                      {'name':'check_vitality','entry':1344,'last':1620,'name_inferred':True}],
          'source_program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_body_guest_verified':verification(PROJECT,'routines',actions,'gathering-cases.json',129),'full_module_restored':False}
    (PROJECT/'data/gathering-routines.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':len(actions),'kinds':sorted({a['kind'] for a in actions})}))


if __name__=='__main__':main()
