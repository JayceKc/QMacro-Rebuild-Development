"""Retained module08 L507..688 plus real skip edges, joined to intact bodies.

Entry is controlled test input, not reconstruction of erased L7..506.
"""
import copy,json,hashlib,re
from pathlib import Path
from export_fishing_routines import arguments
from qmacro_gathering_walk import Expression
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    pth=PROJECT/'programs/08.json';p=json.loads(pth.read_text(encoding='utf8'));code=p['code'];s=p['strings']
    routines=json.loads((PROJECT/'data/gathering-routines.json').read_text());walk=json.loads((PROJECT/'data/gathering-walk.json').read_text())
    roles=copy.deepcopy(routines['name_roles']);roles.update({'INTXX':'target_x','INTYY':'target_y','XX1':'minimap_center_x','YY1':'minimap_center_y',
        walk['pi_name'].upper():'walk_pi',walk['angle_name'].upper():'walk_angle','X':'walk_jitter_x','Y':'walk_jitter_y','YC':'recovery_delay'})
    roles[s[code[714][2]].split('=',1)[0].upper()]='walk_radians'
    for at,role in ((510,'fallback_attempts'),(516,'walk_repeats'),(635,'mining_counter')):roles[s[code[at][2]].split('=',1)[0].upper()]=role
    mode=re.fullmatch(r'Sgn\(([A-Za-z0-9_]+)=3\)',s[code[593][2]])[1];roles[mode.upper()]='gather_mode'
    for axis in ('X','Y'):
        for n in range(1,4):roles[f'{axis}{n}{axis}']=f'history_{axis.lower()}{n}'
    def expr(t):
        while t.startswith('(') and t.endswith(')'):
            try:a=arguments(t[1:-1])
            except ValueError:break
            if len(a)!=1:break
            t=t[1:-1]
        m=re.fullmatch(r'[A-Za-z0-9_]+\((\d+)\)',t)
        if m:return {'root_slot':int(m[1])}
        if t.startswith('"') and t.endswith('"'):return {'const':t[1:-1]}
        if ' & ' in t:return {'concat':[expr(x) for x in t.split(' & ')]}
        return {'numeric':Expression(t).parse()}
    root=[]
    for at in list(range(507,689))+[889,915,1276,1343,1621,1625]:
        op,loc,arg,field=code[at];assert at not in p['missing_records'];text=s[arg] if op in (2,4,27,30) else None
        a={'record':at,'opcode':op,'location':loc,'source_sl':arg if text is not None else None,'source':text,'field_3':field}
        if op in (6,16):a.update(kind='if_zero' if op==6 else 'jump',target=at+arg)
        elif op==12:a.update(kind='call',target=arg)
        elif op==22:assert at==1625;a['kind']='program_end'
        elif op==27:assert text=='V8186B4D47378756D';a.update(kind='read_global',global_key=text,role='sdk_marker')
        elif op==4:a.update(kind='test',condition=expr(text))
        elif op in (2,30):
            call=re.fullmatch(r'Call (QMLibrary|DM)\.([A-Za-z0-9_]+)\((.*)\)',text,re.I)
            query=re.fullmatch(r'DM_RET=DM\.(FINDCOLOR|FINDPIC)\((.*)\)',text)
            slot=re.fullmatch(r'[A-Za-z0-9_]+\((\d+)\)=[A-Za-z0-9_]+',text)
            if call:
                lib,method,args=call[1].upper(),call[2].lower(),arguments(call[3])
                if lib=='QMLIBRARY' and method=='delay':
                    try:v=expr(args[0]);constant=int(re.fullmatch(r'\(*(\d+)\)*',args[0])[1]);a.update(kind='delay',milliseconds=constant)
                    except TypeError:a.update(kind='dynamic_delay',value=v)
                elif lib=='QMLIBRARY' and method in ('keypress','mouseclick'):a.update(kind='key_press' if method=='keypress' else 'mouse_click',arguments=[expr(v) for v in args])
                elif lib=='QMLIBRARY' and method=='traceprint':a.update(kind='trace',value=expr(args[0]))
                elif lib=='DM' and method in ('moveto','movetoex'):a.update(kind='move_to' if method=='moveto' else 'move_to_ex',arguments=[expr(v) for v in args])
                else:raise ValueError((at,text))
            elif query:
                args=arguments(query[2]);kind='find_color' if query[1]=='FINDCOLOR' else 'find_pic';assert args[-2:] in (['INTX','INTY'],['INTXX','INTYY'])
                a.update(kind=kind,rect=[int(x) for x in args[:4]],spec=expr(args[4]),similarity=float(args[-4]),direction=int(args[-3]),
                    out_roles=[roles[x] for x in args[-2:]])
                if kind=='find_pic':a['delta']=expr(args[5])
            elif text=='Randomize':a['kind']='randomize'
            elif at in (522,564):assert text=='YC=INT(116*RND+66)';a.update(kind='random_int',role='recovery_delay',lower=66,span=116)
            elif slot:a.update(kind='root_store_temp',slot=int(slot[1]))
            elif text.startswith('Set ') and '=New ' in text:a.update(kind='frame_enter',name={546:'walk',605:'check_vitality',613:'tool_red',672:'walk'}[at])
            else:
                name,value=text.split('=',1);assert name.upper() in roles,(at,text);a.update(kind='assign',role=roles[name.upper()],value=expr(value))
        else:raise ValueError((at,op,text))
        root.append(a)
    walk_actions=[]
    for old in walk['actions']:
        a=copy.deepcopy(old);k=a['kind']
        if k=='test':a['condition']={'numeric':a.pop('expr')}
        elif k=='assign':a.update(role=roles[a.pop('name').upper()],value={'numeric':a.pop('expr')})
        elif k=='random_int':a.update(role=roles[a.pop('name').upper()],lower=-15,span=15)
        elif k in ('move_to','mouse_click'):a['arguments']=[{'numeric':v} for v in a['arguments']]
        walk_actions.append(a)
    actions=sorted(root+walk_actions+copy.deepcopy(routines['actions']),key=lambda a:a['record'])
    assert len(actions)==1091 and len({a['record'] for a in actions})==1091
    for a in actions:
        a['field_3']=code[a['record']][3]
        if 'target' in a:assert a['target'] in {x['record'] for x in actions} or a['target'] in p['missing_records']
    required=['fallback_attempts','walk_repeats','sdk_miss_count','walk_angle']+[f'history_{a}{i}' for a in ('x','y') for i in range(1,4)]
    plan={'module':8,'root_entries':[507,540,581,593],'root_actions':root,'actions':actions,'routines_plan':routines,'name_roles':roles,
        'required_initial_values':required,'missing_records':p['missing_records'],'original_record_count':1091,'source_program_sha256':hashlib.sha256(pth.read_bytes()).hexdigest(),
        'prefix_restored':False,'root_entry_reconstructed':False,'field_3_semantics_verified':False,'full_module_restored':False,
        'source_routines_plan_sha256':hashlib.sha256((PROJECT/'data/gathering-routines.json').read_bytes()).hexdigest(),
        'source_walk_plan_sha256':hashlib.sha256((PROJECT/'data/gathering-walk.json').read_bytes()).hexdigest()}
    (PROJECT/'data/gathering-main-suffix.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'root_and_tail_records':len(root),'joined_records':len(actions),'missing_boundary_targets':sorted({a['target'] for a in actions if a.get('target') in p['missing_records']})}))


if __name__=='__main__':main()
