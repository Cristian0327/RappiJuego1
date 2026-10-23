import json,sys,math,numpy as np
from pathlib import Path
P=Path('urban_safety');sys.path.insert(0,'urban_refresh/python_deps');from shapely import wkt
from shapely.geometry import Point,Polygon
from shapely.ops import nearest_points
walk=wkt.loads(Path('urban_corrections/unified_sidewalks.wkt').read_text());asphalt=wkt.loads(Path('urban_corrections/unified_asphalt.wkt').read_text());safe=walk.buffer(-35);rows=json.loads((P/'actual_instances.json').read_text());items=[];reserved=[]
def footprint(pos,yaw,hx,hy):
 a=math.radians(yaw);c,s=math.cos(a),math.sin(a);return Polygon([(pos[0]+c*x-s*y,pos[1]+s*x+c*y) for x,y in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]])
for row in rows:
 if row['actor']!='BP_BogotaUrbanDressing_C' or 'FarolaLuz' in row['mesh'] or not any(v in row['mesh'] for v in ['Banca','Caneca','Bolardo','Farola']):continue
 for idx,tr in enumerate(row['transforms']):
  if tr['location'][2]>65:continue
  hx,hy=(100,32) if 'Banca' in row['mesh'] else (30,30) if 'Caneca' in row['mesh'] else (12,12) if 'Bolardo' in row['mesh'] else (23,23);poly=footprint(tr['location'],tr['rotation'][2],hx,hy);item=dict(component=row['component'],index=idx,old=tr['location'],mesh=row['mesh'],yaw=tr['rotation'][2],hx=hx,hy=hy)
  if poly.buffer(8).intersection(asphalt).area>1:items.append(item)
  else:reserved.append(poly.buffer(15))
changes=[]
for item in items:
 at=np.array(item['old'][:2]);base=np.array(nearest_points(safe,Point(at))[0].coords[0]);choices=[base]+[base+[math.cos(a)*r,math.sin(a)*r] for r in range(50,1250,50) for a in np.linspace(0,2*math.pi,24,endpoint=False)];choices.sort(key=lambda p:np.linalg.norm(p-at));found=False
 for p in choices:
  poly=footprint(p,item['yaw'],item['hx'],item['hy'])
  if poly.buffer(8).intersects(asphalt) or not walk.covers(poly) or any(poly.intersects(v) for v in reserved):continue
  item['new']=[float(p[0]),float(p[1]),20];reserved.append(poly.buffer(20));changes.append(item);found=True;break
 if not found:raise RuntimeError('No safe furniture placement '+str(item))
(P/'furniture_relocations.json').write_text(json.dumps(changes,indent=2));print('VERIFIED_FURNITURE_RELOCATIONS',len(changes),'no road footprints; no overlapping relocated furniture')
