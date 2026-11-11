"""Bounded Runner arithmetic on supplied pixels, stopping before all OS APIs."""
from pathlib import Path
import hashlib,json,struct,sys,random
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/emulation-deps'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_FPCW
B=(ROOT/'work/qmacro-host-image-current/runner.image-pages.bin').read_bytes()
STACK,PIXELS=0x70000000,0x71000000
def machine():
    m=Uc(UC_ARCH_X86,UC_MODE_32);m.mem_map(0x400000,(len(B)+4095)&~4095);m.mem_write(0x400000,B)
    m.mem_map(STACK,0x4000);m.mem_map(PIXELS,0x4000);m.reg_write(UC_X86_REG_EBP,STACK+0x2000);m.reg_write(UC_X86_REG_ESP,STACK+0x1800);m.reg_write(UC_X86_REG_FPCW,0x37f);return m
def write(m,a,n):m.mem_write(a,struct.pack('<I',n&0xffffffff))
def read(m,a):return struct.unpack('<I',m.mem_read(a,4))[0]
def threshold(similarity,bgr):
    m=machine();bp=STACK+0x2000;m.mem_write(bp-0x38,struct.pack('<f',similarity));write(m,bp-0x4c,bgr);write(m,bp-0x28,1)
    m.reg_write(UC_X86_REG_EAX,PIXELS);reached=[]
    def stop(cpu,a,size,_):
        if a in (0x63141a,0x63143e):reached.append(a);cpu.emu_stop()
        elif a<0x400000 or a>=0x920000:raise AssertionError('Unexpected API boundary '+hex(a))
    m.hook_add(UC_HOOK_CODE,stop);m.emu_start(0x6313b4,0x400000,count=200,timeout=50000)
    assert len(reached)==1
    value=read(m,bp-0x14);converted=read(m,bp+0x20);sim32=struct.unpack('<f',struct.pack('<f',similarity))[0]
    assert value==int((1-sim32)*100),(similarity,value)
    assert converted==((bgr&255)<<16)|(bgr&0xff00)|(bgr>>16&255)
    return value,reached[0]==0x63141a,converted
def scan(pixels,target,margin,exact):
    m=machine();bp=STACK+0x2000;m.mem_write(PIXELS,b''.join(struct.pack('<I',p) for p in pixels));write(m,bp+0x20,target);write(m,bp-0x14,margin);write(m,bp-0x28,len(pixels))
    for r,v in ((UC_X86_REG_EBX,PIXELS),(UC_X86_REG_ECX,0),(UC_X86_REG_EDX,len(pixels))):m.reg_write(r,v)
    seen=[]
    def stop(cpu,a,size,_):
        if a==0x631b06:seen.append(a);cpu.emu_stop()
        elif not (0x63141a<=a<=0x631496):raise AssertionError('Unexpected scan path '+hex(a))
    m.hook_add(UC_HOOK_CODE,stop);m.emu_start(0x63141a if exact else 0x63143e,0x400000,count=2000,timeout=50000);assert seen
    return m.reg_read(UC_X86_REG_ECX)
def find_on_pixels(width,height,pixels,similarity,scan_type=0,left=10,top=20,bgr=0x808080):
    m=machine();bp=STACK+0x2000;m.mem_write(PIXELS,b''.join(struct.pack('<I',p) for p in pixels))
    for offset,value in ((8,left),(12,top),(16,left+width-1),(20,top+height-1),(28,scan_type)):
        write(m,bp+offset,value)
    write(m,bp-0x4c,bgr);write(m,bp-0x28,len(pixels));m.mem_write(bp-0x38,struct.pack('<f',similarity));m.reg_write(UC_X86_REG_EAX,PIXELS)
    m.reg_write(UC_X86_REG_ESI,left);m.reg_write(UC_X86_REG_EDI,left+width-1)
    stopped=[]
    def stop(cpu,a,size,_):
        if a==0x6319f3:stopped.append(a);cpu.emu_stop()
        elif not (0x6313b4<=a<=0x631b33 or 0x5ef710<=a<=0x5ef7f0):raise AssertionError('Unexpected CPU boundary '+hex(a))
    m.hook_add(UC_HOOK_CODE,stop);m.emu_start(0x6313b4,0x400000,count=100000,timeout=50000);assert stopped
    def signed(value):return value if value<0x80000000 else value-0x100000000
    return signed(m.reg_read(UC_X86_REG_ESI)),signed(m.reg_read(UC_X86_REG_EDI))
