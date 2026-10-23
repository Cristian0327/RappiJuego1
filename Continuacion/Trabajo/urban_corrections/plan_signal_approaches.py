import json,numpy as np,math,sys
from pathlib import Path
U=Path(__file__).resolve().parent;O=U.parent/'urban_refresh';sys.path.insert(0,str(O/'python_deps'));from shapely import wkt;from shapely.geometry import Polygon
asphalt=wkt.loads((U/'unified_asphalt.wkt').read_text());plan=json.loads((O/'placement_plan.json').read_text());junctions=json.loads((U/'junction_plan.json').read_text());axes=[];heads=[];verts=[];faces=[];cols=[]
def paint(poly):
 g=poly.intersection(asphalt)
 from shapely import constrained_delaunay_triangles
 for tri in constrained_delaunay_triangles(g).geoms:
  i=len(verts);verts.extend([(x/100,-y/100,.048) for x,y in list(tri.exterior.coords)[:3]]);faces.append([i+2,i+1,i]);cols.append([.85,.83,.73,1])
for ji,j in enumerate(junctions):
 for group,v in enumerate(j['axes']):
  t=np.array(v);rr=np.array([-t[1],t[0]]);q=np.array(j['position'][:2]);main=group==0 or j['kind']=='principal_principal';half=1288 if main else 350;outer=1528 if main else 570;stop=1900 if group==1 or j['kind']=='principal_principal' else 950
  axes.append(dict(position=j['position'],forward=[*v,0],signal_group=group,road_width=half+150,stop_offset=stop,junction_id=ji))
  for sign in [-1,1]:
   pos=q-t*sign*stop+rr*sign*(outer+60);heads.append(dict(position=[*pos.tolist(),20],yaw=math.degrees(math.atan2(t[1],t[0]))+(180 if sign<0 else 0),signal_group=group,junction_id=ji))
   a=q-t*sign*stop;paint(Polygon([a+rr*(sign*x)+t*z for x,z in [(0,-12),(half,-12),(half,12),(0,12)]]))
   center=q-t*sign*(stop-250)
   for lateral in np.arange(-half+40,half-40,90):paint(Polygon([center+t*x+rr*y for x,y in [(-120,lateral),(-120,lateral+42),(120,lateral+42),(120,lateral)]]))
for cr in plan['crossings']:axes.append(dict(position=cr['position'],forward=cr['forward'],signal_group=2,road_width=cr['halfwidth']+100,stop_offset=950))
(U/'signal_approach_plan.json').write_text(json.dumps(dict(approaches=axes,heads=heads,junction_count=len(junctions),pedestrian_sites=len(plan['crossings'])),indent=2));(U/'junction_marking_geometry.json').write_text(json.dumps(dict(name='SM_Bogota_MarcasInterseccion',verts=verts,faces=faces,colors=cols)));print('SIGNALS',len(heads)+len(plan['crossings'])*2,'JUNCTIONS',len(junctions),'APPROACHES',len(axes))
