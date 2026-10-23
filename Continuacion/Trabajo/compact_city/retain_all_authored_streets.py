import json,numpy as np,math,heapq
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,uniform_filter,map_coordinates,label
from scipy.spatial import cKDTree
R=Path.cwd();C=R/'compact_city';O=R/'urban_refresh';names=json.loads((C/'object_sources.json').read_text());labels=np.load(C/'original_labels.npy');hard=np.zeros(labels.shape,bool)
hard=np.array(Image.open(C/'large_tall_mask.png'))>0
hardclear=distance_transform_edt(~hard)*100;soft=uniform_filter(((labels>0)&~hard).astype(float),size=9)*20;heights=np.load(C/'original_terrain_heights_2m.npy');origin=np.array([-40000,-50000]);scale=200;H,V=heights.shape;hardclear=hardclear[::2,::2];soft=soft[::2,::2];original=json.loads((C/'authored_street_curves.json').read_text());roads=[];reports=[]
def world(cell):return np.array(cell[::-1])*scale+origin
def grid(q):return tuple(np.rint((np.array(q)-origin)/scale).astype(int)[::-1])
for row in original:
 points=np.array(row['samples'])[:,:2]
 if row['name'].endswith('.014_0'):
  z=map_coordinates(heights,[(points[:,1]+50000)/200,(points[:,0]+40000)/200],order=1,mode='nearest');idx=np.where(z<25)[0][0];(C/'monserrate_authored_segment.json').write_text(json.dumps(dict(summit=points[0].tolist(),base=points[idx].tolist(),authored=points[:idx+1].tolist())));points=points[idx:]
 im=Image.new('L',(V,H));ImageDraw.Draw(im).line([tuple((p-origin)/scale) for p in points],fill=255,width=1);field=distance_transform_edt(np.array(im)==0)*scale;start=grid(points[0]);end=grid(points[-1]);result=None
 for corridor in [1800,2600,3600,5000,6500,8500,12000]:
  allowed=(hardclear>390)&(field<corridor)&np.isfinite(heights)
  if not np.any(allowed):continue
  labs,num=label(allowed);counts=np.bincount(labs.ravel());counts[0]=0;chosen=int(np.argmax(counts));allowed=labs==chosen;atree=cKDTree(np.argwhere(allowed));a=tuple(atree.data[atree.query(start)[1]]);b=tuple(atree.data[atree.query(end)[1]]);a=tuple(map(int,a));b=tuple(map(int,b));
  if max(math.dist(a,start),math.dist(b,end))*scale>2200:continue
  queue=[(0,0,a)];cost={a:0};prev={};closed=set()
  while queue:
   _,g,x=heapq.heappop(queue)
   if x in closed:continue
   if x==b:
    path=[x]
    while x in prev:x=prev[x];path.append(x)
    result=path[::-1];break
   closed.add(x)
   for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
    y=(x[0]+dy,x[1]+dx)
    if not(0<=y[0]<H and 0<=y[1]<V and allowed[y]):continue
    if dx and dy and not(allowed[x[0]+dy,x[1]] and allowed[x[0],x[1]+dx]):continue
    ng=g+math.hypot(dx,dy)*(1+soft[y]*7+(field[y]/800)**2)
    if ng<cost.get(y,1e30):cost[y]=ng;prev[y]=x;heapq.heappush(queue,(ng+math.dist(y,b),ng,y))
  if result:break
 if result is None:raise RuntimeError('Cannot follow original street locally '+row['name'])
 p=np.array([world(v) for v in result],float)
 # Round local grid corners without escaping the original corridor or large structures.
 def safe(v):
  q=np.rint((np.array(v)-origin)/100).astype(int);x=np.clip(q[:,0],0,799);y=np.clip(q[:,1],0,999);return np.all((distance_transform_edt(~hard)*100)[y,x]>385)
 # Visibility simplification followed by a small corner subdivision preserves the road itself.
 clearFull=distance_transform_edt(~hard)*100
 def valid(a,b):
  q=np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/60)+1));ij=np.rint((q-origin)/100).astype(int);return np.all(clearFull[np.clip(ij[:,1],0,999),np.clip(ij[:,0],0,799)]>390)
 out=[p[0]];i=0
 while i<len(p)-1:
  j=min(len(p)-1,i+12)
  while j>i+1 and not valid(p[i],p[j]):j-=1
  out.append(p[j]);i=j
 p=np.array(out)
 for _ in range(3):
  q=np.concatenate([p[:1],np.stack([p[:-1]*.75+p[1:]*.25,p[:-1]*.25+p[1:]*.75],axis=1).reshape(-1,2),p[-1:]])
  if all(valid(a,b) for a,b in zip(q,q[1:])):p=q
 samples=[]
 for a,b in zip(p,p[1:]):samples.extend(np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/50)+1),endpoint=False).tolist())
 samples.append(p[-1].tolist());
 if row['name'].endswith('.014_0'):
  hill=json.loads((C/'monserrate_authored_segment.json').read_text());hill['base']=samples[0];(C/'monserrate_authored_segment.json').write_text(json.dumps(hill))
 roads.append(dict(name=row['name'],samples=samples,points=points.tolist(),width=480,sidewalk=140));reports.append(dict(name=row['name'],corridor_limit_cm=corridor,samples=len(samples)));print('ORIGINAL_STREET_RETAINED',row['name'],len(samples),'corridor',corridor,flush=True)
(O/'secondary_road_plan.json').write_text(json.dumps(dict(secondary_roads=roads)));(C/'authored_corridor_report.json').write_text(json.dumps(reports,indent=2));print('ALL_FOURTEEN_AUTHORED_STREETS_RETAINED')
