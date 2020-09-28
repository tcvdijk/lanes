from miniipe import *
from math import sqrt

doc = Document()
doc.import_stylefile()
doc.add_layout(page=(400,300))

doc.add_layer('help')
doc.add_layer('metro')
doc.add_layer('input')

W = 16
gap = 1
k = 4

pen = 'pen'
doc.add_pen( pen, W-gap/2 )

doc.add_color('a','1 0 0')
doc.add_color('b','1 1 0')
doc.add_color('c','0 1 0')
doc.add_color('d','0 1 1')

class Vec(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __add__(self,other):
        return Vec(self.x+other.x,self.y+other.y)
    def __sub__(self,other):
        return Vec(self.x-other.x,self.y-other.y)
    def __neg__(self):
        return Vec(-self.x,-self.y)
    def __rmul__(self,other):
        return Vec(other*self.x,other*self.y)
    def left(self):
        return Vec(-self.y,self.x)
    def dot(self,other):
        return self.x*other.x + self.y*other.y
    def len(self):
        return sqrt( self.dot(self) )
    def normalized(self):
        return (1/self.len()) * self
    def tup(self):
        return (self.x,self.y)
    
def bends(xs):
    return zip(xs[0:],xs[1:],xs[2:])

def displace( p, d, late, lane ):
    d = d.normalized()
    return p + late*d + lane*d.left()

def intersect_param_lines( p, dp, q, dq ):
    # s = (h*(a-c)+d*(g-e)) / (d*f - b*h)
    # (q-p).dot(dp) / dp.len()
    s = ( dq.y*(p.x-q.x) + dq.x*(q.y-p.y) ) / (dq.x*dp.y - dp.x*dq.y)
    return p + s*dp


def route(ps,lane,stroke):
    path = Path()
    p = displace( ps[0], ps[1]-ps[0], 0, lane )
    path.move(p.tup())
    for (a,b,c) in bends(ps):
        late = 20
        in_dir = b-a
        out_dir = c-b
        p1 = displace( b, in_dir, -late, lane)
        p2 = displace( b, out_dir, late, lane)
        pivot = intersect_param_lines( p1,(in_dir).left(), p2,(out_dir).left() )
        
        doc.use( pos=pivot.tup(), layer='help' )
        doc.path( circle(pivot.tup(), (p1-pivot).len()), opacity='10%', layer='help' )

        path.line(p1.tup())
        if in_dir.left().dot(out_dir)<0:
            path.arc_cw_fromto( pivot.tup(), p1.tup(), p2.tup() )
        else:
            path.arc_ccw_fromto( pivot.tup(), p1.tup(), p2.tup() )
        path.line(p2.tup())
        
    p = displace( ps[-1], ps[-1]-ps[-2], 0, lane)
    path.line(p.tup())
    doc.path( str(path), stroke=stroke, layer='metro', pen=8 )

ps = [ Vec( 64,  64)
     , Vec( 64, 128)
     , Vec(128, 128)
     , Vec(256, 256)
     , Vec(256,  64)
     ]

doc.path( polyline( list(map(lambda p: p.tup(), ps)) ), layer='input' )
for p in ps:
    doc.use( pos=p.tup(), layer='input' ) 

route(ps,-8,'a')
route(ps,  0,'b')
route(ps, 8,'c')


doc.write('out.ipe')