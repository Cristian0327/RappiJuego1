import json,numpy as np,heapq,math
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,binary_dilation,label
from scipy.spatial import cKDTree
U=Path(__file__).parent;W=U.parent/'new_map_audit';p=json.loads((W/'integration_plan.json').read_text());m=json.loads((W/'manifest.json').read_text());plan=json.loads((U/'secondary_road_plan.json').read_text());occ=np.array(Image.open(W/'obstacles.png'))>0
# The physical wall raster preserves courtyards and avoids conservative block-wide bounding boxes.
for box in [b for b in p['building_footprints'] if 'complemento' in b[4] or 'Relleno urbano' in b[4]]:
 x0,y0,x1,y1=map(int,[(box[0]+40000)/100,(box[1]+50000)/100,(box[2]+40000)/100,(box[3]+50000)/100]);occ[y0:y1+1,x0:x1+1]=True
# Include all full store plots and the accepted additional building footprints.
from PIL import ImageDraw
shopmask=Image.fromarray((occ*255).astype(np.uint8));draw=ImageDraw.Draw(shopmask)
for store in p['shops']:
 c=np.array(store['center'][:2]);aa,bb=np.array(store['store_axes']);corners=[c+aa*x+bb*y for x,y in [(-1200,-1600),(1200,-1600),(1200,1600),(-1200,1600)]];draw.polygon([((q[0]+40000)/100,(q[1]+50000)/100) for q in corners],fill=255)
for item in json.loads((U/'accepted_infill.json').read_text()):
 lo,hi=np.array(item['bounds'])*[100,-100,100];a=np.minimum(lo,hi);b=np.maximum(lo,hi);draw.rectangle(((int((a[0]+40000)/100),int((a[1]+50000)/100)),(int((b[0]+40000)/100),int((b[1]+50000)/100))),fill=255)
occ=np.array(shopmask)>0
# 2 m route grid and 6.7 m clearance, including sidewalk and safety margin.
clear=distance_transform_edt(~occ)*100;flat=np.array(Image.open(U/'flat_urban_terrain.png'))>0;flatdist=distance_transform_edt(flat)*100;free=(clear[::2,::2]>670)&(flatdist[::2,::2]>670);labels,nlabels=label(free);mainprobe=np.array(m['roads'][0]['center'])*[100,-100,100];ix=np.clip(((mainprobe[:,0]+40000)/200).astype(int),0,free.shape[1]-1);iy=np.clip(((mainprobe[:,1]+50000)/200).astype(int),0,free.shape[0]-1);counts=np.bincount(labels[iy,ix]);counts[0]=0;free=labels==np.argmax(counts);H,V=free.shape;near=cKDTree(np.argwhere(free));scale=200;origin=np.array([-40000,-50000]);roads=[]
def grid(q):return tuple(np.rint((np.array(q)-origin)/scale).astype(int)[::-1])
def world(q):return (np.array(q[::-1])*scale+origin).tolist()
def snap(q):
 y,x=grid(q)
 if 0<=y<H and 0<=x<V and free[y,x]:return(y,x)
 return tuple(int(v) for v in near.data[near.query([y,x])[1]])
def astar(a,b):
 a=snap(a);b=snap(b);ay,ax=a;by,bx=b;dy0=by-ay;dx0=bx-ax;den=max(1,dy0*dy0+dx0*dx0);heap=[(0,0,a)];cost={a:0};prev={};done=set()
 while heap:
  _,g,u=heapq.heappop(heap)
  if u in done:continue
  if u==b:
   out=[u]
   while u in prev:u=prev[u];out.append(u)
   return out[::-1]
  done.add(u)
  for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
   v=(u[0]+dy,u[1]+dx)
   if not(0<=v[0]<H and 0<=v[1]<V and free[v]):continue
   if dy and dx and not(free[u[0]+dy,u[1]] and free[u[0],u[1]+dx]):continue
   t=max(0,min(1,((v[0]-ay)*dy0+(v[1]-ax)*dx0)/den));deviation=math.hypot(v[0]-ay-t*dy0,v[1]-ax-t*dx0);ng=g+math.hypot(dx,dy)*(1+deviation*.055)
   if ng<cost.get(v,1e20):cost[v]=ng;prev[v]=u;heapq.heappush(heap,(ng+math.dist(v,b),ng,v))
 raise RuntimeError('No safe road route')
main=np.array(m['roads'][0]['center'])*[100,-100,100];main_tree=cKDTree(main[:,:2])
for s in plan['secondary_roads']:
 anchors=s['points']; first=main[main_tree.query(anchors[0])[1],:2].tolist();last=main[main_tree.query(anchors[-1])[1],:2].tolist();s['points']=[first]+anchors+[last]
 path=[]
 for a,b in zip(s['points'],s['points'][1:]):
  part=astar(a,b);path+=part if not path else part[1:]
 # Keep straight runs as single segments, with physical safety maintained by the sampled grid.
 out=[path[0]]
 for i in range(1,len(path)-1):
  if (np.array(path[i])-path[i-1]).tolist()!=(np.array(path[i+1])-path[i]).tolist():out.append(path[i])
 out.append(path[-1]);s['points']=[world(q) for q in out];s['samples']=[world(q) for q in path];roads.append(s);print(s['name'],len(path),flush=True)
plan['secondary_roads']=roads;plan['routing']='original source curves with physical wall clearance; buildings preserved';(U/'secondary_road_plan.json').write_text(json.dumps(plan,indent=2));print('SAFE_SECONDARY_ROUTES_READY',len(roads))

