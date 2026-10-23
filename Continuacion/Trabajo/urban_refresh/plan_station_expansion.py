import json,math,numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
from PIL import Image
from scipy.ndimage import distance_transform_edt
U=Path(__file__).parent;W=U.parent/'new_map_audit';m=json.loads((W/'manifest.json').read_text());p=json.loads((W/'integration_plan.json').read_text());roads=json.loads((U/'secondary_road_plan.json').read_text())['secondary_roads'];sec=np.array([q for s in roads for q in s['samples']]);stree=cKDTree(sec);main=np.array(m['roads'][0]['center'])*[100,-100,100];mtree=cKDTree(main[:,:2]);bp=np.array(p['lanes'][6]);bt=np.roll(bp,-1,axis=0)-np.roll(bp,1,axis=0);bt[:,2]=0;bt/=np.linalg.norm(bt,axis=1)[:,None];br=np.stack([-bt[:,1],bt[:,0],np.zeros(len(bt))],axis=1);boxes=np.array([q[:4] for q in p['building_footprints']]);shops=np.array([q['center'][:2] for q in p['shops']]);candidates=[]
for i in range(12,len(bp)-12,2):
 if np.dot(bt[i-7],bt[i+7])<.999:continue
 q=bp[i]-br[i]*330;q[2]=20
 if stree.query(q[:2])[0]<5500:continue
 ds=np.linalg.norm(main[:,:2]-q[:2],axis=1);mi=int(np.argmin(ds));other=np.minimum(abs(np.arange(len(main))-mi),len(main)-abs(np.arange(len(main))-mi))>35
 if np.min(ds[other])<4000:continue
 if np.min(np.linalg.norm(shops-q[:2],axis=1))<4000:continue
 # Check station corners against physical building bounds.
 corners=np.array([q[:2]+bt[i,:2]*x+br[i,:2]*y for x in [-2500,2500] for y in [-200,200]])
 if any(np.any((z[0]>boxes[:,0])&(z[0]<boxes[:,2])&(z[1]>boxes[:,1])&(z[1]<boxes[:,3])) for z in corners):continue
 candidates.append((i,q))
selected=[]
# Retain old stop locations where the new intersections allow it, then maximize coverage.
for old in p['stations']:
 near=sorted(candidates,key=lambda z:np.linalg.norm(z[1][:2]-old['position'][:2]))
 for i,q in near:
  if all(np.linalg.norm(q[:2]-z[1][:2])>11000 for z in selected):selected.append((i,q));break
while len(selected)<8:
 options=[z for z in candidates if all(np.linalg.norm(z[1][:2]-v[1][:2])>11000 for v in selected)]
 if not options:break
 z=max(options,key=lambda z:min(np.linalg.norm(z[1][:2]-v[1][:2]) for v in selected));selected.append(z)
stations=[];cross=[]
for i,q in selected:
 yaw=math.degrees(math.atan2(bt[i,1],bt[i,0]));stations.append(dict(position=q.tolist(),bus_stop=bp[i].tolist(),yaw=yaw,route_index=i));at=q-bt[i]*2850;idx=mtree.query(at[:2])[1];at=main[idx].copy();at[2]=0
 cross.append(dict(position=at.tolist(),yaw=yaw,forward=bt[i].tolist(),halfwidth=float(m['roads'][0]['halfwidth'][idx]*100),road_index=int(idx),station_access=True))
(U/'station_expansion_plan.json').write_text(json.dumps(dict(stations=stations,crossings=cross,candidate_count=len(candidates)),indent=2));print('SAFE_STATIONS',len(stations),'CANDIDATES',len(candidates));print([(s['route_index'],s['position'][:2]) for s in stations])
