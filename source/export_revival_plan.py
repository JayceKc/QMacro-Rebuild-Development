"""Translate the intact 88-record monitor into a closed, owned action grammar."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/10.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
TEMP='F2730835_2229_445E_97C7_l3F76l2771DA'
def main():
    path=PROJECT/'programs/10.json';p=json.loads(path.read_text(encoding='utf-8'))
    roles={p['strings'][p['code'][at][2]]:role for at,role in ((1563,'sdk_marker'),(1606,'skill_worker'),(1610,'potion_worker'))}
    actions=[]
    for at in range(1551,1639):
        assert at not in p['missing_records'];op,loc,arg,field=p['code'][at]
        source=p['strings'][arg] if op in (2,4,27,30) else None
        a={'record':at,'opcode':op,'location':loc,'source_sl':arg if source is not None else None,'source':source}
        if op in (6,16):a.update(kind='if_zero' if op==6 else 'jump',target=at+arg)
        elif op==13:a['kind']='return'
        elif op==27:a.update(kind='global',role=roles[source],original_name=source)
        elif op==4:
            assert source in ('Sgn(vbTrue)','Sgn((INTX>=0))');a.update(kind='test',condition='always' if source=='Sgn(vbTrue)' else 'found')
        elif op in (2,30):
            if source=='SET DM=CREATEOBJECT("dm.dmsoft")':a['kind']='require_vision_backend'
            elif source=='Call DM.SETSHOWERRORMSG(0)':a.update(kind='set_error_display',value=0)
            elif 'DM.ENABLEREALMOUSE(2,10,60)' in source:a.update(kind='configure_mouse',arguments=[2,10,60])
            elif source.startswith('Call QMLibrary.Delay('):
                m=re.fullmatch(r'Call QMLibrary.Delay\(\(*(\d+)\)*\)',source);assert m,(at,source);a.update(kind='delay',milliseconds=int(m[1]))
            elif source.startswith('Call QMLibrary.TracePrint('):
                texts=re.findall(r'"([^"]*)"',source);assert len(texts)==1
                a.update(kind='log',text=texts[0],append_mouse_result=' & ' in source)
            elif source.startswith('DM_RET=DM.FINDCOLOR('):
                if at in (1565,1575,1585,1595):a.update(kind='find_color',rect=[160,1,260,25],color_slot={1565:1,1575:2,1585:3,1595:4}[at],suffix='-151515',similarity=.9,direction=0)
                elif at in (1579,1599):a.update(kind='find_color',rect=[1291,162,1479,209],color='FFD200-050505',similarity=.9,direction=0)
                else:raise AssertionError((at,source))
            elif source.startswith('DM_RET=DM.FINDPIC('):
                assert at in (1569,1589)
                a.update(kind='find_pic',rect=[1495,288,1540,550],path=r'C:\users\mymacro\si.bmp',delta='000000' if at==1569 else '050505',similarity=.8,direction=0)
            elif source=='Call GetCursorPos(MX,MY)':a['kind']='read_cursor'
            elif source.startswith('Call QMLibrary.ThreadControl('):
                m=re.search(r'\((\d+)\)\), ([12])\)$',source);assert m,(at,source);a.update(kind='thread_control',id_slot=int(m[1]),mode=int(m[2]))
            elif source.startswith('Call DM.MOVETO('):
                m=re.fullmatch(r'Call DM.MOVETO\((1377|MX),(345|MY)\)',source);assert m,(at,source)
                a.update(kind='move_to',x=int(m[1]) if m[1].isdigit() else m[1],y=int(m[2]) if m[2].isdigit() else m[2])
            elif source=='Call QMLibrary.MouseClick(0,g_iSimulateModeInVBSBlock,1)':a.update(kind='mouse_click',button=0,count=1)
            elif source.startswith(TEMP+'='):a['kind']='frame_return_value'
            else:
                m=re.search(r'\.F2730835_2229_445E_97C7_l3F761277lDA\((\d+)\)='+TEMP+r'\Z',source)
                assert m,(at,source);a.update(kind='store_slot',slot=int(m[1]))
        else:raise AssertionError((at,op,source))
        actions.append(a)
    guest=ROOT/'outputs/plugin-recovery/original-revival-vm-test.json'
    if not guest.exists():guest=PROJECT/'verification/original-revival-vm-test.json'
    evidence=json.loads(guest.read_text(encoding='utf-8-sig')) if guest.exists() else {}
    verified=evidence.get('ok') is True and evidence.get('completed_cases')==18 and evidence.get('original_body_executed') is True
    plan={'module':10,'entry':1551,'loop':1560,'last':1638,'actions':actions,
          'source_program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_global_names':{v:k for k,v in roles.items()},
          'original_record_count':88,'original_missing_records':False,'original_class_entry_mapping':'inferred',
          'sdk_marker_default':None,'sdk_marker_recovered':False,
          'runtime_contract':'Events only. Mouse configuration, queries and cursor reads require supplied backend results; missing data never means found or not found.',
          'original_body_guest_replay_verified':verified,
          'original_body_guest_report_sha256':hashlib.sha256(guest.read_bytes()).hexdigest() if verified else None,
          'live_game_revival_verified':False}
    target=PROJECT/'data/revival-plan.json';target.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'records':len(actions),'entry':1551,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
