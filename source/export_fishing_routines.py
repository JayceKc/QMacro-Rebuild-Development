"""Translate only the two intact module05 bodies into a closed action grammar."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/05.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def arguments(text):
    result=[];start=0;quoted=False;depth=0;i=0
    while i<len(text):
        c=text[i]
        if c=='"':
            if quoted and i+1<len(text) and text[i+1]=='"':i+=2;continue
            quoted=not quoted
        elif not quoted:
            if c=='(':depth+=1
            elif c==')':depth-=1
            elif c==',' and depth==0:result.append(text[start:i].strip());start=i+1
            if depth<0:raise ValueError('Unbalanced arguments')
        i+=1
    if quoted or depth:raise ValueError('Unbalanced arguments')
    result.append(text[start:].strip());return result


def routine_roles(p):
    source=p['strings'];code=p['code']
    roles={source[sl].split('=',1)[0]:role for sl,role in ((57,'repair_mode'),(53,'completion_mode'),(86,'slow_repair'),(68,'return_home'),(8,'sdk_marker'))}
    roles.update({source[code[645][2]].split('=',1)[0]:'silver_found','MX':'saved_cursor_x','MY':'saved_cursor_y',
                  'XLX':'random_x','XLY':'random_y','XX':'move_x','YY':'move_y','INTX':'query_x','INTY':'query_y',
                  'g_iSimulateModeInVBSBlock':'simulation_mode'})
    return roles


def translate_bodies(p,ranges,roles):
    source=p['strings'];code=p['code']
    def expression(s):
        if s in roles:return {'role':roles[s]}
        if re.fullmatch(r'-?\d+',s):return {'const':int(s)}
        if re.fullmatch(r'\d+\.\d+',s):return {'const':float(s)}
        if re.fullmatch(r'"(?:[^"]|"")*"',s):return {'const':s[1:-1].replace('""','"')}
        if ' & ' in s:return {'concat':[expression(x) for x in s.split(' & ')]}
        if '+' in s:return {'add':[expression(x) for x in s.split('+')]}
        raise ValueError('Unreviewed expression '+s)
    actions=[]
    for entry,last in ranges:
        for at in range(entry,last+1):
            assert at not in p['missing_records'];op,location,arg,field=code[at]
            text=source[arg] if op in (2,4,30,31) else None
            a={'record':at,'opcode':op,'location':location,'source_sl':arg if text is not None else None,'source':text}
            if op in (6,16):a.update(kind='if_zero' if op==6 else 'jump',target=at+arg)
            elif op==5:a.update(kind='jump',target=arg)
            elif op==12:a.update(kind='call',target=arg)
            elif op==13:a['kind']='return'
            elif op==31:
                assert arg==203;a.update(kind='load_service_intent',name='SYS')
            elif op==4:
                if text=='Sgn(vbTrue)':a.update(kind='test',condition={'const':True})
                else:
                    m=re.fullmatch(r'Sgn\(\(?([A-Za-z_0-9]+)(>=|=)(\d+)\)?\)',text);assert m,(at,text)
                    a.update(kind='test',condition={'ge' if m[2]=='>=' else 'equals':[expression(m[1]),expression(m[3])]})
            elif op in (2,30):
                call=re.fullmatch(r'Call (QMLibrary|DM|SYS)\.([A-Za-z_0-9]+)\((.*)\)',text,re.I)
                if call:
                    library,method,args=call[1].upper(),call[2].lower(),arguments(call[3])
                    if library=='QMLIBRARY' and method=='delay':
                        m=re.fullmatch(r'\(*(\d+)\)*',args[0]);assert m and len(args)==1;a.update(kind='delay',milliseconds=int(m[1]))
                    elif library=='QMLIBRARY' and method in ('keypress','keydown','keyup','mouseclick'):
                        assert len(args)==3;a.update(kind={'keypress':'key_press','keydown':'key_down','keyup':'key_up','mouseclick':'mouse_click'}[method],arguments=[expression(x) for x in args])
                    elif library=='QMLIBRARY' and method=='traceprint':assert len(args)==1;a.update(kind='trace',value=expression(args[0]))
                    elif library=='QMLIBRARY' and method=='exitscript':assert args==['0'];a.update(kind='exit_script',restart=0)
                    elif library=='DM' and method=='moveto':assert len(args)==2;a.update(kind='move_to',arguments=[expression(x) for x in args])
                    elif library=='SYS' and method=='exitos':assert args==['1'];a.update(kind='os_exit_intent',flags=1)
                    else:raise ValueError((at,text))
                elif text.startswith('DM_RET=DM.FIND'):
                    m=re.fullmatch(r'DM_RET=DM\.(FINDCOLOR|FINDPIC)\((.*)\)',text);assert m
                    args=arguments(m[2]);kind='find_color' if m[1]=='FINDCOLOR' else 'find_pic'
                    assert len(args)==(9 if kind=='find_color' else 10) and args[-2:]==['INTX','INTY']
                    a.update(kind=kind,rect=[int(x) for x in args[:4]],spec=expression(args[4]),similarity=float(args[-4]),direction=int(args[-3]))
                    if kind=='find_pic':a['delta']=expression(args[5])
                elif text=='Randomize':a['kind']='randomize'
                elif '=INT(' in text and '*RND+' in text:
                    m=re.fullmatch(r'(XLX|XLY)=INT\((\d+)\*RND\+(\d+)\)',text);assert m
                    a.update(kind='random_int',role=roles[m[1]],span=int(m[2]),lower=int(m[3]))
                elif at in (785,803):
                    assert text.startswith('Set ') and '=New ' in text;a.update(kind='frame_enter',name='return_home')
                elif at in (787,805):a.update(kind='store_return',slot=1 if at==787 else 2)
                elif at in (876,922):a['kind']='frame_restore'
                else:
                    m=re.fullmatch(r'([A-Za-z_0-9]+)=(.*)',text);assert m and m[1] in roles,(at,text)
                    a.update(kind='assign',role=roles[m[1]],value=expression(m[2]))
            else:raise ValueError((at,op,text))
            actions.append(a)
    return actions


def main():
    path=PROJECT/'programs/05.json';p=json.loads(path.read_text(encoding='utf8'))
    roles=routine_roles(p)
    actions=translate_bodies(p,((541,877),(879,923)),roles)
    assert len(actions)==382
    records={a['record'] for a in actions}
    for a in actions:
        if 'target' in a:assert a['target'] in records,(a['record'],a['target'])
    guest_path=PROJECT/'verification/original-fishing-vm-test.json';compare_path=PROJECT/'verification/fishing-original-vs-rebuild.json'
    guest=json.loads(guest_path.read_text(encoding='utf-8-sig')) if guest_path.exists() else {}
    comparison=json.loads(compare_path.read_text(encoding='utf8')) if compare_path.exists() else {}
    action_sha=hashlib.sha256(json.dumps(actions,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    verified=guest.get('ok') is True and guest.get('completed_cases')==77 and comparison.get('ok') is True and comparison.get('cases')==77
    verified=verified and guest.get('source_program_sha256')==hashlib.sha256(path.read_bytes()).hexdigest() and comparison.get('original_guest_report_sha256')==hashlib.sha256(guest_path.read_bytes()).hexdigest()
    verified=verified and comparison.get('source_action_sha256')==action_sha and guest.get('case_spec_sha256')==hashlib.sha256((PROJECT/'data/fishing-cases.json').read_bytes()).hexdigest()
    code_root=ROOT if (ROOT/'qmacro_fishing.py').exists() else ROOT/'work'
    verified=verified and set(comparison.get('owned_source_sha256',{}))=={'qmacro_fishing.py','replay_fishing_cases.py'}
    for name,sha in comparison.get('owned_source_sha256',{}).items():verified=verified and hashlib.sha256((code_root/name).read_bytes()).hexdigest()==sha
    covered={n for case in guest.get('cases',[]) for n in case['records']} if verified else set()
    plan={'module':5,'routines':[{'name':'repair','entry':541,'last':877,'name_mapping':'inferred'},{'name':'return_home','entry':879,'last':923,'name_mapping':'retained frame+call879'}],
          'source_program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_action_sha256':action_sha,'original_record_count':382,'actions':actions,
          'original_roles':{v:k for k,v in roles.items()},'original_missing_records':False,
          'original_body_guest_replay_verified':verified,'original_rng_equivalent':False,'sdk_marker_default':None,
          'original_guest_report_sha256':hashlib.sha256(guest_path.read_bytes()).hexdigest() if verified else None,
          'guest_controlled_cases':77 if verified else 0,'guest_records_covered':len(covered),
          'guest_uncovered_records':sorted(records-covered) if verified else sorted(records),
          'policy':'Owned events only; queries and random values require explicit replies. No source eval, COM, input, sleep or OS shutdown.',
          'limits':['Original class return fields stay Empty; no return assignment appears in these bodies.',
                    'Frame restoration models parent/slots, not native object notifications or cleanup.',
                    'The erased 500-record main entry and original execution timing are not restored.'],
          'full_module_restored':False}
    target=PROJECT/'data/fishing-routines.json';target.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'actions':len(actions),'kinds':sorted({a['kind'] for a in actions}),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
