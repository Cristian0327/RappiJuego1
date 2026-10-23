import json,numpy as np,math,heapq
from pathlib import Path
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt
from scipy.spatial import cKDTree
from PIL import Image
C=Path('compact_city');src=json.loads((C/'monserrate_destination.json').read_text());base=np.array(src['base'][:2]);goal=np.array(src['summit'][:2]);raw=np.load(C/'original_terrain_heights_2m.npy');h=gaussian_filter(np.nan_to_num(raw),1.5);origin=np.array([-40000,-50000]);scale=200;yy,xx=np.indices(h.shape);xy=np.stack([xx*scale-40000,yy*scale-50000],axis=-1);dist=np.linalg.norm(xy-goal,axis=-1);entrydist=np.linalg.norm(xy-base,axis=-1);occ=distance_transform_edt(np.array(Image.open('new_map_audit/obstacles.png'))==0)[::2,::2]*100;roads=json.loads(Path('urban_refresh/secondary_road_plan.json').read_text())['secondary_roads'];roadpoints=np.concatenate([np.array(v['samples']) for v in roads]);tree=cKDTree(roadpoints);rd=tree.query(xy.reshape(-1,2))[0].reshape(h.shape);permitted=np.isfinite(raw)&(raw>=-5)&(dist<19000)&(occ>230)&((rd>450)|(entrydist<1500));side=(goal-base)/np.linalg.norm(goal-base);permitted &= np.sum((xy-base)*side,axis=-1)>-2500
# Pick a genuinely flat approach to avoid starting on the abrupt voxel cliff itself.
choices=np.argwhere(permitted&(h<30)&(entrydist<3000));a=tuple(choices[np.argmin(np.linalg.norm(xy[choices[:,0],choices[:,1]]-base,axis=1))]);choices=np.argwhere(permitted&(dist<1800)&(abs(raw-h)<350)&(raw>3500));b=tuple(choices[np.argmin(np.linalg.norm(xy[choices[:,0],choices[:,1]]-goal,axis=1))]);moves=[(dy,dx) for dy in range(-2,3) for dx in range(-2,3) if (dx or dy) and math.gcd(abs(dx),abs(dy))==1];path=None
for slope in [.22,.28,.35]:
 heap=[(0,0,a)];cost={a:0};prev={};closed=set()
 while heap:
  _,g,v=heapq.heappop(heap)
  if v in closed:continue
  if v==b:
   path=[v]
   while v in prev:v=prev[v];path.append(v)
   path=path[::-1];break
  closed.add(v)
  for dy,dx in moves:
   w=(v[0]+dy,v[1]+dx)
   if not(0<=w[0]<h.shape[0] and 0<=w[1]<h.shape[1]) or not permitted[w]:continue
   ds=math.hypot(dx,dy)*scale;gr=abs(float(h[w]-h[v]))/ds
   if gr>slope:continue
   # Favor real contours, avoiding deep artificial cuts or fills.
   ng=g+ds*(1+(gr/.14)**4+abs(float(raw[w]-h[w]))/150)
   if ng<cost.get(w,1e30):cost[w]=ng;prev[w]=v;heapq.heappush(heap,(ng+math.dist(w,b)*scale,ng,w))
 if path:break
if not path:raise RuntimeError('No natural mountain route')
q=np.array([xy[y,x] for y,x in path]);q=np.concatenate([[base],q]);
# Smooth only the horizontal corners; height and physical terrain are checked again afterwards.
for _ in range(3):q=np.concatenate([q[:1],np.stack([q[:-1]*.75+q[1:]*.25,q[:-1]*.25+q[1:]*.75],axis=1).reshape(-1,2),q[-1:]])
length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))];samples=np.arange(0,length[-1],50);q=np.column_stack([np.interp(samples,length,q[:,i]) for i in range(2)]);z=map_coordinates(h,[(q[:,1]+50000)/200,(q[:,0]+40000)/200],order=1);z=np.maximum(0,z);z[0]=0
for i in range(1,len(z)):z[i]=min(z[i],z[i-1]+.25*np.linalg.norm(q[i]-q[i-1]))
for i in range(len(z)-2,-1,-1):z[i]=min(z[i],z[i+1]+.25*np.linalg.norm(q[i+1]-q[i]))
natural=map_coordinates(raw,[(q[:,1]+50000)/200,(q[:,0]+40000)/200],order=1);ds=np.linalg.norm(np.diff(q,axis=0),axis=1);grade=np.max(abs(np.diff(z))/np.maximum(ds,1));hill=dict(name='Camino_Monserrate_Jugador',points=np.column_stack([q,z]).tolist(),base=[*q[0],float(z[0])],summit=[*q[-1],float(z[-1])],length_m=float(sum(ds)/100),maximum_grade=float(grade),width_cm=300,player_allowed=['walk','bicycle','motorcycle'],npc_vehicles_allowed=False,cars_allowed=False,maximum_cut_fill_m=float(max(abs(z-natural))/100));(C/'monserrate_path.json').write_text(json.dumps(hill,indent=2));print('NATURAL_MON SERRATE_PATH_READY',hill['length_m'],hill['maximum_grade'],hill['maximum_cut_fill_m'],'summit',hill['summit'])
