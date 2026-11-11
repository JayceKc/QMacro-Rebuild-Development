"""Normalize saved original observations into portable owned-backend test data."""
from pathlib import Path
import collections,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'outputs/plugin-recovery' if (ROOT/'outputs/plugin-recovery').exists() else ROOT/'verification/fixtures'
OUT=ROOT/'verification' if (ROOT/'verification/fixtures').exists() else ROOT/'outputs/QMacro-Rebuild-Development/verification'
def read(name):return json.loads((SOURCE/name).read_text(encoding='utf-8-sig'))
def frame(w,h,rgb,origin=(0,0)):return {'width':w,'height':h,'origin':list(origin),'rgb_hex':bytes(rgb).hex()}
def main():
    cases=[];sources={}
    def add(name,i,s,scene,rect,similarity,templates=None):
        sources[name]=hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()
        row={'source':name,'sample_index':i,'scene':scene,'rect':rect,'similarity':similarity,
             'direction':s['direction'],'expected':[s['return_value'],s['x'],s['y']]}
        if templates is None:row.update(kind='color',color=s['color'])
        else:row.update(kind='picture',delta=s['delta'],templates=templates)
        cases.append(row)
    for name in ('original-color-oracle-valid-157.json','original-color-oracle-boundaries.json'):
        d=read(name);assert d['ok']
        for i,s in enumerate(d['samples']):
            assert s['capture_valid']
            if 'pixel' in s:
                n=s['pixel']&0xffffff;rgb=((n>>16)&255,(n>>8)&255,n&255)
                origin=(s['expected_x'],s['expected_y']);scene=frame(1,1,rgb,origin)
                rect=[origin[0],origin[1],origin[0]+1,origin[1]+1]
            else:
                rgb=bytearray([17,34,51]*9)
                for dot in s['dots']:
                    off=(dot['Y']*3+dot['X'])*3;rgb[off:off+3]=bytes((145,16,10))
                for dot in s.get('white_dots',[]):
                    off=(dot['Y']*3+dot['X'])*3;rgb[off:off+3]=b'\xff\xff\xff'
                rect=s['query_rect'];scene=frame(3,3,rgb,rect[:2])
            add(name,i,s,scene,rect,s['sim'])
    name='picture-input-oracle-reset-outputs.json';d=read(name);assert d['ok'] and d['output_variants_reset']
    layouts={'cross':[(3,2),(2,3)],'red-first':[(3,2)],'white-first':[(3,2)],'right-boundary':[(4,2)],'bottom-boundary':[(2,4)]}
    for i,s in enumerate(d['samples']):
        assert s['input_validated'];rgb=bytearray([17,34,51]*64)
        for x,y in layouts[s['layout']]:rgb[(y*8+x)*3:(y*8+x)*3+3]=bytes((145,16,10))
        if s['layout'].endswith('first'):rgb[(2*8+2)*3:(2*8+2)*3+3]=b'\xff\xff\xff'
        add(name,i,s,frame(8,8,rgb),s['rect'],s['similarity'])
    name='picture-input-oracle-center.json';d=read(name);assert d['ok'];remaining={}
    for i,s in enumerate(d['samples']):
        assert s['input_validated'];w,h=s['width'],s['height'];key=(w,h)
        if key not in remaining:remaining[key]=bytearray([145,16,10]*(w*h))
        rgb=remaining[key];sample=dict(s,color='91100A-000000')
        add(name,i,sample,frame(w,h,rgb,(2,2)),[2,2,2+w,2+h],1)
        if s['return_value']==1:
            off=((s['y']-2)*w+s['x']-2)*3;rgb[off:off+3]=bytes((17,34,51))
    assert len(cases)==416
    for name in ('original-image-oracle.json','original-image-oracle-extended.json'):
        d=read(name);assert d['ok'] and d['output_variants_reset']
        for i,s in enumerate(d['samples']):
            assert s['input_validated'];scene=dict(s['scene'],origin=[0,0]);templates=[dict(t,origin=[0,0]) for t in s['templates']]
            add(name,i,s,scene,s['rect'],s['similarity'],templates)
    assert len(cases)==557
    document={'schema':1,'cases':cases,'source_sha256':sources,
        'normalization_limits':['Single-pixel desktop probes verify that pixel and its observed position; their normalization is not a reconstruction of the entire desktop.',
          'Center probes reconstruct the validated remove-found-pixel sequence.',
          '141 picture observations include 64 repeated cases; 77 distinct picture parameter sets.',
          'No new original plugin execution or game capture occurs in this generator.']}
    path=OUT/'vision-replay-cases.json';path.write_text(json.dumps(document,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'cases':len(cases),'kinds':dict(collections.Counter(c['kind'] for c in cases)),
                      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
