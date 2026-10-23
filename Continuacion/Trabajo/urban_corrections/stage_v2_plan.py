import json,shutil,numpy as np,sys
from pathlib import Path
U=Path(__file__).resolve().parent;O=U.parent/'urban_refresh';W=O.parent/'new_map_audit';sys.path.insert(0,str(O/'python_deps'));from shapely import wkt;from shapely.geometry import Point
for file in ['placement_plan.json','station_expansion_plan.json']:
 backup=U/('before_'+file)
 if not backup.exists():shutil.copy2(O/file,backup)
backup=U/'before_integration_plan.json'
if not backup.exists():shutil.copy2(W/'integration_plan.json',backup)
p=json.loads(backup.read_text());u=json.loads((U/'before_placement_plan.json').read_text());st=json.loads((U/'two_sided_stations.json').read_text());j=json.loads((U/'junction_plan.json').read_text());p['stations']=st['stations'];u['stations']=st['stations'];u['crossings']=[v for v in u['crossings'] if not v.get('station_access') and all(np.linalg.norm(np.array(v['position'][:2])-q['position'][:2])>3500 for q in j+st['crossings'])]+st['crossings']
for v in u['crossings']:v['signal_group']=2
reserve=wkt.loads((O/'road_reserve.wkt').read_text());u['furniture']=[v for v in u['furniture'] if not reserve.buffer(180 if v['type']=='Banca' else 75).contains(Point(v['position'][:2]))]
for path,data in [(W/'integration_plan.json',p),(O/'placement_plan.json',u),(O/'station_expansion_plan.json',st)]:path.write_text(json.dumps(data,indent=2))
print('STAGED',len(p['stations']),'stations',len(st['crossings']),'station end crossings',len(u['crossings']),'total pedestrian sites')
