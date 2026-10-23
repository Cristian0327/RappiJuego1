import json,sys,numpy as np,math
from pathlib import Path
from scipy.spatial import cKDTree
U=Path(__file__).resolve().parent;O=U.parent/'urban_refresh';sys.path.insert(0,str(O/'python_deps'))
from shapely.geometry import LineString,Point
from shapely import STRtree
m=json.loads((O.parent/'new_map_audit/manifest.json').read_text());primary=[LineString((np.array(r['center'])*[100,-100,100])[:,:2]) for r in m['roads']];secondary=[LineString(v) for v in json.loads((U/'unique_centerlines.json').read_text())];raw=[]
def tangent(line,d):
 a=np.array(line.interpolate(max(0,d-300)).coords[0]);b=np.array(line.interpolate(min(line.length,d+300)).coords[0]);return (b-a)/max(1e-8,np.linalg.norm(b-a))
def add(q,a,b,kind):
 a=np.array(a);b=np.array(b)
 if abs(np.dot(a,b))>.86:return
 if any(np.linalg.norm(np.array(v['position'][:2])-q)<3000 for v in raw):return
 yaw=lambda v:math.degrees(math.atan2(v[1],v[0]));raw.append(dict(position=[float(q[0]),float(q[1]),0],axes=[a.tolist(),b.tolist()],kind=kind))
# True crossings between non-adjacent sections of the original principal.
c=np.array(primary[0].coords);segments=[LineString([a,b]) for a,b in zip(c,c[1:])];tree=STRtree(segments)
for i,line in enumerate(segments):
 for j in tree.query(line,predicate='intersects'):
  if j<=i+20:continue
  q=line.intersection(segments[j])
  if q.geom_type=='Point':add(np.array(q.coords[0]),tangent(primary[0],primary[0].project(q)),np.diff(np.array(segments[j].coords),axis=0)[0]/segments[j].length,'principal_principal')
# Open endpoints of the authored primary connect to a different section of the same road.
for idx in [0,len(c)-1]:
 dist=np.linalg.norm(c-c[idx],axis=1);dist[max(0,idx-35):min(len(c),idx+36)]=1e10;j=int(np.argmin(dist))
 if dist[j]<2200:add((c[idx]+c[j])/2,tangent(primary[0],primary[0].project(Point(c[idx]))),tangent(primary[0],primary[0].project(Point(c[j]))),'principal_principal')
for line in primary[1:]+secondary:
 for d in [0,line.length]:
  pt=line.interpolate(d);options=[(pt.distance(v),v) for v in primary];distance,major=min(options,key=lambda z:z[0]);limit=1800 if major==primary[0] else 700
  if distance<limit:
   proj=major.project(pt);q=np.array(major.interpolate(proj).coords[0]);add(q,tangent(major,proj),tangent(line,d),'principal_secundaria')
# Add only substantial secondary junctions; close/parallel duplicates have already been removed.
for i,a in enumerate(secondary):
 for b in secondary[i+1:]:
  hit=a.intersection(b)
  points=[hit] if hit.geom_type=='Point' else [g for g in getattr(hit,'geoms',[]) if g.geom_type=='Point']
  for q in points:add(np.array(q.coords[0]),tangent(a,a.project(q)),tangent(b,b.project(q)),'secundaria_secundaria')
(U/'junction_plan.json').write_text(json.dumps(raw,indent=2));print('STRATEGIC_JUNCTIONS',len(raw),{k:sum(v['kind']==k for v in raw) for k in set(v['kind'] for v in raw)})
