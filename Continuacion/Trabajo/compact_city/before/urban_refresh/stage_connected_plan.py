import json,copy,shutil,sys,numpy as np
from pathlib import Path
U=Path(__file__).parent;W=U.parent/'new_map_audit';sys.path.insert(0,str(U/'python_deps'));from shapely import wkt;from shapely.geometry import Point
for name in ['manifest.json','integration_plan.json']:
 bak=U/('before_connected_'+name)
 if not bak.exists():shutil.copy2(W/name,bak)
if not (U/'before_connected_placement_plan.json').exists():shutil.copy2(U/'placement_plan.json',U/'before_connected_placement_plan.json')
m=json.loads((U/'before_connected_manifest.json').read_text());p=json.loads((U/'before_connected_integration_plan.json').read_text());u=json.loads((U/'before_connected_placement_plan.json').read_text());st=json.loads((U/'station_expansion_plan.json').read_text());new=json.loads((U/'accepted_infill.json').read_text());m['instances']+=new;m['additional_urban_infill_count']=len(new)
for v in new:
 lo,hi=np.array(v['bounds'])*[100,-100,100];a=np.minimum(lo,hi);b=np.maximum(lo,hi);p['building_footprints'].append([a[0],a[1],b[0],b[1],v['source']])
p['stations']=st['stations'];u['stations']=st['stations'];u['crossings']=[c for c in u['crossings'] if all(np.linalg.norm(np.array(c['position'][:2])-s['position'][:2])>4000 for s in st['crossings'])]+st['crossings'];reserve=wkt.loads((U/'road_reserve.wkt').read_text());u['furniture']=[v for v in u['furniture'] if not reserve.buffer(170 if v['type']=='Banca' else 75).contains(Point(v['position'][:2]))]
for path,data in [(W/'manifest.json',m),(W/'integration_plan.json',p),(U/'placement_plan.json',u)]:path.write_text(json.dumps(data,indent=2))
print('CONNECTED_PLAN_STAGED',len(new),'buildings',len(p['stations']),'stations',len(u['crossings']),'crossings')
