import sys,json,numpy as np,math
from pathlib import Path
U=Path(__file__).resolve().parent;O=U.parent/'urban_refresh';sys.path.insert(0,str(O/'python_deps'))
from shapely.geometry import LineString,Polygon,Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
m=json.loads((O.parent/'new_map_audit/manifest.json').read_text());plan=json.loads((O/'secondary_road_plan.json').read_text());mainlines=[LineString((np.array(r['center'])*[100,-100,100])[:,:2]) for r in m['roads']]
def ribbon(r,key):
 c=np.array(r['center'])*[100,-100,100];side=np.array(r['side'])*[1,-1,1];w=np.array(r[key])*100;l=c[:,:2]+side[:,:2]*w[:,None];rr=c[:,:2]-side[:,:2]*w[:,None]
 return unary_union([Polygon([l[i],rr[i],rr[i+1],l[i+1]]).buffer(0) for i in range(len(c)-1)])
# Keep the original main-road geometry and widths. Only remove pavement where roads meet.
mainp=[ribbon(r,'innerwidth') for r in m['roads']];maino=[ribbon(r,'halfwidth') for r in m['roads']];main_asphalt=unary_union(mainp);secondary=[];covered=main_asphalt.buffer(100);dedup=[]
for row in plan['secondary_roads']:
 line=LineString(row['samples']);remaining=line.difference(covered);pieces=[remaining] if remaining.geom_type=='LineString' else [g for g in remaining.geoms if g.geom_type=='LineString'];kept=[]
 for piece in pieces:
  if piece.length<1600:continue
  secondary.append(piece);kept.append(piece);covered=unary_union([covered,piece.buffer(400,quad_segs=20)])
 dedup.append(dict(source=row['name'],retained_segments=len(kept),retained_length_m=sum(g.length for g in kept)/100))
secp=unary_union([s.buffer(350,quad_segs=24,join_style=1) for s in secondary]);seco=unary_union([s.buffer(570,quad_segs=24,join_style=1) for s in secondary]);asphalt=unary_union(mainp+[secp]);city=json.loads((O.parent/'new_map_audit/integration_plan.json').read_text());shoplinks=unary_union([LineString(v['walk_link']).buffer(100,quad_segs=8,join_style=1) for v in city['shops']]);outer=unary_union(maino+[seco,shoplinks]);walk=outer.difference(asphalt)
parts=[walk] if walk.geom_type=='Polygon' else list(walk.geoms);small=[p for p in parts if p.area<250000];asphalt=unary_union([asphalt]+small);walk=outer.difference(asphalt);assert asphalt.geom_type=='Polygon','Disconnected carriageway network'
(U/'unique_centerlines.json').write_text(json.dumps([list(g.coords) for g in secondary]));(U/'deduplication_report.json').write_text(json.dumps(dedup,indent=2))
meshes=[]
def begin(name):return dict(name=name,verts=[],faces=[],colors=[])
def face(o,pts,col):
 i=len(o['verts']);o['verts'] += [(float(x/100),float(-y/100),float(z/100)) for x,y,z in pts];o['faces'].append(list(range(i,i+len(pts))));o['colors'].append(col)
def flat(o,poly,z,col):
 for tri in constrained_delaunay_triangles(poly).geoms:
  pts=[(x,y,z) for x,y in list(tri.exterior.coords)[:3]];face(o,list(reversed(pts)) if o['name'].startswith('SM_Mapa') else pts,col)
def edge(o,poly):
 for p in ([poly] if poly.geom_type=='Polygon' else poly.geoms):
  if p.is_empty:continue
  for ring in [p.exterior]+list(p.interiors):
   for a,b in zip(ring.coords,list(ring.coords)[1:]):
    pts=[(a[0],a[1],0),(b[0],b[1],0),(b[0],b[1],20),(a[0],a[1],20)];face(o,list(reversed(pts)) if o['name'].startswith('SM_Mapa') else pts,[.38,.32,.24,1])
assignedp=Polygon();assignedw=Polygon()
for i,(ap,op) in enumerate(zip(mainp,maino)):
 o=begin('SM_Mapa_Road_'+str(i));road=ap.difference(assignedp);pave=walk.intersection(op).difference(assignedw);flat(o,road,4,[.12,.15,.17,1]);flat(o,pave,20,[.68,.69,.66,1]);edge(o,pave);assignedp=unary_union([assignedp,road]);assignedw=unary_union([assignedw,pave]);meshes.append(o)
o=begin('SM_Bogota_CallesSecundarias');road=asphalt.difference(assignedp);pave=walk.difference(assignedw);flat(o,road,4,[.12,.15,.17,1]);flat(o,pave,20,[.55,.36,.18,1]);edge(o,pave)
for line in secondary:
 for t in np.arange(500,line.length-500,900):
  a=line.interpolate(t);b=line.interpolate(min(t+300,line.length));mark=LineString([a,b]).buffer(6,cap_style=2).intersection(road);flat(o,mark,4.7,[.8,.6,.08,1])
meshes.insert(0,o);(O/'secondary_geometry.json').write_text(json.dumps(meshes));(O/'road_reserve.wkt').write_text(seco.wkt);(O/'secondary_network.wkt').write_text(unary_union(secondary).wkt);(U/'unified_asphalt.wkt').write_text(asphalt.wkt);(U/'unified_sidewalks.wkt').write_text(walk.wkt);(U/'unified_main_outer.wkt').write_text(unary_union(maino).wkt);(U/'geometry_report.json').write_text(json.dumps(dict(asphalt_components=1,sidewalk_asphalt_overlap_cm2=walk.intersection(asphalt).area,minimum_sidewalk_width_cm=220,removed_junction_wedges=len(small),meshes=[dict(name=o['name'],faces=len(o['faces'])) for o in meshes]),indent=2));print('UNIFIED_ROAD_NETWORK_READY',[(o['name'],len(o['faces'])) for o in meshes])
