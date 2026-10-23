import json,sys,numpy as np,math,shutil
from pathlib import Path
from PIL import Image
from scipy.ndimage import distance_transform_edt
R=Path.cwd();C=R/'compact_city';U=R/'urban_corrections';O=R/'urban_refresh';W=R/'new_map_audit';sys.path.insert(0,str(O/'python_deps'))
from shapely import wkt
from shapely.geometry import LineString
p=json.loads((W/'integration_plan.json').read_text());st=json.loads((U/'two_sided_stations.json').read_text());p['stations']=st['stations'];asphalt=wkt.loads((U/'unified_asphalt.wkt').read_text());clear=distance_transform_edt(np.array(Image.open(W/'obstacles.png'))==0)*100;routes=[]
def safe(points):
 pts=np.array(points);x=np.rint((pts[:,0]+40000)/100).astype(int);y=np.rint((pts[:,1]+50000)/100).astype(int)
 return np.all((x>=0)&(x<800)&(y>=0)&(y<1000)) and np.all(clear[y,x]>60) and LineString(pts[:,:2]).buffer(40).intersection(asphalt).area<1
for route in p['walk_routes']:
 if safe(route):routes.append(route)
for coords in json.loads((U/'unique_centerlines.json').read_text()):
 line=LineString(coords)
 for start in np.arange(1200,line.length-4000,4000):
  q=np.array([line.interpolate(d).coords[0] for d in np.linspace(start,start+2800,16)]);t=np.gradient(q,axis=0);t/=np.linalg.norm(t,axis=1)[:,None];rr=np.stack([-t[:,1],t[:,0]],1)
  for sign in [-1,1]:
   a=q+rr*(sign*460-32);b=q+rr*(sign*460+32);path=np.concatenate([a,b[::-1]]);path=np.concatenate([path,np.ones((32,1))*20],axis=1)
   if safe(path):routes.append(path.tolist())
assert len(routes)>15
rows=[]
for rid,route in enumerate(routes):
 for j in [3,11,19,27]:
  pt=route[j][:];pt[2]=108;delta=np.array(route[(j+1)%32])-route[j];rows.append(dict(route=rid,next=(j+1)%32,position=pt,yaw=math.degrees(math.atan2(delta[1],delta[0])),model=len(rows)%60))
p['walk_routes']=routes;p['pedestrians']=rows;p['player_start']=rows[len(rows)//2]['position'];(W/'integration_plan.json').write_text(json.dumps(p));print('SAFE_COMPACT_ROUTES',len(routes),'CITIZENS',len(rows))
exec(compile((O/'plan_urban_refresh.py').read_text(),'OriginalDensityFurniturePlan','exec'),{})
u=json.loads((O/'placement_plan.json').read_text());junctions=json.loads((U/'junction_plan.json').read_text());u['stations']=st['stations'];u['crossings']=[v for v in u['crossings'] if all(np.linalg.norm(np.array(v['position'][:2])-np.array(q['position'][:2]))>3500 for q in junctions+st['crossings'])]+st['crossings']
for v in u['crossings']:v['signal_group']=2
reserve=wkt.loads((O/'road_reserve.wkt').read_text());from shapely.geometry import Point
u['furniture']=[v for v in u['furniture'] if not reserve.buffer(180 if v['type']=='Banca' else 75).contains(Point(v['position'][:2]))]
(O/'placement_plan.json').write_text(json.dumps(u));(O/'station_expansion_plan.json').write_text(json.dumps(st));print('COMPACT_DRESSING',len(u['furniture']),len(u['crossings']),'crossings')
