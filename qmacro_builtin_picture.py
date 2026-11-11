"""Owned pixel-only port of Runner 0x631d94..0x6323f5.

This intentionally preserves observed quirks: final fitting origin is excluded,
uniform corner color is transparent, five sparse stages omit some pixels.
Not the original filename loader, BMP conversion, capture or packed API adapter.
"""
import math,struct
from qmacro_builtin_color import BuiltinContractError


def find_picture(frame,template,left,top,right,bottom,similarity=1,transparent=None):
    if isinstance(similarity,bool) or not isinstance(similarity,(float,int)) or not math.isfinite(similarity) or not .1<=similarity<=1:
        raise BuiltinContractError('Unverified builtin picture similarity')
    if any(type(n) is not int for n in (left,top,right,bottom)):
        raise BuiltinContractError('Only integer rectangles verified')
    ox,oy=frame.origin
    if not ox<=left<=right<ox+frame.width or not oy<=top<=bottom<oy+frame.height:
        raise BuiltinContractError('Inclusive rectangle outside supplied capture')
    tx,ty=template.origin;w=template.width;h=template.height
    if transparent is None:
        corners=[template.pixel(tx+x,ty+y) for x,y in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))]
        if all(p==corners[0] for p in corners):transparent=tuple(corners[0])
    elif len(transparent)!=3 or any(type(v) is not int or not 0<=v<=255 for v in transparent):
        raise BuiltinContractError('Expected RGB transparency')
    single=struct.unpack('<f',struct.pack('<f',similarity))[0]
    allowance=math.trunc(w*h*(1-single))
    stages=((0,0,4,4,max(1,allowance//16)),
            (2,2,4,4,max(1,allowance//8)),
            (0,1,2,2,max(1,3*allowance//8)),
            (1,0,2,2,5*allowance//8),
            (1,1,2,2,7*allowance//8))
    # Native candidate bounds are strict < (capture size - template size).
    for y in range(top,bottom+1-h):
        for x in range(left,right+1-w):
            misses=0;rejected=False
            for sx,sy,dx,dy,limit in stages:
                for yy in range(sy,h,dy):
                    for xx in range(sx,w,dx):
                        target=tuple(template.pixel(tx+xx,ty+yy))
                        if target!=transparent:
                            pixel=frame.pixel(x+xx,y+yy)
                            if sum(abs(a-b) for a,b in zip(pixel,target))>=24:misses+=1
                        if misses>limit:rejected=True;break
                    if rejected:break
                if rejected:break
            if not rejected:return x,y
    return -1,-1
