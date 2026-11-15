import json,sys,math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.cluster.hierarchy import fclusterdata
P=Path(__file__).resolve().parent;R=P.parent;sys.path.insert(0,str(R/'urban_refresh/python_deps'))
from shapely.geometry import LineString,Point
from shapely.strtree import STRtree
lanes=[np.array(q) for q in json.loads((P/'actual_lanes.json').read_text())];segments=[];meta=[]
for li in [0,1,2,3,6]:
 q=lanes[li]
 for i,a in enumerate(q):
  b=q[(i+1)%len(q)]
  if np.linalg.norm(b[:2]-a[:2])<1:continue
  segments.append(LineString([a[:2],b[:2]]));meta.append((li,i))
tree=STRtree(segments);points=[]
for i,line in enumerate(segments):
 for j in tree.query(line,predicate='intersects'):
  j=int(j)
  if j<=i:continue
  li,si=meta[i];lj,sj=meta[j]
  if li==lj and min(abs(si-sj),len(lanes[li])-abs(si-sj))<6:continue
  a=np.array(line.coords);b=np.array(segments[j].coords);da=a[1]-a[0];db=b[1]-b[0];sine=abs(np.cross(da,db))/(np.linalg.norm(da)*np.linalg.norm(db))
  if sine<.22:continue
  p=line.intersection(segments[j])
  if p.geom_type=='Point':points.append(list(p.coords[0]))
points=np.array(points);labels=fclusterdata(points,1900,criterion='distance',method='single');rawcenters=[]
for label in sorted(set(labels)):rawcenters.append(points[labels==label].mean(0).tolist())
rawcenters=np.array(rawcenters);groups=fclusterdata(rawcenters,6000,criterion='distance',method='single');regions=[rawcenters[groups==label] for label in sorted(set(groups))];centers=[q.mean(0).tolist() for q in regions]
print('ACTUAL_TRAFFIC_CONFLICT_ZONES',len(centers),centers,flush=True)
events=[]
for li,q in enumerate(lanes):
 line=LineString(np.vstack([q[:,:2],q[0,:2]]));length=line.length;ds=np.arange(0,length,75);samples=np.array([line.interpolate(t).coords[0] for t in ds]);row=[]
 for ji,c in enumerate(centers):
  inside=np.min(np.linalg.norm(samples[:,None,:]-regions[ji][None,:,:],axis=2),axis=1)<2000
  from scipy.ndimage import binary_closing
  n=len(inside);inside=binary_closing(np.tile(inside,3),structure=np.ones(27))[n:2*n]
  # Rotate to an outside sample, so wraparound intervals remain whole.
  if not inside.any():continue
  outside=np.where(~inside)[0];assert len(outside);offset=int(outside[0]);indices=(np.arange(len(ds))+offset)%len(ds);flags=inside[indices];starts=np.where(flags&~np.r_[False,flags[:-1]])[0];ends=np.where(flags&~np.r_[flags[1:],False])[0]
  for st,en in zip(starts,ends):
   entry=float(ds[indices[st]]);exit=float((ds[indices[en]]+75)%length);middle=(entry+(exit-entry+length)%length*.5)%length;before=np.array(line.interpolate((entry+100)%length).coords[0])-np.array(line.interpolate((entry-100+length)%length).coords[0]);before/=np.linalg.norm(before);row.append(dict(junction=ji,entry=entry,exit=exit,direction=before.tolist(),span=(exit-entry+length)%length))
 events.append(dict(length=length,events=sorted(row,key=lambda e:e['entry'])))
# At each junction use one fixed principal axis for phase A, perpendicular approaches phase B.
for ji,c in enumerate(centers):
 dirs=[e['direction'] for row in events for e in row['events'] if e['junction']==ji];axis=np.array(dirs[0])
 for row in events:
  for e in row['events']:
   if e['junction']==ji:e['group']=0 if abs(np.dot(axis,e['direction']))>.70 else 1
movements=[];lookup={}
for li,row in enumerate(events):
 canonical={4:0,5:1}.get(li,li)
 line=LineString(np.vstack([lanes[li][:,:2],lanes[li][0,:2]]))
 for e in row['events']:
  key=(canonical,e['junction'],round(e['entry']/50));mid=lookup.get(key)
  if mid is None:
   mid=len(movements);lookup[key]=mid;span=e['span'];q=[line.interpolate((e['entry']+d)%line.length).coords[0] for d in np.linspace(0,span,max(3,int(span/100)+1))];movements.append(dict(lane=canonical,junction=e['junction'],entry=e['entry'],exit=e['exit'],path=q))
  e['movement']=mid
count=len(movements);compatible=np.eye(count,dtype=bool)
for i,a in enumerate(movements):
 for j,b in enumerate(movements[:i]):
  safe=a['junction']!=b['junction'] or LineString(a['path']).distance(LineString(b['path']))>410
  compatible[i,j]=compatible[j,i]=safe
(P/'arc_conflicts.json').write_text(json.dumps(dict(centers=centers,lanes=events,movements=movements,compatible=compatible.ravel().tolist(),movement_count=count),indent=2));print('ARC_CONFLICT_EVENTS',[len(r['events']) for r in events],count,flush=True)
