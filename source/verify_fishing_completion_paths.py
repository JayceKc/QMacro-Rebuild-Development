"""Static owned CFG walk of retained repair completion selector, no script eval.

Assume stable mode, repair=2 and return-home unchecked. No queries occur here.
"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT/'outputs/QMacro-Rebuild-Development'


def main():
    path=PROJECT/'programs/05.json';p=json.loads(path.read_text(encoding='utf8'));source=p['strings'];code=p['code']
    repair=source[57].split('=',1)[0];completion=source[53].split('=',1)[0];home=source[68].split('=',1)[0]
    results=[]
    for mode in range(6):
        values={repair:2,completion:mode,home:0};pc=769;condition=None;visited=[];effects=[];end=None
        for _ in range(500):
            assert 769<=pc<=877 and pc not in p['missing_records']
            visited.append(pc);op,location,arg,flags=code[pc];text=source[arg] if op in (2,30,4,31) else None
            if op==4:
                m=re.fullmatch(r'Sgn\(([A-Za-z_0-9]+)=(\d+)\)',text);assert m,text
                condition=values[m[1]]==int(m[2]);pc+=1
            elif op==6:
                assert condition is not None;pc=pc+1 if condition else pc+arg
            elif op==16:pc+=arg
            elif op==13:end='routine_return';break
            elif op in (2,30,31):
                if text.startswith('Call QMLibrary.ExitScript('):effects.append({'record':pc,'source_sl':arg,'intent':'stop_script'});end='script_stop';break
                elif text.startswith('Call QMLibrary.KeyPress(') or text.startswith('Call QMLibrary.MouseClick(') or text.startswith('Call DM.MOVETO('):
                    effects.append({'record':pc,'source_sl':arg,'intent':'input','source':text})
                elif text.startswith('Call SYS.EXITOS('):effects.append({'record':pc,'source_sl':arg,'intent':'os_exit_request'})
                pc+=1
            else:raise AssertionError('Unexpected instruction in this bounded selector '+str((pc,op)))
        assert end
        results.append({'mode':mode,'repair_mode':2,'return_home':0,'visited_records':visited,'effect_intents':effects,'end':end,
                        'shutdown_reached':any(e['intent']=='os_exit_request' for e in effects)})
    assert results[5]['end']=='routine_return' and not results[5]['effect_intents']
    assert not any(c['shutdown_reached'] for c in results)
    report={'source_program_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'entry':769,'cases':results,
            'finding':'With a stable completion value, the repeated mode=4 test at L864 cannot reach SYS.ExitOS; mode5 returns without completion action.',
            'duplicate_condition_records':[826,864],'os_exit_record':868,
            'assumptions':['Stable completion/repair/return-home values; repair=2, return-home=0.',
                           'Only already-verified branch semantics; input/OS/COM calls recorded as intents, never executed.'],
            'original_script_executed':False,'os_calls_made':False,'game_input_sent':False,'full_module_verified':False}
    out=ROOT/'outputs/fishing-recovery';out.mkdir(exist_ok=True)
    (out/'repair-completion-paths.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'cases':len(results),'mode5_end':results[5]['end'],'shutdown_reachable_under_assumptions':False}))


if __name__=='__main__':main()
