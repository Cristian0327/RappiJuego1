import json,sys,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'urban_refresh/python_deps'))
from shapely import wkt
from shapely.geometry import Point,LineString
from shapely.ops import nearest_points
data=json.loads((P/'arc_conflicts.json').read_text());lanes=json.loads((P/'actual_lanes.json').read_text());walk=wkt.loads((P/'sidewalks.wkt').read_text());safe=walk.buffer(-45);heads=[]
for li,row in enumerate(data['lanes']):
 if li in [4,5]:continue
 line=LineString([p[:2] for p in lanes[li]]+[lanes[li][0][:2]])
 for e in row['events']:
  p=np.array(line.interpolate((e['entry']-680)%line.length).coords[0]);direction=np.array(e['direction'])
  if any(np.linalg.norm(p-np.array(h['stop']))<350 and np.dot(direction,h['direction'])>.8 for h in heads):continue
  a,b=nearest_points(Point(p),safe);q=np.array(b.coords[0]);heads.append(dict(position=[float(q[0]),float(q[1]),20],stop=p.tolist(),direction=direction.tolist(),yaw=math.degrees(math.atan2(direction[1],direction[0]))+180,signal_group=e['group'],junction=e['junction']))
(P/'signal_heads.json').write_text(json.dumps(heads,indent=2));area=wkt.loads((P/'outer.wkt').read_text()).buffer(-25);im=Image.new('L',(4096,5120));dr=ImageDraw.Draw(im)
def coords(r):return [((x+40000)/80000*4096,(y+50000)/100000*5120) for x,y in r.coords]
for poly in [area] if area.geom_type=='Polygon' else area.geoms:
 dr.polygon(coords(poly.exterior),fill=255)
 for ring in poly.interiors:dr.polygon(coords(ring),fill=0)
im.save(P/'T_UrbanGroundPriority.png');print('V2_SIGNAL_HEADS_AND_GROUND_MASK',len(heads))
