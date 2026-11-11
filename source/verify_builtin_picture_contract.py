"""Run only saved Runner pixel arithmetic on owned synthetic row tables.

Stop before free/capture/file APIs. Not the filename loader or original COM.
"""
from pathlib import Path
import hashlib,json,struct,sys,random
from verify_builtin_color_contract import machine,write,read,STACK,PIXELS,B,ROOT
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI


def match(fw,fh,pixels,tw,th,template,similarity=1,left=10,top=20,transparent=-1):
    assert len(pixels)==fw*fh and len(template)==tw*th
    assert fw*fh<=1024 and tw*th<=256
    m=machine();bp=STACK+0x2000
    scene=PIXELS;data=PIXELS+0x1000;rows=PIXELS+0x2000;obj=PIXELS+0x2800;meta=PIXELS+0x2900
    m.mem_write(scene,b''.join(struct.pack('<I',p) for p in pixels));m.mem_write(data,b''.join(struct.pack('<I',p) for p in template))
    for y in range(th):write(m,rows+y*4,data+y*tw*4)
    for at in (obj,bp-0x48):
        write(m,at+8,meta);write(m,at+0x34,rows);m.mem_write(at+0x14,struct.pack('<H',32))
    write(m,meta+4,tw);write(m,meta+8,th)
    for off,val in ((-0x40,meta),(-0x90,left),(-0x94,top),(-0x80,scene),(-0x78,obj),(-0x6c,transparent),(-0xa8,-1),(-0xb0,-1)):
        write(m,bp+off,val)
    m.mem_write(bp+0x1c,struct.pack('<f',similarity));m.reg_write(UC_X86_REG_ESI,left+fw-1);m.reg_write(UC_X86_REG_EDI,top+fh-1)
    stopped=[]
    def guard(cpu,a,size,_):
        if a==0x6323f5:stopped.append(a);cpu.emu_stop()
        elif not (0x631d94<=a<0x6323f5 or 0x5ef710<=a<=0x5ef7f0 or 0x67bf20<=a<=0x67c03b):
            raise AssertionError('Unexpected native boundary '+hex(a))
    m.hook_add(UC_HOOK_CODE,guard);m.emu_start(0x631d94,0x400000,count=300000,timeout=100000)
    assert stopped,'Pixel arithmetic did not terminate'
    def signed(n):return n if n<0x80000000 else n-0x100000000
    return signed(read(m,bp-0xa8)),signed(read(m,bp-0xb0))


def main():
    cases=[]
    from qmacro_builtin_picture import find_picture
    from qmacro_color import PixelImage
    def case(label,fw,fh,pixels,tw,th,template,sim=1,transparent=-1):
        xy=match(fw,fh,pixels,tw,th,template,sim,transparent=transparent)
        def frame(w,h,colors,origin=(0,0)):
            return PixelImage(w,h,bytes(v for p in colors for v in ((p>>16)&255,(p>>8)&255,p&255)),origin)
        key=None if transparent==-1 else ((transparent>>16)&255,(transparent>>8)&255,transparent&255)
        port=find_picture(frame(fw,fh,pixels,(10,20)),frame(tw,th,template),10,20,9+fw,19+fh,sim,key)
        assert port==xy,(label,fw,fh,tw,th,sim,port,xy)
        cases.append({'label':label,'frame_size':[fw,fh],'template_size':[tw,th],
                      'frame_rgb':[f'{p:06x}' for p in pixels],'template_rgb':[f'{p:06x}' for p in template],
                      'similarity':sim,'explicit_transparency':transparent,'origin':[10,20],'found_xy':list(xy)})
        return xy
    template=[0x102030,0x405060,0x708090,0xa0b0c0]
    for fw,fh in ((2,2),(3,3),(4,4)):
        for y in range(fh-1):
            for x in range(fw-1):
                pixels=[0]*(fw*fh)
                for ty in range(2):pixels[(y+ty)*fw+x:(y+ty)*fw+x+2]=template[ty*2:ty*2+2]
                case('exact-position',fw,fh,pixels,2,2,template)
    for sim in (1,.99,.9,.8,.5):
        for delta in (0,23,24,25):
            changed=template.copy();changed[0]+=delta
            pixels=[0]*16
            for y in range(2):pixels[y*4:y*4+2]=changed[y*2:y*2+2]
            case('single-pixel-l1-boundary',4,4,pixels,2,2,template,sim)
    for color in (0,0x123456):
        case('uniform-template',4,4,[0]*16,2,2,[color]*4)
    template=[0x304050+i for i in range(64)]
    for changed in range(64):
        pixels=[0]*81
        for yy in range(8):pixels[yy*9:yy*9+8]=template[yy*8:(yy+1)*8]
        pixels[(changed//8)*9+changed%8]=0
        case('single-mismatch-grid-'+str(changed),9,9,pixels,8,8,template)
    rng=random.Random(631940)
    for index in range(120):
        tw,th=rng.randrange(1,10),rng.randrange(1,10);fw,fh=tw+rng.randrange(0,5),th+rng.randrange(0,5)
        template=[rng.choice((0x102030,0x405060,0x708090,0xa0b0c0)) for _ in range(tw*th)]
        pixels=[rng.choice((0,0x102030,0xa0b0c0)) for _ in range(fw*fh)]
        if index%2==0:
            x=rng.randrange(fw-tw+1);y=rng.randrange(fh-th+1)
            for yy in range(th):pixels[(y+yy)*fw+x:(y+yy)*fw+x+tw]=template[yy*tw:(yy+1)*tw]
            for _ in range(index%11):pixels[rng.randrange(len(pixels))]=0
        case('seeded-sparse-and-boundary-'+str(index),fw,fh,pixels,tw,th,template,(1,.9,.8,.5)[index%4])
    report={'image_sha256':hashlib.sha256(B).hexdigest(),'entry_va':'0x631d94','stop_va':'0x6323f5','cases':cases,
            'observations_complete':True,'owned_pixel_port_matched':True,'full_findpic_contract_verified':False,'original_process_started':False,'os_api_called':False,
            'limits':['Only supplied converted 32-bit row tables; no filename parsing, loading, capture or cleanup.',
                      'Owned pixel port matches all cases; filename parsing, loading, conversion and live capture are not covered.',
                      'Supplied pixels have zero high byte. Alpha-bearing converted template rows are not covered.']}
    path=ROOT/'outputs/runner-vbs-library/builtin-picture-observations.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'observed_cases':len(cases),'same_size':cases[0]['found_xy'],
                      'uniform':next(c['found_xy'] for c in cases if c['label']=='uniform-template'),
                      'pixel_port_matched':True}))

if __name__=='__main__':main()
