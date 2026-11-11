"""Bounded row-table and 24->32-bit conversion arithmetic from saved Runner.

Allocation/file/GDI APIs are not executed. Buffers and DIB metadata are supplied.
"""
import hashlib,json,struct
from pathlib import Path
from verify_builtin_color_contract import machine,write,read,STACK,ROOT,B
from unicorn import UC_HOOK_BLOCK
from unicorn.x86_const import UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_ESP,UC_X86_REG_EBX
from qmacro_picture import load_bmp

DATA=0x72000000


def convert(raw):
    width,height=struct.unpack_from('<ii',raw,18);planes,depth,compression=struct.unpack_from('<HHI',raw,26)
    offset=struct.unpack_from('<I',raw,10)[0];stride=(width*3+3)&~3;h=abs(height)
    assert width>0 and h>0 and planes==1 and depth==24 and compression==0
    assert width*h<100000 and h<1000 and offset+stride*h<=len(raw)
    m=machine();m.mem_map(DATA,0x200000);bp=STACK+0x2000
    source,dest=DATA+0x100,DATA+0x200;srcmeta,dstmeta=DATA+0x1000,DATA+0x1100
    srcrows,dstrows=DATA+0x2000,DATA+0x4000;srcdata,dstdata=DATA+0x10000,DATA+0x100000
    m.mem_write(srcdata,raw[offset:offset+stride*h])
    stages=[]
    def guard(cpu,a,size,_):
        stop=stages[-1]
        if a in stop:cpu.emu_stop()
        elif not (0x67cb4a<=a<=0x67cba7 or 0x67ce88<=a<=0x67cfcb or 0x67bf20<=a<0x67c1c4 or 0x67c610<=a<0x67c7a4):
            raise AssertionError('Unexpected native boundary '+hex(a))
    # All allowed exits are basic-block entries (branch fallthrough targets).
    # Block hooks retain API-boundary guards without per-pixel instruction hooks.
    m.hook_add(UC_HOOK_BLOCK,guard)
    row_cases=[]
    for obj,meta,rows,data,signed,stride_,bits in ((source,srcmeta,srcrows,srcdata,height,stride,24),
                                                 (dest,dstmeta,dstrows,dstdata,h,width*4,32)):
        write(m,obj+8,meta);write(m,obj+0xc,data);write(m,obj+0x34,rows)
        m.mem_write(obj+0x14,struct.pack('<H',bits));write(m,meta+4,width);write(m,meta+8,signed)
        write(m,bp-0x34,stride_);m.reg_write(UC_X86_REG_ESI,obj);m.reg_write(UC_X86_REG_EDI,meta)
        stages.append({0x67cb77,0x67cba7});m.emu_start(0x67cb4a,0x400000,count=20000,timeout=100000)
        from unicorn.x86_const import UC_X86_REG_EIP
        assert m.reg_read(UC_X86_REG_EIP) in stages[-1],'Row table bound reached'
        actual=[read(m,rows+i*4) for i in range(h)]
        expected=[data+(h-1-i if signed>0 else i)*stride_ for i in range(h)]
        assert actual==expected
        row_cases.append({'depth':bits,'signed_height':signed,'logical_row_offsets':[p-data for p in actual]})
    m.reg_write(UC_X86_REG_ESI,dest);m.reg_write(UC_X86_REG_EDI,source);write(m,bp-0x460,source)
    stages.append({0x67cfcb});m.emu_start(0x67ce88,0x400000,count=20000000,timeout=3000000)
    from unicorn.x86_const import UC_X86_REG_EIP
    assert m.reg_read(UC_X86_REG_EIP)==0x67cfcb,'Pixel conversion bound reached'
    out=bytearray();high=[]
    for y in range(h):
        row=read(m,dstrows+y*4);pixels=bytes(m.mem_read(row,width*4))
        for x in range(width):
            b,g,r,a=pixels[x*4:x*4+4];out.extend((r,g,b));high.append(a)
    assert not any(high),'24-bit source generated nonzero high byte'
    return bytes(out),row_cases


