import sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'python_deps'))
import numpy as np
from shapely import wkt
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
S=R.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
old=json.loads((S/'actual_lanes.json').read_text());obstacles=unary_union([wkt.loads(x['wkt']) for x in json.loads((R/'route_obstacle_footprints.json').read_text())]);asphalt=wkt.loads((S/'asphalt.wkt').read_text());outer=wkt.loads((S/'outer.wkt').read_text());result=[];reports=[]
for li,raw in enumerate(old):
 if li in [4,5]:result.append(result[{4:0,5:1}[li]]);continue
 q=np.array(raw);n=len(q);margin=165;road=asphalt.union(outer.intersection(LineString(raw+[raw[0]]).buffer(300)));free=road.buffer(-100).difference(obstacles.buffer(margin));pf=prep(free);po=prep(obstacles);hl=915 if li==6 else 340;hw=155
 tangent=np.roll(q[:,:2],-1,axis=0)-np.roll(q[:,:2],1,axis=0);tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-6);normals=np.column_stack([-tangent[:,1],tangent[:,0]])
 offsets=np.arange(-1600,1601,50);k=len(offsets);zero=int(np.where(offsets==0)[0][0]);cand=q[:,None,:2]+normals[:,None,:]*offsets[None,:,None]
 valid=np.array([[pf.covers(Point(p)) for p in row] for row in cand]);
 for i,p in enumerate(q):
  if valid[i,zero] and obstacles.distance(Point(p[:2]))>3500 and asphalt.boundary.distance(Point(p[:2]))>200:valid[i,:]=False;valid[i,zero]=True
 missing=np.where(~valid.any(axis=1))[0]
 assert not len(missing),(li,'no physical corridor within 8m',missing.tolist())
 anchors=[i for i in range(n) if valid[i,zero] and free.boundary.distance(Point(q[i,:2]))>100];anchor=anchors[0] if anchors else int(np.where(valid[:,zero])[0][0]);order=(np.arange(n+1)+anchor)%n
 costs=np.full(k,np.inf);costs[zero]=0;parents=[]
 for step in range(1,n+1):
  a,b=order[step-1],order[step];newcost=np.full(k,np.inf);pred=np.full(k,-1,int)
  for j in np.where(valid[b])[0]:
   if step==n and j!=zero:continue
   for h in np.where(np.isfinite(costs)&(np.abs(offsets-offsets[j])<=150))[0]:
    extra=(offsets[j]/250)**2+((offsets[j]-offsets[h])/65)**2
    cost=costs[h]+extra
    if cost>=newcost[j]:continue
    pa,pb=cand[a,h],cand[b,j]
    if not pf.covers(LineString([pa,pb])):continue
    f=pb-pa;d=np.linalg.norm(f)
    if d<1:continue
    f=f/d;normal=np.array([-f[1],f[0]]);box=Polygon([pa-f*hl+normal*hw,pb+f*hl+normal*hw,pb+f*hl-normal*hw,pa-f*hl-normal*hw])
    if po.intersects(box):continue
    newcost[j]=cost;pred[j]=h
  assert np.isfinite(newcost).any(),(li,'unconnected corridor',int(b),step)
  costs=newcost;parents.append(pred)
 idx=zero;choices=np.zeros(n,int)
 for step in range(n,0,-1):
  b=order[step];choices[b]=idx;idx=parents[step-1][idx]
 new=q.copy();new[:,:2]=cand[np.arange(n),choices];ds=offsets[choices];assert all(pf.covers(LineString([new[i,:2],new[(i+1)%n,:2]])) for i in range(n))
 result.append(new.tolist());reports.append(dict(lane=li,changed_points=int(np.count_nonzero(ds)),max_offset_cm=int(max(abs(ds))),max_step_cm=int(max(abs(np.diff(np.r_[ds,ds[0]]))))));print(reports[-1],flush=True)
(R/'clearance_lanes.json').write_text(json.dumps(result));(R/'clearance_lane_plan.json').write_text(json.dumps(reports,indent=2))