def main():
    cases=[];rounding=[]
    for similarity in (.1,.25,.5,.75,.9,.95,.98,.99,.995,1):
        margin,exact,target=threshold(similarity,0x808080);rounding.append({'similarity':similarity,'threshold':margin,'exact':exact})
        for channel in range(3):
            for deviation in sorted({0,max(0,margin-1),margin,margin+1}):
                for sign in (-1,1):
                    rgb=[128]*3;rgb[channel]+=sign*deviation
                    if any(v<0 or v>255 for v in rgb):continue
                    color=rgb[0]<<16|rgb[1]<<8|rgb[2];index=scan([color],target,margin,exact)
                    # Explicit independent predicate: exact RGB, otherwise strict L1.
                    expected=0 if (color==target if exact else sum(abs(v-128) for v in rgb)<margin) else 1
                    assert index==expected,(similarity,rgb,index,expected)
                    cases.append({'similarity':similarity,'rgb':rgb,'target_bgr':'808080','threshold':margin,'exact':exact,'matched':index==0})
    margin,exact,target=threshold(.9,0x40752b)
    assert target==0x2b7540
    for pixels in ([0x2b7540],[0x40752b],[0x2c7641,0x2b7540],[0,0,0x2b7540]):
        index=scan(pixels,target,margin,exact)
        expected=next((i for i,p in enumerate(pixels) if sum(abs(((p>>shift)&255)-((target>>shift)&255)) for shift in (0,8,16))<margin),len(pixels))
        assert index==expected;cases.append({'similarity':.9,'pixels_rgb':[f'{v:06x}' for v in pixels],'target_bgr':'40752b','found_index':index})
    dimensions=[]
    for left,top,right,bottom in ((5,7,5,7),(5,7,7,9),(0,0,1,1)):
        m=machine();bp=STACK+0x2000
        for off,value in ((8,left),(12,top),(16,right),(20,bottom)):write(m,bp+off,value)
        m.emu_start(0x630ea3,0x630eb7,count=15,timeout=50000);sp=m.reg_read(UC_X86_REG_ESP)
        w,h=read(m,sp+4),read(m,sp+8);assert (w,h)==(right-left+1,bottom-top+1)
        dimensions.append({'rect':[left,top,right,bottom],'width':w,'height':h})
    m=machine();m.emu_start(0x6319ee,0x6319f3,count=4);assert m.reg_read(UC_X86_REG_ESI)==0xffffffff and m.reg_read(UC_X86_REG_EDI)==0xffffffff
    m.emu_start(0x631a00,0x631a0b,count=6);assert m.reg_read(UC_X86_REG_ESI)==((-8193)&0xffffffff)
    center=[]
    from qmacro_builtin_color import scan_points,find_color_ex
    from qmacro_color import PixelImage
    for w,h in ((1,1),(1,4),(4,1),(3,3),(4,4),(3,5),(5,3),(4,3),(3,4)):
        pixels=[0x808080]*(w*h);order=[]
        for step in range(w*h+1):
            x,y=find_on_pixels(w,h,pixels,1,1)
            if step==w*h:assert (x,y)==(-1,-1)
            else:
                assert 10<=x<10+w and 20<=y<20+h;index=(y-20)*w+x-10;assert pixels[index]==0x808080
                order.append([x,y]);pixels[index]=0
        assert order==[list(p) for p in scan_points(10,20,9+w,19+h,1)]
        center.append({'width':w,'height':h,'origin':[10,20],'order':order})
    for w,h in ((1,1),(3,2)):
        for index in range(w*h):
            pixels=[0]*(w*h);pixels[index]=0x2b7540
            assert find_on_pixels(w,h,pixels,.9,0,bgr=0x40752b)==(10+index%w,20+index//w)
    replay=[];rng=random.Random(6312)
    for n in range(80):
        w=rng.randrange(1,10);h=rng.randrange(1,10);mode=n%2;sim=(1,.9,.8,.99,.98)[n%5]
        left=rng.randrange(0,100);top=rng.randrange(0,100)
        pixels=[rng.choice((0,0x2b7540,0x2c7641,0x2f7944,0x40752b)) for _ in range(w*h)]
        expected=find_on_pixels(w,h,pixels,sim,mode,left,top,0x40752b)
        rgb=bytes(v for p in pixels for v in ((p>>16)&255,(p>>8)&255,p&255))
        frame=PixelImage(w,h,rgb,(left,top))
        packed,x,y=find_color_ex(frame,left,top,left+w-1,top+h-1,'40752b',mode,sim)
        assert (x,y)==expected,(n,w,h,sim,mode,(x,y),expected)
        replay.append({'width':w,'height':h,'origin':[left,top],'scan_type':mode,'similarity':sim,
                       'pixels_rgb':[f'{p:06x}' for p in pixels],'target_bgr':'40752b','expected_xy':list(expected),'packed':packed})
    report={'ok':True,'image_sha256':hashlib.sha256(B).hexdigest(),'threshold_cases':rounding,'scan_cases':cases,'rectangle_cases':dimensions,'center_removal_cases':center,'owned_replay_cases':replay,
            'miss_packed_value':-8193,'pixel_encoding':'x*8192+y','color_order':'BGR string converted to internal RGB',
            'similarity':'Single precision then trunc(100*(1-sim)); exact path if sim32 > double0.99; otherwise strict L1 sum < threshold.',
            'rectangle':'right and bottom inclusive','supported_scan_types':[0,1],
            'original_process_started':False,'os_api_called':False,
            'limits':['Starts after string parsing and screen capture; pixels are supplied, not sampled from a live game.',
                      'Type0 row scan and type1 center-removal observations verified; other scan modes remain separate work.',
                      'Rectangle swap, string parse failures and arbitrary VARIANT conversion are not replayed.']}
    out=ROOT/'outputs/runner-vbs-library/builtin-color-contract.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'scan_cases':len(cases),'threshold_cases':len(rounding),'inclusive_rectangle_cases':len(dimensions),'center_rectangles':len(center),'owned_replay_cases':len(replay)}))
if __name__=='__main__':main()