def synthetic(width,height):
    h=abs(height);stride=(width*3+3)&~3;rgb=bytes((i*37+11)%256 for i in range(width*h*3));dib=bytearray()
    for y in range(h):
        yy=h-1-y if height>0 else y
        for x in range(width):
            r,g,b=rgb[(yy*width+x)*3:(yy*width+x)*3+3];dib.extend((b,g,r))
        dib.extend(bytes([0xad])*(stride-width*3))
    header=struct.pack('<2sIHHI',b'BM',54+len(dib),0,0,54)+struct.pack('<IiiHHIIiiII',40,width,height,1,24,0,len(dib),0,0,0,0)
    return header+dib,rgb


def capture_header(width,height):
    m=machine();bp=STACK+0x2000;count_pointer=0x71003000
    write(m,bp-0xa8,height);write(m,bp-0xac,width);write(m,bp-0x40,count_pointer);m.reg_write(UC_X86_REG_EBX,0)
    # Stop at the allocator CALL instruction; no allocation/GDI/API is run.
    m.emu_start(0x630f58,0x630fb9,count=80,timeout=100000)
    from unicorn.x86_const import UC_X86_REG_EIP
    assert m.reg_read(UC_X86_REG_EIP)==0x630fb9
    signed_h=struct.unpack('<i',m.mem_read(bp-0x90,4))[0]
    assert read(m,bp-0x98)==40 and read(m,bp-0x94)==width and signed_h==-height
    assert read(m,bp-0x8c)==0x200001 and read(m,count_pointer)==width*height
    assert read(m,m.reg_read(UC_X86_REG_ESP))==width*height*4
    return {'width':width,'height':height,'dib_signed_height':signed_h,'planes':1,'bits_per_pixel':32,'allocation_bytes':width*height*4}


def main():
    cases=[]
    for width in (1,2,3,4,5):
        for signed in (3,-3):
            raw,expected=synthetic(width,signed);actual,rows=convert(raw);assert actual==expected
            cases.append({'kind':'owned_fixture','width':width,'signed_height':signed,'bmp_hex':raw.hex(),
                          'native_rgb_sha256':hashlib.sha256(actual).hexdigest(),'native_high_byte_zero':True,'row_tables':rows})
    catalog=json.loads((ROOT/'outputs/QMacro-Rebuild-Development/data/asset-catalog.json').read_text(encoding='utf8'))
    unique={item['sha256']:item for item in catalog['images'] if item['kind']=='ordinary_bmp'}
    for index,(sha,item) in enumerate(sorted(unique.items())):
        path=ROOT/item['source'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
        actual,rows=convert(raw);owned=load_bmp(path);assert actual==owned.rgb
        cases.append({'kind':'recovered_asset','filename':item['filename'],'bundle_path':item['bundle_path'],
                      'bmp_sha256':sha,'width':owned.width,'height':owned.height,
                      'native_rgb_sha256':hashlib.sha256(actual).hexdigest(),'native_high_byte_zero':True})
        if (index+1)%50==0:print(json.dumps({'converted':index+1,'total':len(unique)}),flush=True)
    assert len(unique)==377
    capture_headers=[capture_header(w,h) for w,h in ((1,1),(5,3),(20,15),(1920,1080))]
    report={'ok':True,'image_sha256':hashlib.sha256(B).hexdigest(),'row_table_entry_va':'0x67cb4a','capture_header_cases':capture_headers,
            'conversion_entry_va':'0x67ce88','conversion_stop_va':'0x67cfcb','cases':cases,
            'owned_fixtures':10,'unique_recovered_bmp':len(unique),'original_process_started':False,'os_api_called':False,
            'limits':['Original BMP file loader, allocation, handle ownership and filename/prefix logic are outside this replay.',
                      'Only 24-bit BI_RGB DIB rows supplied; other formats, malformed headers, 32-bit alpha inputs and DMDM remain unverified.']}
    out=ROOT/'outputs/runner-vbs-library/builtin-bitmap-conversion.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ok':True,'owned_fixtures':10,'unique_recovered_bmp':len(unique)}))


if __name__=='__main__':main()
