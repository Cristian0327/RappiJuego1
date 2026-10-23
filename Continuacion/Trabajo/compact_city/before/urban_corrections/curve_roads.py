import json,numpy as np,math,shutil
from pathlib import Path
from scipy.spatial import cKDTree
U=Path(__file__).resolve().parent;old=U.parent/'urban_refresh';W=old.parent/'new_map_audit'
backup=U/'before_secondary_road_plan.json'
if not backup.exists():shutil.copy2(old/'secondary_road_plan.json',backup)
# Rebuild from the authored original anchors, with enough space for broad curved corners.
exec(compile((old/'plan_secondary_roads.py').read_text(),'AuthoredAnchors','exec'),{'__file__':str(old/'plan_secondary_roads.py')})
s=(old/'route_secondary_roads.py').read_text().replace('clear[::2,::2]>670','clear[::2,::2]>1150').replace('flatdist[::2,::2]>670','flatdist[::2,::2]>800');ns={'__file__':str(old/'route_secondary_roads.py')};exec(compile(s,'WiderCurveReserve','exec'),ns);clear=ns['clear'];flatdist=ns['flatdist'];m=ns['m'];main=np.array(m['roads'][0]['center'])*[100,-100,100];tree=cKDTree(main[:,:2]);plan=json.loads((old/'secondary_road_plan.json').read_text());radii=[]
def safe(q,margin=960):
 q=np.asarray(q);ix=((q[:,0]+68800)/100).astype(int);iy=((q[:,1]+86000)/100).astype(int)
 if np.any(ix<0)|np.any(iy<0)|np.any(ix>=clear.shape[1])|np.any(iy>=clear.shape[0]):return False
 return bool(np.all(clear[iy,ix]>margin)&np.all(flatdist[iy,ix]>620))
def segment(a,b):return np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/70)+1))
for row in plan['secondary_roads']:
 raw=np.array(row['samples'],float);stack=[];indices={}
 for q in raw:
  key=tuple(q)
  if key in indices:
   idx=indices[key]
   for v in stack[idx+1:]:indices.pop(tuple(v),None)
   stack=stack[:idx+1]
  else:indices[key]=len(stack);stack.append(q)
 raw=np.array(stack);raw[0]=main[tree.query(raw[0])[1],:2];raw[-1]=main[tree.query(raw[-1])[1],:2]
 out=[raw[0]];i=0
 while i<len(raw)-1:
  chosen=i+1
  for j in range(len(raw)-1,i+1,-1):
   if safe(segment(raw[i],raw[j])):chosen=j;break
  out.append(raw[chosen]);i=chosen
 p=np.array(out);smooth=[p[0]]
 for i in range(1,len(p)-1):
  a,b,c=p[i-1:i+2];la=np.linalg.norm(b-a);lb=np.linalg.norm(c-b)
  if min(la,lb)<1:continue
  v=(b-a)/la;w=(c-b)/lb;theta=math.acos(np.clip(np.dot(v,w),-1,1));sign=np.sign(np.cross(v,w))
  if theta<.025 or theta>3.0:smooth.append(b);continue
  distance=min(1200*math.tan(theta/2),la*.43,lb*.43);chosen=None
  for factor in [1,.8,.6,.4,.2,.1]:
   d=distance*factor;radius=d/math.tan(theta/2);entry=b-v*d;exit=b+w*d;center=entry+np.array([-v[1],v[0]])*sign*radius;start=math.atan2(entry[1]-center[1],entry[0]-center[0]);angles=np.linspace(start,start+sign*theta,max(5,int(radius*theta/45)+1));arc=center+radius*np.stack([np.cos(angles),np.sin(angles)],axis=1)
   if safe(arc,600):chosen=arc;radii.append(radius);break
  if chosen is None:raise RuntimeError('No safe curved corner '+row['name'])
  smooth+=segment(np.array(smooth[-1]),chosen[0]).tolist()[1:];smooth+=chosen.tolist()[1:]
 smooth+=segment(np.array(smooth[-1]),p[-1]).tolist()[1:];row['samples']=np.asarray(smooth).tolist();row['points']=p.tolist();row['curve_type']='tangent circular fillets, sampled at <=45cm';print('CURVED',row['name'],len(smooth),flush=True)
plan['curve_radius_cm']={'min':min(radii),'median':float(np.median(radii)),'max':max(radii)};plan['routing']='Connected source corridors with circular tangent corners and physical clearance';(old/'secondary_road_plan.json').write_text(json.dumps(plan,indent=2));(U/'curved_road_plan.json').write_text(json.dumps(plan,indent=2));print('CURVED_ROADS_READY',plan['curve_radius_cm'])
