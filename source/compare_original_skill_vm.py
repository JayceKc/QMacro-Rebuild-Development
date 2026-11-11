"""Compare working v3 action translation to preserved VBScript guest executions.
Replay measured RND buckets, not the same RNG algorithm or wall-clock scheduling.
"""
from pathlib import Path
import hashlib,importlib.machinery,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'outputs/QMacro-Rebuild'
if not PROJECT.exists():PROJECT=ROOT/'reference'
loader=importlib.machinery.SourceFileLoader('working_v3',str(PROJECT/'qmacro_rebuild.pyw'))
spec=importlib.util.spec_from_loader(loader.name,loader);app=importlib.util.module_from_spec(spec);loader.exec_module(app)
plan=app.load_plan()
native_path=ROOT/'outputs/plugin-recovery/original-skill-vm-test.json'
if not native_path.exists():native_path=ROOT/'verification/original-skill-vm-test.json'
native=json.loads(native_path.read_text(encoding='utf-8-sig'));assert native['ok'] and native['completed_cases']==64


class BucketReplay:
    def __init__(self,case):
        self.values=[]
        for cycle in case['cycles']:
            base,width=[(66,116),(270,220),(600,600 if case['entry']==959 else 400),(1300,1000)][case['speed']]
            self.values.extend([(cycle['yc']-base+.125)/width,(cycle['sj']+.125)/4])
        self.index=0
    def random(self):
        value=self.values[self.index];self.index+=1;return value


def main():
    observations=[];total=0
    for case in native['cases']:
        rng=BucketReplay(case) if case['kind']=='controller' else None
        machine=app.Machine(plan,case['entry'],case.get('speed',0),bool(case['g']),2,rng=rng)
        if case['kind']=='order':machine.state.update(SJ=case['sj'],YC=100)
        expected=[]
        for e in case['events']:
            if e['Kind']=='delay':expected.append((e['Record'],'delay',e['Value']))
            elif e['Kind']=='key_press':
                key,mode,count=e['Value'];assert mode==0 and count==1
                expected.append((e['Record'],'key',key))
        actual=[]
        for _ in range(10000):
            event=machine.step()
            if event['kind']=='delay':actual.append((event['record'],'delay',event['milliseconds']))
            elif event['kind']=='key':actual.append((event['record'],'key',event['key']))
            if machine.done or machine.cycles==4:break
        else:raise AssertionError('Unexpected control loop')
        assert actual==expected,(case['kind'],case['entry'],case.get('speed'),case['g'],
                                  next(((a,b) for a,b in zip(actual,expected) if a!=b),('lengths',len(actual),len(expected))))
        if rng is not None:assert rng.index==len(rng.values)
        total+=len(actual)
        observations.append({'kind':case['kind'],'entry':case['entry'],'speed':case.get('speed'),
                              'sj':case.get('sj'),'g':case['g'],'matched_actions':len(actual)})
    report={'ok':True,'cases':len(observations),'matched_actions':total,'observations':observations,
            'source_sha256':hashlib.sha256((PROJECT/'qmacro_rebuild.pyw').read_bytes()).hexdigest(),
            'plan_sha256':hashlib.sha256((PROJECT/'data/skill-plan.json').read_bytes()).hexdigest(),
            'guest_report_sha256':hashlib.sha256(native_path.read_bytes()).hexdigest(),
            'scope':'Exact record/key/delay event sequence after replaying observed random value buckets; logs, wall-clock timing and game response not compared.',
            'actual_game_input_sent':False,'full_program_restored':False}
    development=ROOT if (ROOT/'qmacro_potion.py').exists() else ROOT/'outputs/QMacro-Rebuild-Development'
    output=development/'verification/skill-original-vs-working-v3.json'
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('observations','scope')}))


if __name__=='__main__':main()
