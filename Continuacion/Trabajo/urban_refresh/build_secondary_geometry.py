import sys,json,numpy as np,math
from pathlib import Path
U=Path(__file__).parent;sys.path.insert(0,str(U/'python_deps'))
from shapely.geometry import LineString,Polygon,Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=U.parent/'new_map_audit';m=json.loads((W/'manifest.json').read_text());p=json.loads((W/'integration_plan.json').read_text());plan=json.loads((U/'secondary_road_plan.json').read_text());lines=[LineString(s['samples']).simplify(80) for s in plan['secondary_roads']];asphalt=unary_union([s.buffer(350,cap_style=2,join_style=2) for s in lines]);reserve=unary_union([s.buffer(570,cap_style=2,join_style=2) for s in lines]);main=[];mainouter=[]
for road in m['roads']:
 c=np.array(road['center'])*[100,-100,100];line=LineString(c[:,:2]);main.append(line.buffer(float(np.median(road['innerwidth'])*100),cap_style=2));mainouter.append(line.buffer(float(np.median(road['halfwidth'])*100),cap_style=2))
main=unary_union(main);mainouter=unary_union(mainouter);walk=reserve.difference(asphalt).difference(mainouter);newasphalt=asphalt.difference(main)
meshes=[]
def begin(name):return dict(name=name,verts=[],faces=[],colors=[])
def face(o,pts,col):
 i=len(o['verts']);o['verts']+=[(float(q[0]/100),float(-q[1]/100),float(q[2]/100)) for q in pts];o['faces'].append(list(range(i,i+len(pts))));o['colors'].append(col)
def flat(o,poly,z,col):
 if poly.is_empty:return
 for tri in constrained_delaunay_triangles(poly).geoms:
  pts=[(x,y,z) for x,y in list(tri.exterior.coords)[:3]]
  face(o,list(reversed(pts)) if o['name'].startswith('SM_Mapa') else pts,col)
o=begin('SM_Bogota_CallesSecundarias');flat(o,newasphalt,4,[.12,.15,.17,1]);flat(o,walk,20,[.55,.36,.18,1])
# Solid curb walls and side faces make the road reserve tangible from every angle.
for poly in ([walk] if walk.geom_type=='Polygon' else walk.geoms):
 if poly.is_empty:continue
 for ring in [poly.exterior]+list(poly.interiors):
  for a,b in zip(ring.coords,list(ring.coords)[1:]):face(o,[(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],20),(a[0],a[1],20)],[.38,.26,.15,1])
# Broken centerline is clipped to the actual secondary asphalt and omitted at main-road junctions.
for line in lines:
 for t in np.arange(300,line.length-300,900):
  a=line.interpolate(t);b=line.interpolate(min(t+300,line.length));mark=LineString([a,b]).buffer(6,cap_style=2).intersection(newasphalt);flat(o,mark,4.8,[.8,.6,.08,1])
meshes.append(o)
# Remove only original raised sidewalks/curbs at the new road mouths; asphalt stays intact.
cut=asphalt.buffer(10)
for src in json.loads((U/'road_mesh_source.json').read_text()):
 o=begin(src['name']);v=np.array(src['verts'])*[100,-100,100]
 for inds,col in zip(src['faces'],src['colors']):
  pts=v[inds];poly=Polygon(pts[:,:2]).buffer(0);mid=pts.mean(axis=0)
  if np.max(pts[:,2])<10 or not cut.intersects(poly if poly.area>.1 else Point(*mid[:2])):face(o,pts,col);continue
  if poly.area<.1:
   if not cut.contains(Point(*mid[:2])):face(o,pts,col)
  else:flat(o,poly.difference(cut),float(np.max(pts[:,2])),col)
 meshes.append(o)
(U/'secondary_geometry.json').write_text(json.dumps(meshes));(U/'road_reserve.wkt').write_text(reserve.wkt);(U/'secondary_network.wkt').write_text(unary_union(lines).wkt)
print('ROAD_GEOMETRY_READY',[(o['name'],len(o['faces'])) for o in meshes]);print('NETWORK_COMPONENTS',len(unary_union(lines).geoms))

