"""Constrain erased prefix against retained SL order and surviving line groups.

This is an alignment model, not decryption. Keep every matching path; report
only edges common to all paths as forced under the explicit compiler model.
No original script is evaluated and no erased record is overwritten.
"""
from pathlib import Path
from collections import defaultdict,Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'outputs/QMacro-Rebuild-Development';OUT=ROOT/'outputs/fishing-recovery'
TEXT={2,30};REF=TEXT|{4,37,38,31}


def role(source):
    if source.startswith('Sgn('):return 'condition'
    if re.fullmatch(r'Form1\.[A-Za-z_0-9]+\.(ListIndex|Value|Text)',source,re.I):return 'ui'
    if source.startswith('Set ') and '=New ' in source:return 'frame'
    if '\n' in source and source.split('\n')[0] in ('FILE','SYS','PIC'):return 'library'
    if source=='Randomize':return 'randomize'
    if source.startswith('Class '):return 'class'
    if source.startswith('Call '):return 'call'
    return 'statement'


def groups(code):
    result=[]
    for i,r in enumerate(code):
        if not result or code[result[-1][0]][1]!=r[1]:result.append([])
        result[-1].append(i)
    return result


def templates(programs):
    catalog={}
    for p in programs:
        for group in groups(p['code']):
            rows=[p['code'][i] for i in group]
            if any(i in p['missing_records'] for i in group):continue
            if any(r[0] not in {2,30,4,6,16,12,37,38,31} for r in rows):continue
            refs=sorted({r[2] for r in rows if r[0] in REF})
            if not refs or refs!=list(range(refs[0],refs[-1]+1)):continue
            lo=refs[0]
            ops=tuple(('text' if r[0] in TEXT else r[0],r[2]-lo if r[0] in REF else None) for r in rows)
            kinds=tuple(role(p['strings'][i]) for i in refs)
            key=(ops,kinds)
            if key not in catalog:catalog[key]={'ops':ops,'roles':kinds,'consume':len(refs),'evidence':[]}
            if len(catalog[key]['evidence'])<3:catalog[key]['evidence'].append({'module':p['module'],'records':group,'source_sl':refs})
    # A single control instruction has no source string. Its operand is unknown.
    catalog['jump']={'ops':((16,None),),'roles':(),'consume':0,'evidence':[],'inferred_control':True}
    catalog['ui-select']={'ops':((37,0),('text',1),('text',2)),'roles':('ui','statement','statement'),'consume':3,
                          'evidence':[{'model':'module10 semantic UI read, validated guest cases; prefix template still inferred'}]}
    catalog['ui-condition']={'ops':((37,0),('text',1),(4,2),(6,None)),'roles':('ui','statement','condition'),'consume':3,
                             'evidence':[{'model':'module10 semantic UI read/condition, validated guest cases; prefix template still inferred'}]}
    return list(catalog.values())


def main():
    programs=[json.loads(p.read_text(encoding='utf8')) for p in sorted((PROJECT/'programs').glob('[0-9][0-9].json'))]
    p=next(x for x in programs if x['module']==5);source=p['strings'];catalog=templates(programs)
    unknown=[g for g in groups(p['code']) if g[0]>=4 and g[-1]<=503]
    variants=defaultdict(list)
    for t in catalog:variants[len(t['ops'])].append(t)
    # Reused library initializer SL203 is separately referenced by preserved
    # L516 followed by SL409; keep it outside monotonic new-SL consumption.
    variants[2].append({'ops':((31,'reuse_sys'),('text',0)),'roles':('call',),'consume':1,
                       'evidence':[{'module':5,'records':[516,517],'source_sl':[203,409]}]})
    def choices(group,sl):
        result=[]
        for t in variants[len(group)]:
            end=sl+t['consume']
            if end>400 or tuple(role(s) for s in source[sl:end])!=t['roles']:continue
            if any(offset=='reuse_sys' for op,offset in t['ops']) and (sl<=203 or not source[sl].upper().startswith('CALL SYS.')):continue
            result.append((end,t))
        return result
    forward=[{3:1}];edges=[]
    for g in unknown:
        after=defaultdict(int);layer=[]
        for sl,count in forward[-1].items():
            for end,t in choices(g,sl):
                after[end]+=count;layer.append((sl,end,t))
        forward.append(dict(after));edges.append(layer)
    total=forward[-1].get(400,0)
    backward=[set() for _ in range(len(unknown)+1)];backward[-1]={400}
    for i in range(len(unknown)-1,-1,-1):
        backward[i]={sl for sl,end,t in edges[i] if end in backward[i+1]}
    rows=[];forced=0
    for i,g in enumerate(unknown):
        candidates=[];seen=set();layouts=set()
        for sl,end,t in edges[i]:
            if end not in backward[i+1]:continue
            instructions=[]
            for record,(op,offset) in zip(g,t['ops']):
                instructions.append({'record':record,'op':op,'source_sl':203 if offset=='reuse_sys' else sl+offset if offset is not None else None})
            layout=json.dumps(instructions,sort_keys=True)
            layouts.add(layout)
            key=(sl,end,layout)
            if key in seen:continue
            seen.add(key);candidates.append({'source_range':[sl,end],'instructions':instructions,'template_evidence':t['evidence']})
        if len(layouts)==1:forced+=len(g)
        rows.append({'records':g,'location_id':p['code'][g[0]][1],'model_forced':len(layouts)==1,'candidates':candidates})
    OUT.mkdir(exist_ok=True)
    report={'module':5,'source_sha256':hashlib.sha256((PROJECT/'programs/05.json').read_bytes()).hexdigest(),
            'missing_records_unchanged':len(p['missing_records']),'source_window':[3,400],
            'alignment_paths':str(total),'groups':rows,'model_forced_records':forced,
            'branch_operands_recovered':False,'original_code_executed':False,'full_program_restored':False,
            'assumptions':['Contiguous missing line groups preserve SL allocation order, excluding evidenced reused SYS initializer.',
                           'Compiler templates are learned from intact line groups; text2/30 selection remains a separate encoding contract.',
                           'A source-free single jump is permitted; its original opcode/operand are not thereby recovered.',
                           'Model-forced assignments are conditional on these assumptions, not recovered ciphertext.']}
    (OUT/'prefix-alignment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'groups':len(unknown),'templates':len(catalog),'paths':str(total),'forced_records':forced,
                      'last_reachable':list(forward[-1])[:10],'layers':[(i,list(x)[:4]) for i,x in enumerate(forward) if not x][:2]}))


if __name__=='__main__':main()
