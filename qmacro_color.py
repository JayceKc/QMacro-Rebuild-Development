"""FindColor subset reconstructed from original 7.2450 controlled guest observations.

Coordinates use a right/bottom-exclusive rectangle. Unknown color syntax, direction,
or out-of-image capture requests are errors, never a synthetic 'not found'.
"""
import heapq,math,re

class ColorContractError(ValueError):pass

def scan_points(x1,y1,x2,y2,direction):
    if direction not in range(9):raise ColorContractError('Unverified scan direction')
    if x1>=x2 or y1>=y2:return
    if direction==4:
        width=x2-x1;height=y2-y1;cx=x1+width//2;cy=y1+height//2
        seen=bytearray(width*height);seen[(cy-y1)*width+cx-x1]=1
        pending=[(0,cy,cx)]
        while pending:
            _,y,x=heapq.heappop(pending);yield x,y
            for nx,ny in ((x,y-1),(x-1,y),(x+1,y),(x,y+1)):
                if x1<=nx<x2 and y1<=ny<y2:
                    i=(ny-y1)*width+nx-x1
                    if not seen[i]:
                        seen[i]=1;heapq.heappush(pending,((nx-cx)**2+(ny-cy)**2,ny,nx))
        return
    xs=range(x1,x2) if direction in (0,1,5,7) else range(x2-1,x1-1,-1)
    ys=range(y1,y2) if direction in (0,2,5,6) else range(y2-1,y1-1,-1)
    if direction<=3:
        for y in ys:
            for x in xs:yield x,y
    else:
        for x in xs:
            for y in ys:yield x,y

def parse_color(spec,similarity):
    if not isinstance(spec,str):raise ColorContractError('Missing color expression')
    if not isinstance(similarity,(float,int)) or not math.isfinite(similarity) or not 0.1<=similarity<=1:
        raise ColorContractError('Unverified similarity range')
    margin=int(255*(1-similarity));patterns=[]
    for token in spec.split('|'):
        # Original 7.2450 color-list oracle: empty token is a default black
        # pattern, unlike empty FindPic filename tokens (which are skipped).
        token=token or '000000'
        m=re.fullmatch(r'([0-9a-fA-F]{6})(?:-([0-9a-fA-F]{6}))?',token)
        if not m:raise ColorContractError('Unverified color syntax: '+token)
        expected=tuple(int(m[1][i:i+2],16) for i in (0,2,4))
        delta=m[2] or '000000'
        tolerance=tuple(int(delta[i:i+2],16)+margin for i in (0,2,4))
        patterns.append((expected,tolerance))
    return tuple(patterns)

def matches_rgb(rgb,patterns):
    if len(rgb)!=3 or any(not isinstance(c,int) or not 0<=c<=255 for c in rgb):raise ColorContractError('Invalid RGB sample')
    return any(all(abs(c-e)<=d for c,e,d in zip(rgb,expected,tolerance)) for expected,tolerance in patterns)

class PixelImage:
    def __init__(self,width,height,rgb,origin=(0,0)):
        if width<=0 or height<=0 or len(rgb)!=width*height*3:raise ColorContractError('Invalid captured RGB frame')
        self.width=width;self.height=height;self.rgb=bytes(rgb);self.origin=origin
    def pixel(self,x,y):
        xx=x-self.origin[0];yy=y-self.origin[1]
        if not 0<=xx<self.width or not 0<=yy<self.height:raise ColorContractError('Pixel outside captured frame')
        i=(yy*self.width+xx)*3;return tuple(self.rgb[i:i+3])
    def find_color(self,x1,y1,x2,y2,spec,similarity,direction=0):
        if direction not in range(9):raise ColorContractError('Unverified scan direction')
        if x1>x2 or y1>y2:raise ColorContractError('Reversed rectangle requires original-behavior evidence')
        ox,oy=self.origin
        if not ox<=x1<=x2<=ox+self.width or not oy<=y1<=y2<=oy+self.height:
            raise ColorContractError('Requested rectangle outside captured frame')
        patterns=parse_color(spec,similarity)
        for x,y in scan_points(x1,y1,x2,y2,direction):
            if matches_rgb(self.pixel(x,y),patterns):return 1,x,y
        return 0,-1,-1
    def contains_color(self,x1,y1,x2,y2,spec,similarity):
        """Use only when the preserved consumer tests found/not-found, not a target coordinate."""
        ox,oy=self.origin
        if not ox<=x1<=x2<=ox+self.width or not oy<=y1<=y2<=oy+self.height:raise ColorContractError('Rectangle outside capture')
        return self.find_any_color(x1,y1,x2,y2,spec,similarity)[0]!=0
    def find_any_color(self,x1,y1,x2,y2,spec,similarity):
        """Return an actual matching pixel without claiming original coordinate priority."""
        ox,oy=self.origin
        if not ox<=x1<=x2<=ox+self.width or not oy<=y1<=y2<=oy+self.height:raise ColorContractError('Rectangle outside capture')
        patterns=parse_color(spec,similarity)
        for y in range(y1,y2):
            for x in range(x1,x2):
                if matches_rgb(self.pixel(x,y),patterns):return 1,x,y
        return 0,-1,-1
