import json,sys,math,pickle
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path,connected_components
P=Path(__file__).resolve().parent;R=P.parent;sys.path.insert(0,str(R/'urban_refresh/python_deps'))
from shapely import wkt
from shapely.geometry import LineString,Point,Polygon
from shapely.ops import unary_union,nearest_points
m=json.loads((P/'manifest.json').read_text());roads=json.loads((P/'streets.json').read_text())['secondary_roads'];shops=json.loads((P/'shops.json').read_text());asphalt=wkt.loads((P/'asphalt.wkt').read_text());walk=wkt.loads((P/'sidewalks.wkt').read_text());outer=wkt.loads((P/'outer.wkt').read_text());actual_lanes=json.loads((P/'actual_lanes.json').read_text());lines=[LineString([q[:2] for q in r]+[r[0][:2]]) for r in actual_lanes[:4]]+[LineString((np.array(r['center'])*[100,-100,100])[:,:2]) for r in m['roads'][1:]];station_polys=[]
for a in json.loads((P/('actors_final.json' if (P/'actors_final.json').exists() else 'actors.json')).read_text()):
 if a['cls']!='BP_BogotaTransmiStation_C':continue
 angle=math.radians(a['rotation'][1]);t=np.array([math.cos(angle),math.sin(angle)]);n=np.array([-t[1],t[0]]);c=np.array(a['position'][:2]);length=1212.5 if a['name'].endswith('_2') else 2425;station_polys.append(Polygon([c+t*x+n*y for x,y in [(-length,-230),(length,-230),(length,230),(-length,230)]]))
obstacles=unary_union(station_polys).buffer(70)
def paved(seg):return outer.buffer(150).covers(seg) and not obstacles.intersects(seg)
lines=[part for line in lines for part in ([line.difference(obstacles)] if line.difference(obstacles).geom_type=='LineString' else line.difference(obstacles).geoms) if part.length>.1];network=unary_union(lines)
for r in roads:
 line=LineString(r['samples']);a,b=nearest_points(line,network)
 if a.distance(b)>.1:
  connector=LineString([a,b]);assert outer.buffer(50).covers(connector),('Road connector leaves paving',r['name'],a.distance(b));lines.append(connector)
 pieces=line.difference(obstacles);lines.extend([pieces] if pieces.geom_type=='LineString' else list(pieces.geoms));network=unary_union(lines)
for s in shops:
 line=LineString([p[:2] for p in s['walk_link']]);a,b=nearest_points(line,network);connector=LineString([a,b]);assert outer.buffer(150).covers(connector),('Shop connector',s['name']);lines.extend([line,connector,LineString([line.coords[0],s['entrance'][:2]])]);network=unary_union(lines)
foot=pickle.loads((P/'footprint_cache.pkl').read_bytes());moves={v['source']:np.array(v['delta_cm']) for v in json.loads((P/'final_building_moves.json').read_text())};occ=np.zeros((1000,800),bool);origin=np.array([-40000,-50000])
for f in foot:
 for key in ['low','tall']:
  if f[key] is not None:
   yy,xx=f[key];delta=moves.get(f['source'],np.zeros(2)).astype(int)//100;occ[np.clip(yy+delta[1],0,999),np.clip(xx+delta[0],0,799)]=True
im=Image.new('1',(800,1000));dr=ImageDraw.Draw(im)
for poly in [walk] if walk.geom_type=='Polygon' else walk.geoms:
 dr.polygon([tuple((np.array(p)-origin)/100) for p in poly.exterior.coords],fill=1)
 for ring in poly.interiors:dr.polygon([tuple((np.array(p)-origin)/100) for p in ring.coords],fill=0)
free=np.array(im)&(distance_transform_edt(~occ)>1.0);yy,xx=np.where(free);points=np.column_stack([xx,yy])*100+origin;grade=np.load(P/'road_grade_samples.npy');grade_tree=cKDTree(grade[:,:2]);points=points[grade[grade_tree.query(points)[1],2]<30];tree=cKDTree(points);candidates=[]
for it in m['instances']:
 if it['source'].startswith('SM_Mapa_Road') or 'Relieve' in it['source']:continue
 q=np.array(it['location'][:2])*[100,-100];dist,k=tree.query(q);p=points[k]
 if dist>2200:continue
 if min(np.linalg.norm(p-np.array(s['entrance'][:2])) for s in shops)<1400:continue
 candidates.append(dict(source=it['source'],point=[float(p[0]),float(p[1]),20.],distance_to_house_cm=float(dist)))
