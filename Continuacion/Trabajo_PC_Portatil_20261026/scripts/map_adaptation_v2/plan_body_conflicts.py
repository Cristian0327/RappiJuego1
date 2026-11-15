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
# Account for the complete bodies sweeping through bends, including paths
# whose center lines never intersect.
for li in [0,1,2,3,6]:
 line=LineString(np.vstack([lanes[li][:,:2],lanes[li][0,:2]]));ds=np.arange(0,line.length,180);pa=np.array([line.interpolate(x).coords[0] for x in ds]);fa=np.array([np.array(line.interpolate((x+90)%line.length).coords[0])-np.array(line.interpolate((x-90)%line.length).coords[0]) for x in ds]);fa/=np.linalg.norm(fa,axis=1)[:,None];ra=np.column_stack([-fa[:,1],fa[:,0]]);la=1000 if li==6 else 340;wa=155
 for lj in [k for k in [0,1,2,3,6] if k>li]:
  lineb=LineString(np.vstack([lanes[lj][:,:2],lanes[lj][0,:2]]));db=np.arange(0,lineb.length,180);pb=np.array([lineb.interpolate(x).coords[0] for x in db]);fb=np.array([np.array(lineb.interpolate((x+90)%lineb.length).coords[0])-np.array(lineb.interpolate((x-90)%lineb.length).coords[0]) for x in db]);fb/=np.linalg.norm(fb,axis=1)[:,None];rb=np.column_stack([-fb[:,1],fb[:,0]]);lb=1000 if lj==6 else 340;wb=155;treeb=cKDTree(pb);on_a=np.array([line.distance(Point(q)) for q in pb])<120
  for i,at in enumerate(pa):
   near=treeb.query_ball_point(at,la+lb+400)
   if not near:continue
   near=np.array(near);delta=pb[near]-at;dot=fb[near]@fa[i];sine=rb[near]@fa[i];ca=np.abs(dot);sa=np.abs(sine);valid=(np.abs(delta@fa[i])<la+lb*ca+wb*sa)&(np.abs(delta@ra[i])<wa+lb*sa+wb*ca)&(np.abs(np.einsum('ij,ij->i',delta,fb[near]))<lb+la*ca+wa*sa)&(np.abs(np.einsum('ij,ij->i',delta,rb[near]))<wb+la*sa+wa*ca);valid&=~((dot>.3)&on_a[near]&(lineb.distance(Point(at))<120))
   for q in pb[near[valid]]:points.append(((at+q)*.5).tolist())
points=np.unique(np.round(np.array(points)/300)*300,axis=0).tolist()
print('BODY_CONFLICT_POINTS',len(points),flush=True)
points=np.array(points);labels=fclusterdata(points,1900,criterion='distance',method='single');rawcenters=[]
for label in sorted(set(labels)):rawcenters.append(points[labels==label].mean(0).tolist())
rawcenters=np.array(rawcenters);groups=fclusterdata(rawcenters,6000,criterion='distance',method='single');regions=[points[np.isin(labels,np.array(sorted(set(labels)))[groups==label])] for label in sorted(set(groups))];centers=[q.mean(0).tolist() for q in regions]
print('ACTUAL_TRAFFIC_CONFLICT_ZONES',len(centers),centers,flush=True)
def make_events(regions):
 events=[]
 for li,q in enumerate(lanes):
  line=LineString(np.vstack([q[:,:2],q[0,:2]]));length=line.length;ds=np.arange(0,length,75);samples=np.array([line.interpolate(t).coords[0] for t in ds]);row=[]
  for ji,region in enumerate(regions):
   inside=np.min(np.linalg.norm(samples[:,None,:]-regions[ji][None,:,:],axis=2),axis=1)<2000
   from scipy.ndimage import binary_closing
   n=len(inside);inside=binary_closing(np.tile(inside,3),structure=np.ones(27))[n:2*n]
   # Rotate to an outside sample, so wraparound intervals remain whole.
   if not inside.any():continue
   outside=np.where(~inside)[0];assert len(outside);offset=int(outside[0]);indices=(np.arange(len(ds))+offset)%len(ds);flags=inside[indices];starts=np.where(flags&~np.r_[False,flags[:-1]])[0];ends=np.where(flags&~np.r_[flags[1:],False])[0]
   for st,en in zip(starts,ends):
    entry=float(ds[indices[st]]);exit=float((ds[indices[en]]+75)%length);middle=(entry+(exit-entry+length)%length*.5)%length;before=np.array(line.interpolate((entry+100)%length).coords[0])-np.array(line.interpolate((entry-100+length)%length).coords[0]);before/=np.linalg.norm(before);row.append(dict(junction=ji,entry=entry,exit=exit,direction=before.tolist(),span=(exit-entry+length)%length))
  events.append(dict(length=length,events=sorted(row,key=lambda e:e['entry'])))
 return events
while True:
 events=make_events(regions);parents=list(range(len(regions)))
 def find(x):
  while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
  return x
 for row in events:
  es=row['events'];length=row['length']
  for i,e in enumerate(es):
   other=es[(i+1)%len(es)];gap=(other['entry']-e['entry'])%length-e['span']
   if gap<3000 and e['junction']!=other['junction']:parents[find(other['junction'])]=find(e['junction'])
 groups2={}
 for i,r in enumerate(regions):groups2.setdefault(find(i),[]).append(r)
 if len(groups2)==len(regions):break
 regions=[np.vstack(parts) for parts in groups2.values()]
centers=[q.mean(0).tolist() for q in regions]
print('DISJOINT_BODY_ZONES',len(centers),flush=True)
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
(P/'body_arc_conflicts.json').write_text(json.dumps(dict(centers=centers,lanes=events,movements=movements,compatible=compatible.ravel().tolist(),movement_count=count),indent=2));print('ARC_CONFLICT_EVENTS',[len(r['events']) for r in events],count,flush=True)
