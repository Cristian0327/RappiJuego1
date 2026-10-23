import json,numpy as np,heapq,math
from pathlib import Path
from scipy.spatial import cKDTree
W=Path('new_map_audit');p=json.loads((W/'integration_plan.json').read_text());m=json.loads((W/'manifest.json').read_text());road=m['roads'][0];c=np.array(road['center'])*[100,-100,100];tree=cKDTree(c[:,:2]);half=np.array(road['halfwidth'])*100
step=150;ox=-67080.0;oy=-82560.0;nx=895;ny=1101;xx,yy=np.meshgrid(ox+np.arange(nx)*step,oy+np.arange(ny)*step);q=np.stack([xx.ravel(),yy.ravel()],axis=1);ds,idx=tree.query(q);blocked=(ds<half[idx]-240).reshape(ny,nx)
from PIL import Image
from scipy.ndimage import distance_transform_edt
physical=np.array(Image.open(W/'obstacles.png'))>0
clearance=distance_transform_edt(~physical)*100
ix=np.clip(((xx+68800.0)/100).astype(int),0,1375);iy=np.clip(((yy+86000.0)/100).astype(int),0,1719)
blocked |= clearance[iy,ix]<85
def cell(v):return (round((v[0]-ox)/step),round((v[1]-oy)/step))
def astar(a,b):
 a=cell(a);b=cell(b)
 if blocked[a[1],a[0]] or blocked[b[1],b[0]]:return []
 h=lambda n:math.dist(n,b);queue=[(h(a),0,a)];cost={a:0};prev={}
 while queue:
  _,g,n=heapq.heappop(queue)
  if n==b:
   route=[b]
   while route[-1]!=a:route.append(prev[route[-1]])
   return [[ox+x*step,oy+y*step,20] for x,y in route[::-1]]
  if g!=cost.get(n):continue
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
   v=(n[0]+dx,n[1]+dy)
   if not(0<=v[0]<nx and 0<=v[1]<ny) or blocked[v[1],v[0]]:continue
   if dx and dy and (blocked[n[1],v[0]] or blocked[v[1],n[0]]):continue
   ng=g+math.hypot(dx,dy)
   if ng<cost.get(v,1e12):cost[v]=ng;prev[v]=n;heapq.heappush(queue,(ng+h(v),ng,v))
 return []
valid_starts=[]
for ci,v in enumerate(c):
 tangent=c[min(ci+1,len(c)-1)]-c[max(ci-1,0)];tangent[2]=0;tangent/=max(np.linalg.norm(tangent),1e-6);right=np.array([-tangent[1],tangent[0],0])
 for side in [-1,1]:
  sp=v+right*side*(half[ci]-100);cc=cell(sp)
  if 0<=cc[0]<nx and 0<=cc[1]<ny and not blocked[cc[1],cc[0]]:valid_starts.append(sp)
starts_tree=cKDTree(np.array(valid_starts)[:,:2])
for s in p['shops']:
 i=s['road_index'];center=np.array(s['center']);direction=-np.array([*s['store_axes'][1],0]);entrance=center+direction*1600;entrance[2]=20
 # Approach outside the doorway, leaving its opening unobstructed.
 goal=entrance+direction*80;normal=c[i]-center;normal[2]=0;normal/=np.linalg.norm(normal);start=c[i]-normal*(half[i]-100);start[2]=20
 route=astar(start,goal)
 if not route:
  _,candidates=starts_tree.query(goal[:2],k=24)
  for j in candidates:
   route=astar(valid_starts[j],goal)
   if route:break
 s['entrance']=entrance.tolist();s['store_yaw']=math.degrees(math.atan2(direction[1],direction[0]))+90;s['walk_link']=route
 print('STORE_LINK',len(route))
(W/'integration_plan.json').write_text(json.dumps(p))


