import sys,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'python_deps'))
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import wkt
S=P.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
lanes=json.loads((S/'actual_lanes.json').read_text());a=json.loads((S/'actors_final.json').read_text());st=next(x for x in a if x['name']=='BP_BogotaTransmiStation_C_4');yaw=math.radians(st['rotation'][1]);c,s=math.cos(yaw),math.sin(yaw);x,y=st['position'][:2]
sweeps=[]
for i,points in enumerate(lanes):
 if i in [4,5]:continue
 shapes=[];hl=915 if i==6 else 400;hw=155
 for p,q in zip(points,points[1:]+points[:1]):
  dx,dy=q[0]-p[0],q[1]-p[1];d=math.hypot(dx,dy)
  if d<.001:continue
  fx,fy=dx/d,dy/d;rx,ry=-fy,fx
  shapes.append(Polygon([(p[0]-fx*hl+rx*hw,p[1]-fy*hl+ry*hw),(q[0]+fx*hl+rx*hw,q[1]+fy*hl+ry*hw),(q[0]+fx*hl-rx*hw,q[1]+fy*hl-ry*hw),(p[0]-fx*hl-rx*hw,p[1]-fy*hl-ry*hw)]))
 sweeps.append((i,unary_union(shapes)))
outer=wkt.loads((S/'outer.wkt').read_text());rows=[]
for delta in range(-12000,12001,250):
 xx,yy=x+delta*c,y+delta*s;poly=Polygon([(xx+c*u-s*v,yy+s*u+c*v) for u,v in [(-2425,-181),(-2425,181),(2425,181),(2425,-181)]])
 bad=[i for i,z in sweeps if z.intersects(poly)]
 rows.append(dict(delta=delta,position=[xx,yy,0],overlap_lanes=bad,inside_pavement=outer.covers(poly)))
(P/'station4_candidates.json').write_text(json.dumps(rows,indent=2));print('valid',sorted([r for r in rows if not r['overlap_lanes'] and r['inside_pavement']],key=lambda r:abs(r['delta']))[:8])