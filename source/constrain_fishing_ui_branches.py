"""Add explicit UI If/Else hypotheses; preserve the unconstrained alignment.

Every inferred edge is labelled, and no original opcode/operand is overwritten.
"""
import hashlib,json,re
from collections import defaultdict
from pathlib import Path
from align_fishing_prefix import groups,templates,role,PROJECT,ROOT,OUT,REF,TEXT


def main():
    baseline_path=OUT/'prefix-alignment.json';baseline=json.loads(baseline_path.read_text(encoding='utf8'))
    programs=[json.loads(p.read_text(encoding='utf8')) for p in sorted((PROJECT/'programs').glob('[0-9][0-9].json'))]
    p=next(p for p in programs if p['module']==5);source=p['strings'];code=p['code']
    assert baseline['source_sha256']==hashlib.sha256((PROJECT/'programs/05.json').read_bytes()).hexdigest()
    examples=[]
    for program in programs:
        rows=program['code']
        for i,r in enumerate(rows):
            if r[0]!=6 or r[2]!=3 or i<1 or i+4>=len(rows) or rows[i-1][0]!=4:continue
            a,b,c=rows[i+1:i+4]
            if a[0] in TEXT and b[0]==16 and b[2]==2 and c[0] in TEXT and [a[1],b[1],c[1],rows[i+4][1]]==[r[1]+1,r[1]+2,r[1]+3,r[1]+5]:
                examples.append({'module':program['module'],'condition':i-1,'if_zero':i,'true':i+1,'else_jump':i+2,'false':i+3,'end':i+4})
    assert examples
    unknown=[g for g in groups(code) if 4<=g[0] and g[-1]<=503];constraints={};hypotheses=[]
    def shape(index):
        window=unknown[index:index+5]
        return len(window)==5 and all(len(g)==1 for g in window[1:4]) and [code[g[0]][1] for g in window[1:]]==[code[window[0][0]][1]+d for d in (1,2,3,5)]
    def add(index,condition_sl,true_sl,false_sl,basis):
        cond,yes,skip,no,end=unknown[index:index+5]
        for record,pair in ((yes[0],('text',true_sl)),(skip[0],(16,None)),(no[0],('text',false_sl))):
            assert record not in constraints;constraints[record]=pair
        hypotheses.append({'condition_group':cond,'condition_sl':condition_sl,'true_sl':true_sl,'false_sl':false_sl,'basis':basis,
                           'inferred_if_zero_record':cond[-1],'inferred_if_zero_target':no[0],
                           'inferred_else_jump_record':skip[0],'inferred_else_jump_target':end[0],
                           'native_operands_recovered':False})
    for index,g in enumerate(baseline['groups']):
        if not g['model_forced'] or len(g['records'])!=4 or not shape(index):continue
        candidate=g['candidates'][0];start,end=candidate['source_range']
        if end-start!=3 or [a['op'] for a in candidate['instructions']]!=[37,'text',4,6]:continue
        yes,no=source[end:end+2];a=re.fullmatch(r'([A-Za-z_0-9]+)=1',yes);b=re.fullmatch(r'([A-Za-z_0-9]+)=0',no)
        if a and b and a[1]==b[1]:add(index,start+2,end,end+1,'UI read/condition followed by same-variable 1/0 and native-shaped Else line gap; hypothesis')
    version=[]
    for index,g in enumerate(baseline['groups']):
        if len(g['records'])!=2 or not shape(index):continue
        if any([(a['op'],a['source_sl']) for a in c['instructions']]==[(4,42),(6,None)] for c in g['candidates']):version.append(index)
    if len(version)==1:add(version[0],42,43,44,'Unique matching version predicate + success/failure traces under the native-shaped Else/gap model; hypothesis')
    variants=defaultdict(list)
    for t in templates(programs):variants[len(t['ops'])].append(t)
    variants[2].append({'ops':((31,'reuse_sys'),('text',0)),'roles':('call',),'consume':1,'evidence':[{'module':5,'records':[516,517]}]})
    def choices(g,sl):
        for t in variants[len(g)]:
            end=sl+t['consume']
            if end>400 or tuple(role(x) for x in source[sl:end])!=t['roles']:continue
            if any(offset=='reuse_sys' for op,offset in t['ops']) and (sl<=203 or not source[sl].upper().startswith('CALL SYS.')):continue
            refs=[(203 if off=='reuse_sys' else sl+off if off is not None else None) for op,off in t['ops']]
            if any(at in constraints and (op,ref)!=constraints[at] for at,(op,off),ref in zip(g,t['ops'],refs)):continue
            yield end,t,refs
    forward=[{3:1}];edges=[]
    for g in unknown:
        after=defaultdict(int);layer=[]
        for sl,count in forward[-1].items():
            for end,t,refs in choices(g,sl):after[end]+=count;layer.append((sl,end,t,refs))
        forward.append(dict(after));edges.append(layer)
    total=forward[-1].get(400,0);assert total>0,'Structured model has no complete alignment; do not choose a fallback path'
    backward=[set() for _ in forward];backward[-1]={400}
    for i in range(len(unknown)-1,-1,-1):backward[i]={sl for sl,end,t,refs in edges[i] if end in backward[i+1]}
    rows=[];unique=0
    for index,g in enumerate(unknown):
        possibilities={}
        layouts=set()
        for sl,end,t,refs in edges[index]:
            if end not in backward[index+1]:continue
            steps=[{'record':at,'op':op if ref is not None or at in constraints else 'source_free_unknown','source_sl':ref} for at,(op,off),ref in zip(g,t['ops'],refs)]
            layout=json.dumps(steps,sort_keys=True)
            layouts.add(layout)
            possibilities[(sl,end,layout)]={'source_range':[sl,end],'instructions':steps}
        candidates=list(possibilities.values())
        if len(layouts)==1:unique+=len(g)
        rows.append({'records':g,'location_id':code[g[0]][1],'model_unique':len(layouts)==1,'candidates':candidates})
    report={'module':5,'source_sha256':baseline['source_sha256'],'baseline_sha256':hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
            'baseline_paths':baseline['alignment_paths'],'alignment_paths':str(total),'baseline_unique_records':baseline['model_forced_records'],
            'model_unique_records':unique,'hypotheses':hypotheses,'native_else_examples':examples,'groups':rows,
            'original_missing_records_unchanged':500,'native_branch_operands_recovered':False,'original_code_executed':False,'full_module_restored':False,
            'limits':['UI If/Else pairing and source order are hypotheses, not recovered encrypted records.',
                      'Native one-statement Else shapes support the layout, not proof these erased nodes use the same opcode.',
                      'Source-free nodes are explicitly unknown; a remaining path cannot be selected as original code without more evidence.']}
    (OUT/'prefix-structured-alignment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'hypotheses':len(hypotheses),'native_else_examples':len(examples),'paths_before':baseline['alignment_paths'],'paths_after':str(total),'unique_before':baseline['model_forced_records'],'unique_after':unique}))


if __name__=='__main__':main()
