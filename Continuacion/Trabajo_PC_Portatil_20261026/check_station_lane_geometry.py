import sys,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'python_deps'))
from shapely.geometry import Polygon,LineString
src=P.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
a=json.loads((src/'actors_final.json').read_text());lanes=json.loads((src/'actual_lanes.json').read_text());rows=[]
for st in a:
 if st['cls']!='BP_BogotaTransmiStation_C':continue
 yaw=math.radians(st['rotation'][1]);c,s=math.cos(yaw),math.sin(yaw);x,y=st['position'][:2]
 for compact in ([False,True] if st['name'].endswith('_2') else [False]):
  hl=1212.5 if compact else 2425;hw=180.75; poly=Polygon([(x+c*u-s*v,y+s*u+c*v) for u,v in [(-hl,-hw),(-hl,hw),(hl,hw),(hl,-hw)]])
  row=dict(station=st['name'],compact=compact,lanes=[])
  for i,points in enumerate(lanes):
   path=LineString(points+[points[0]]);hits=[k for k in range(len(points)) if LineString([points[k],points[(k+1)%len(points)]]).distance(poly)<70]
   row['lanes'].append(dict(lane=i,distance_cm=round(path.distance(poly),2),sphere70_near_segments=hits))
  rows.append(row)
(P/'station_lane_geometry.json').write_text(json.dumps(rows,indent=2));print([(r['station'],r['compact'],[(x['lane'],x['distance_cm'],len(x['sphere70_near_segments'])) for x in r['lanes']]) for r in rows])