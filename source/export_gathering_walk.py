from pathlib import Path
import json,hashlib,re,math
from qmacro_gathering_walk import Expression
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    path=PROJECT/'programs/08.json';p=json.loads(path.read_text(encoding='utf8'));actions=[]
    for record in range(689,889):
        op,loc,arg,flags=p['code'][record];assert record not in p['missing_records']
        source=p['strings'][arg] if op in (2,4,30) else None
        a={'record':record,'opcode':op,'location':loc,'source_sl':arg if source is not None else None,'source':source}
        if op in (5,6,16):a.update(kind='if_zero' if op==6 else 'jump',target=arg if op==5 else record+arg)
        elif op==13:a['kind']='return'
        elif op==4:a.update(kind='test',expr=Expression(source).parse())
        elif op in (2,30):
            if record==887:a['kind']='frame_restore'
            elif source=='Randomize':a['kind']='randomize'
            elif record in (701,704):
                m=re.fullmatch(r'([XY])=INT\(15\*RND-15\)',source);assert m;a.update(kind='random_int',name=m[1])
            elif source.startswith('Call QMLibrary.Delay('):
                m=re.fullmatch(r'Call QMLibrary.Delay\(\(*(\d+)\)*\)',source);assert m;a.update(kind='delay',milliseconds=int(m[1]))
            elif source.startswith('Call DM.MOVETO(') or source.startswith('Call QMLibrary.MouseClick('):
                body=source[source.index('(')+1:-1];args=body.split(',')
                a.update(kind='move_to' if source.startswith('Call DM.') else 'mouse_click',arguments=[Expression(x).parse() for x in args])
            else:
                name,expression=source.split('=',1);a.update(kind='assign',name=name.upper(),expr=Expression(expression).parse())
        else:raise ValueError((record,op))
        if 'target' in a:assert 689<=a['target']<=888
        actions.append(a)
    angle=p['strings'][p['code'][708][2]].split('=')[0];pi=p['strings'][81].split('=')[0]
    action_sha=hashlib.sha256(json.dumps(actions,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    evidence=PROJECT/'verification/gathering-walk-original-vs-rebuild.json';native_path=PROJECT/'verification/original-gathering-walk.json'
    check=json.loads(evidence.read_text(encoding='utf8')) if evidence.exists() else {}
    verified=check.get('ok') is True and check.get('cases')==146 and check.get('source_action_sha256')==action_sha and native_path.exists()
    if verified:verified=check.get('original_guest_sha256')==hashlib.sha256(native_path.read_bytes()).hexdigest()
    code_root=ROOT if (ROOT/'qmacro_gathering_walk.py').exists() else ROOT/'work'
    verified=verified and set(check.get('owned_source_sha256',{}))=={'qmacro_gathering_walk.py','replay_gathering_walk.py'}
    case_path=PROJECT/'data/gathering-walk-cases.json'
    verified=verified and case_path.exists() and check.get('case_spec_sha256')==hashlib.sha256(case_path.read_bytes()).hexdigest()
    for name,sha in check.get('owned_source_sha256',{}).items():verified=verified and hashlib.sha256((code_root/name).read_bytes()).hexdigest()==sha
    plan={'module':8,'entry':689,'last':888,'actions':actions,'angle_name':angle,'pi_name':pi,'source_action_sha256':action_sha,
          'source_program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_rng_equivalent':False,'original_body_guest_verified':verified,
          'guest_report_sha256':check.get('original_guest_sha256') if verified else None,'controlled_cases':146 if verified else 0,'full_module_restored':False}
    (PROJECT/'data/gathering-walk.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    cases=[]
    def add(x,y,dx=-15,dy=-15,label='ray',initial=None):
        context={'INTXX':x,'INTYY':y,'XX1':1743,'YY1':168,pi:3.1415926,'g_iSimulateModeInVBSBlock':0}
        if initial is not None:context[angle]=initial
        cases.append({'id':len(cases),'context':context,'random_x':dx,'random_y':dy,'label':label,'expected_error':x==1743 and y==168})
    for x,y in ((0,168),(1743,0),(-1,168),(1743,-1),(1743,168)):
        add(x,y,label='zero-negative-or-coincident');add(x,y,label='preserve-previous-angle',initial=271)
    # Integer minimap points on axes and either side of all sector boundaries.
    points={(1743+int(round(100*math.cos(math.radians(a)))),168-int(round(100*math.sin(math.radians(a))))) for a in (0,5,9,10,11,45,79,80,81,90,99,100,101,135,169,170,171,180,189,190,191,225,259,260,261,270,279,280,281,315,349,350,351,355)}
    for x,y in sorted(points):
        for dx,dy in ((-15,-15),(-15,-1),(-1,-15),(-1,-1)):add(x,y,dx,dy)
    output={'cases':cases,'source_program_sha256':plan['source_program_sha256'],'random_values_controlled':True,'full_module_restored':False}
    (PROJECT/'data/gathering-walk-cases.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':200,'cases':len(cases),'source_sha256':plan['source_program_sha256']}))


if __name__=='__main__':main()