# Keep well-distributed, distinct houses; all recipients stand on reachable pavement.
homes=[]
while candidates and len(homes)<100:
 best=max(range(len(candidates)),key=lambda i:min(np.linalg.norm(np.array(candidates[i]['point'][:2])-np.array(h['point'][:2])) for h in homes) if homes else -candidates[i]['distance_to_house_cm']);row=candidates.pop(best)
 if homes and min(math.dist(row['point'],h['point']) for h in homes)<600:continue
 homes.append(row)
validhomes=[]
for h in homes:
 a,b=nearest_points(Point(h['point'][:2]),network);connector=LineString([a,b])
 if not paved(connector):continue
 lines.append(connector);validhomes.append(h)
homes=validhomes;assert len(homes)>60,len(homes)
network=unary_union(lines);nodes=[];lookup={};edge=[]
def node(q):
 key=(round(q[0],2),round(q[1],2))
 if key not in lookup:lookup[key]=len(nodes);nodes.append([*key,6.])
 return lookup[key]
pieces=list(network.geoms) if hasattr(network,'geoms') else [network]
for line in pieces:
 if line.length<.01:continue
 # Keep original curve samples at bends while removing redundant near-collinear points.
 line=line.simplify(35,preserve_topology=True);ds=np.linspace(0,line.length,max(2,math.ceil(line.length/650)+1));q=[line.interpolate(t).coords[0] for t in ds]
 for a,b in zip(q,q[1:]):
  ia=node(a);ib=node(b)
  if ia!=ib:edge.append((ia,ib,float(math.dist(a,b))))
N=len(nodes);ii=[];jj=[];ww=[]
for a,b,w in edge:ii.extend([a,b]);jj.extend([b,a]);ww.extend([w,w])
graph=csr_matrix((ww,(ii,jj)),shape=(N,N));components,labels=connected_components(graph);stitched=0
while components>1:
 best=None;coords=np.array(nodes)[:,:2]
 for label in range(components):
  own=np.where(labels==label)[0];other=np.where(labels!=label)[0];tree=cKDTree(coords[other]);ds,at=tree.query(coords[own]);order=np.argsort(ds)
  for k in order[:30]:
   a=int(own[k]);b=int(other[at[k]]);length=float(ds[k])
   if length>800:break
   if not paved(LineString([nodes[a][:2],nodes[b][:2]])):continue
   if best is None or length<best[0]:best=(length,a,b)
   break
 if best is None:raise RuntimeError(('Disconnected physical street graph',components))
 length,a,b=best;edge.append((a,b,max(.01,length)));ii.extend([a,b]);jj.extend([b,a]);ww.extend([max(.01,length)]*2);graph=csr_matrix((ww,(ii,jj)),shape=(N,N));components,labels=connected_components(graph);stitched+=1
dist,pred=shortest_path(graph,directed=False,return_predecessors=True);nexthop=np.full((N,N),-1,np.int32)
for goal in range(N):nexthop[:,goal]=pred[goal,:];nexthop[goal,goal]=goal
assert np.all(nexthop>=0)
# Validate sample paths against the actual paved mesh footprint.
bad=[]
for a,b,w in edge:
 seg=LineString([nodes[a][:2],nodes[b][:2]])
 if not outer.buffer(160).covers(seg) or obstacles.buffer(-1).intersects(seg):bad.append((a,b,w))
assert not bad,('Navigation edge leaves physical pavement',bad[:5])
(P/'road_navigation_network.json').write_text(json.dumps(dict(nodes=nodes,next_hop=nexthop.ravel().tolist(),count=N,unreachable_pairs=0)));(P/'homes.json').write_text(json.dumps(homes,indent=2));(P/'navigation_edges.json').write_text(json.dumps(edge));(P/'navigation_report.json').write_text(json.dumps(dict(nodes=N,edges=len(edge),homes=len(homes),shops=len(shops),street_sources=len(roads),components=components,physical_path_errors=len(bad)),indent=2));print('V2_NAVIGATION_NETWORK_READY',N,len(edge),len(homes),flush=True)
