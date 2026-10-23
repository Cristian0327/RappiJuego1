import json,numpy as np,math,heapq
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree
U=Path(__file__).resolve().parent;O=U.parent/'urban_refresh';setup=(O/'route_secondary_roads.py').read_text();ns={'__file__':str(O/'route_secondary_roads.py')};exec(compile(setup[:setup.index('\nmain=np.array(m')],'PhysicalReserve','exec'),ns);free=ns['free'];H,V=free.shape;clear=ns['clear'];flatdist=ns['flatdist'];m=ns['m'];snap=ns['snap'];world=ns['world'];main=np.array(m['roads'][0]['center'])*[100,-100,100];tree=cKDTree(main[:,:2]);src={};exec(compile((O/'plan_secondary_roads.py').read_text().split('def dist')[0],'OriginalRoadAnchors','exec'),{'__file__':str(O/'plan_secondary_roads.py')},src);original=src['lines'];roads=[]
def catmull(p):
 p=np.array(p);ext=np.concatenate([p[:1],p,p[-1:]]);out=[]
 for i in range(1,len(ext)-2):
  a,b,c,d=ext[i-1:i+3]
  for t in np.linspace(0,1,24,endpoint=False):out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 return np.array(out+[p[-1]])
for row in original:
 desired=catmull(row['points']);start=main[tree.query(desired[0])[1],:2];end=main[tree.query(desired[-1])[1],:2];anchors=np.concatenate([[start],desired,[end]]);mask=Image.new('L',(V,H),0);draw=ImageDraw.Draw(mask);draw.line([((q[0]+68800)/200,(q[1]+86000)/200) for q in anchors],fill=255,width=1);field=distance_transform_edt(np.array(mask)==0);a=snap(start);b=snap(end);heap=[(0,0,a)];cost={a:0};prev={};closed=set()
 while heap:
  _,g,x=heapq.heappop(heap)
  if x in closed:continue
  if x==b:break
  closed.add(x)
  for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
   y=(x[0]+dy,x[1]+dx)
   if not(0<=y[0]<H and 0<=y[1]<V and free[y]):continue
   if dx and dy and not(free[x[0]+dy,x[1]] and free[x[0],x[1]+dx]):continue
   ng=g+math.hypot(dx,dy)*(1+field[y]*.3)
   if ng<cost.get(y,1e30):cost[y]=ng;prev[y]=x;heapq.heappush(heap,(ng+math.dist(y,b),ng,y))
 else:raise RuntimeError('No connected corridor '+row['name'])
 path=[b];x=b
 while x in prev:x=prev[x];path.append(x)
 path=path[::-1];row['samples']=[world(v) for v in path];row['points']=[v.tolist() for v in anchors];roads.append(row);print('CORRIDOR',row['name'],len(path),flush=True)
plan=dict(secondary_roads=roads);(O/'secondary_road_plan.json').write_text(json.dumps(plan));(U/'corridor_grid_plan.json').write_text(json.dumps(plan))
# Apply the tangent-arc portion of the curve builder to the safe non-backtracking routes.
s=(U/'curve_roads.py').read_text();s=s[s.index('radii=[]'):] if 'radii=[]' in s else s
# The smoothing portion starts at its safety helper and uses the current physical reserve.
s=(U/'curve_roads.py').read_text();body=s[s.index('def safe'):];body=body.replace('margin=960','margin=650').replace('if safe(arc,600)','if safe(arc,610)');radii=[];old=O;exec(compile(body,'RoundTangentCorridors','exec'))

