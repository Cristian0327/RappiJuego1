import json,numpy as np,math,shutil
from pathlib import Path
from scipy.spatial import cKDTree
U=Path(__file__).resolve().parent;O=U.parent/'urban_refresh';W=O.parent/'new_map_audit';p=json.loads((W/'integration_plan.json').read_text());m=json.loads((W/'manifest.json').read_text());junctions=json.loads((U/'junction_plan.json').read_text());jtree=cKDTree(np.array([v['position'][:2] for v in junctions]));bp=np.array(p['lanes'][6]);bt=np.roll(bp,-1,axis=0)-np.roll(bp,1,axis=0);bt[:,2]=0;bt/=np.linalg.norm(bt,axis=1)[:,None];br=np.stack([-bt[:,1],bt[:,0],np.zeros(len(bt))],axis=1);main=np.array(m['roads'][0]['center'])*[100,-100,100];mtree=cKDTree(main[:,:2]);shops=np.array([s['center'][:2] for s in p['shops']]);candidates=[]
for i in range(12,len(bp)-12,2):
 if np.dot(bt[i-7],bt[i+7])<.999:continue
 q=bp[i]-br[i]*330;q[2]=20
 if jtree.query(q[:2])[0]<6400 or np.min(np.linalg.norm(shops-q[:2],axis=1))<4000:continue
 ds=np.linalg.norm(main[:,:2]-q[:2],axis=1);mi=int(np.argmin(ds));other=np.minimum(abs(np.arange(len(main))-mi),len(main)-abs(np.arange(len(main))-mi))>35
 if min(ds[other])<4000:continue
 candidates.append((i,q))
chosen=[]
for old in p['stations']:
 for i,q in sorted(candidates,key=lambda v:np.linalg.norm(v[1][:2]-old['position'][:2])):
  if all(np.linalg.norm(q[:2]-v[1][:2])>10000 for v in chosen):chosen.append((i,q));break
 if len(chosen)>=7:break
stations=[];crossings=[]
for si,(i,q) in enumerate(chosen):
 yaw=math.degrees(math.atan2(bt[i,1],bt[i,0]));stations.append(dict(position=q.tolist(),bus_stop=bp[i].tolist(),yaw=yaw,route_index=i))
 for end in [-1,1]:
  at=q+bt[i]*2850*end;idx=mtree.query(at[:2])[1];at=main[idx].copy();at[2]=0;crossings.append(dict(position=at.tolist(),yaw=yaw,forward=bt[i].tolist(),halfwidth=float(m['roads'][0]['halfwidth'][idx]*100),road_index=int(idx),station_access=True,station_id=si,station_end=end,signal_group=2))
result=dict(stations=stations,crossings=crossings,candidate_count=len(candidates));(U/'two_sided_stations.json').write_text(json.dumps(result,indent=2));print('STATIONS',len(stations),'TWO_END_CROSSINGS',len(crossings),'CANDIDATES',len(candidates))
