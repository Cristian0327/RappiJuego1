import sys,json,copy,numpy as np,math
from pathlib import Path
U=Path(__file__).parent;sys.path.insert(0,str(U/'python_deps'))
from shapely import wkt
from shapely.geometry import box,LineString,Point
from shapely.ops import unary_union
from scipy.spatial import cKDTree
W=U.parent/'new_map_audit';m=json.loads((W/'manifest.json').read_text());p=json.loads((W/'integration_plan.json').read_text());reserve=wkt.loads((U/'road_reserve.wkt').read_text());st=json.loads((U/'station_expansion_plan.json').read_text());buildings=[box(*b[:4]) for b in p['building_footprints']];road=unary_union([LineString((np.array(v['center'])*[100,-100,100])[:,:2]).buffer(float(np.median(v['halfwidth'])*100)+200) for v in m['roads']]+[reserve.buffer(150)]);walk=unary_union([LineString(np.array(v)[:,:2]).buffer(180) for v in p['walk_routes']]+[LineString(np.array(v['walk_link'])[:,:2]).buffer(180) for v in p['shops'] if len(v['walk_link'])>1]);stores=unary_union([Point(v['center'][:2]).buffer(3800) for v in p['shops']]);stations=unary_union([Point(v['position'][:2]).buffer(4000) for v in st['stations']]);fixed=unary_union(buildings+[road,walk,stores,stations]);protos=[]
for v in m['instances']:
 if 'bounds' not in v or v.get('urban_infill'):continue
 lo,hi=np.array(v['bounds'])*[100,-100,100];a=np.minimum(lo,hi);b=np.maximum(lo,hi);dim=b-a
 if 600<max(dim[:2])<2200 and dim[2]>400 and dim[2]<3200:protos.append((v,(a+b)/2,dim))
tree=cKDTree([v[1][:2] for v in protos]);cands=[]
for x in range(-50000,50000,1800):
 for y in range(-65000,65000,1800):
  q=np.array([x,y]);dist,idx=tree.query(q)
  if not 2200<dist<6500 or not 1000<road.distance(Point(q))<5500:continue
  v,c,dim=protos[idx];foot=box(x-dim[0]/2-250,y-dim[1]/2-250,x+dim[0]/2+250,y+dim[1]/2+250)
  if not fixed.intersects(foot):cands.append((dist,v,c,dim,q,foot))
cands.sort(key=lambda z:z[0]);chosen=[]
for _,v,c,dim,q,foot in cands:
 if any(foot.intersects(k['foot']) for k in chosen):continue
 o=copy.deepcopy(v);shift=np.array([q[0]-c[0],q[1]-c[1],0]);o['location']=(np.array(o['location'])+shift/[100,-100,100]).tolist();o['bounds']=(np.array(o['bounds'])+shift/[100,-100,100]).tolist();o['source']=v['source']+' | Relleno urbano '+str(len(chosen)+1);o['urban_infill']=True;chosen.append(dict(instance=o,foot=foot))
 if len(chosen)>=56:break
(U/'additional_infill_plan.json').write_text(json.dumps([v['instance'] for v in chosen],indent=2));print('ADDITIONAL_MATCHING_BUILDINGS',len(chosen))
