"""Preserve all original records and compile reviewed, closed worker events."""
import json,hashlib,re
from pathlib import Path
from gathering_evidence_status import verification
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'programs/08.json').exists() else ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    path=PROJECT/'programs/08.json';p=json.loads(path.read_text(encoding='utf8'));actions=[]
    for record in range(890,915):
        op,loc,arg,flags=p['code'][record];assert record not in p['missing_records']
        source=p['strings'][arg] if op in (2,4,27,30) else None
        a={'record':record,'opcode':op,'location':loc,'source_sl':arg if source is not None else None,'source':source}
        if op in (6,16):a.update(kind='if_zero' if op==6 else 'jump',target=record+arg)
        elif op==13:a['kind']='return'
        elif record==891:
            assert source=='SET DM=CREATEOBJECT("dm.dmsoft")';a['kind']='load_vision_intent'
        elif record==892:
            assert source=='Call DM.SETSHOWERRORMSG(0)';a.update(kind='set_show_error',value=0)
        elif record==894:
            assert source=='Sgn(vbTrue)';a.update(kind='test',condition='true')
        elif record in (900,904):
            condition='query_x>0' if record==900 else 'query_x>=0'
            assert source==('Sgn((INTX>0))' if record==900 else 'Sgn((INTX>=0))');a.update(kind='test',condition=condition)
        elif record==897:
            assert op==27;a.update(kind='read_sdk',global_key=source)
        elif record==898:
            assert re.fullmatch(r'[A-Za-z0-9_]+\.[A-Za-z0-9_]+\(1\)=[A-Za-z0-9_]+',source);a['kind']='store_sdk'
        elif record==899:
            assert source.startswith('DM_RET=DM.FINDCOLOR(160,1,260,25,') and source.endswith(' & "-151515",0.9,0,INTX,INTY)')
            a.update(kind='find_color',arguments=[160,1,260,25,None,0.9,0])
        elif record==903:
            m=re.fullmatch(r'DM_RET=DM.FINDPIC\(938,606,983,652,"([^"]+)","151515",0.8,0,INTX,INTY\)',source);assert m
            assert m[1].split('|')==[rf'C:\users\mymacro\kuangG{i}.bmp' for i in range(1,5)]
            a.update(kind='find_pic',arguments=[938,606,983,652,m[1],'151515',0.8,0])
        elif record in (906,908,910):
            assert source=='Call QMLibrary.KeyPress("G",g_iSimulateModeInVBSBlock,1)';a['kind']='key_press'
        elif record==913:a['kind']='frame_restore'
        else:
            m=re.fullmatch(r'Call QMLibrary.Delay\(\(*(\d+)\)*\)',source or '');assert m,(record,op,source)
            a.update(kind='delay',milliseconds=int(m[1]))
        if 'target' in a:assert 890<=a['target']<=914
        actions.append(a)
    plan={'module':8,'entry':890,'last':914,'actions':actions,'source_program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'body_original_records':25,'normal_loop_records':list(range(890,913)),
          'normal_unreachable_records':[913,914],'worker_identity_inferred':True,'worker_start_original_record':None,
          'sdk_source_unknown':True,'original_body_guest_verified':verification(PROJECT,'worker',actions,'gathering-worker-cases.json',41),'full_module_restored':False}
    (PROJECT/'data/gathering-worker.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    cases=[]
    def add(label,color,picture,invert=False,stop=None,iterations=2,mode=0):
        cases.append({'id':len(cases),'label':label,'color_result':color,'picture_result':picture,'invert_return':invert,
                      'stop_before_record':stop,'iterations':iterations,'simulation_mode':mode,'sdk_markers':['112233','A0B0C0']})
    for color in (-1,160,259):
        for picture in (-1,938,982):
            for invert in (False,True):add('two-loop-query-results',color,picture,invert)
    for at in range(890,913):add('cancel-at-record',160,938,stop=at,iterations=10,mode=3)
    (PROJECT/'data/gathering-worker-cases.json').write_text(json.dumps({'cases':cases,'sdk_marker_is_synthetic_test_data':True},indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':25,'cases':len(cases),'normal_unreachable':[913,914]}))


if __name__=='__main__':main()
