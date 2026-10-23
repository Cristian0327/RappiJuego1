exec(compile(__import__('pathlib').Path(__file__).with_name('plan_streets.py').read_text().split('rows=json.loads')[0],'setup','exec'))
from shapely import constrained_delaunay_triangles,wkt
from shapely.geometry import MultiPoint
from scipy.spatial import cKDTree
foot=pickle.loads((P/'footprint_cache.pkl').read_bytes());moves={v['source']:np.array(v['delta_cm']) for v in json.loads((P/'building_moves.json').read_text())};m=json.loads((R/'urban_safety/leveled_manifest.json').read_text());roads=json.loads((P/'streets.json').read_text())['secondary_roads'];actors=json.loads((P/'actors.json').read_text());shops=json.loads((P/'actual_shops.json').read_text());shape=(1000,800);origin=np.array([-40000,-50000])
def raster(poly,res=100):
 im=Image.new('1',(int(80000/res),int(100000/res)));d=ImageDraw.Draw(im)
 for p in [poly] if poly.geom_type=='Polygon' else poly.geoms:
  if p.is_empty:continue
  d.polygon([tuple((np.array(q)-origin)/res) for q in p.exterior.coords],fill=1)
  for ring in p.interiors:d.polygon([tuple((np.array(q)-origin)/res) for q in ring.coords],fill=0)
 return np.array(im)
def ribbon(r,key):
 c=np.array(r['center'])*[100,-100,100];s=np.array(r['side'])*[1,-1,1];w=np.array(r[key])*100;l=c[:,:2]+s[:,:2]*w[:,None];rt=c[:,:2]-s[:,:2]*w[:,None]
 return unary_union([Polygon([l[i],rt[i],rt[i+1],l[i+1]]).buffer(0) for i in range(len(c)-1)])
mainp=[ribbon(r,'innerwidth') for r in m['roads']];maino=[ribbon(r,'halfwidth') for r in m['roads']];secondaryp=unary_union([LineString(r['samples']).buffer(240,quad_segs=16) for r in roads]);secondaryo=unary_union([LineString(r['samples']).buffer(380,quad_segs=16) for r in roads]);asphalt=unary_union(mainp+[secondaryp]);outer=unary_union(maino+[secondaryo]);reserve=secondaryo.buffer(60);roadmask=raster(outer);occ=np.zeros(shape,np.int16)
for f in foot:
 if f['tall'] is None:continue
 yy,xx=f['tall'];delta=moves.get(f['source'],np.zeros(2)).astype(int)//100;occ[np.clip(yy+delta[1],0,999),np.clip(xx+delta[0],0,799)]+=1
flat=np.load(R/'compact_city/original_terrain_heights_2m.npy');flat=np.array(Image.fromarray(np.nan_to_num(flat,nan=99999).astype(np.float32)).resize((800,1000),Image.Resampling.BILINEAR));flatok=abs(flat)<35;shopmask=np.zeros(shape,bool);newshopmask=np.zeros(shape,bool);unmovable=np.zeros(shape,bool)
for f in foot:
 if f['tall'] is not None and len(f['tall'][0])>500:
  yy,xx=f['tall'];delta=moves.get(f['source'],np.zeros(2)).astype(int)//100;unmovable[np.clip(yy+delta[1],0,999),np.clip(xx+delta[0],0,799)]=True
def shop_polygon(s):
 yaw=math.radians(s['yaw']);t=np.array([math.cos(yaw),math.sin(yaw)]);b=np.array([-t[1],t[0]]);p=np.array(s['entrance'][:2]);return Polygon([p+t*x+b*y for x,y in [(-1350,-100),(1350,-100),(1350,3400),(-1350,3400)]])
for s in shops:
 if s['conflict']<=1:shopmask|=raster(shop_polygon(s))
for s in shops:
 if s['conflict']<=1:continue
 poly=shop_polygon(s);mask=raster(poly);yy,xx=np.where(mask);y0=int(yy.min());x0=int(xx.min());kernel=np.zeros((np.ptp(yy)+1,np.ptp(xx)+1),np.float32);kernel[yy-y0,xx-x0]=1;bad=roadmask|shopmask|unmovable|~flatok;score=fftconvolve(bad.astype(np.float32),kernel[::-1,::-1],mode='valid');load=fftconvolve((occ>0).astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(score<.15);assert len(xs),s['name'];ds=(ys-y0)**2+(xs-x0)**2;k=int(np.argmin(np.sqrt(ds)+load[ys,xs]*.03));delta=np.array([int(xs[k]-x0)*100,int(ys[k]-y0)*100]);s['original_entrance']=s['entrance'];s['entrance']=[s['entrance'][0]+int(delta[0]),s['entrance'][1]+int(delta[1]),20];s['delta_cm']=delta.tolist();mask=raster(shop_polygon(s));shopmask|=mask;newshopmask|=mask;print('SHOP_MOVE',s['name'],delta.tolist(),flush=True)
extra=[]
for f in foot:
 if f['tall'] is None:continue
 yy,xx=f['tall'];delta=moves.get(f['source'],np.zeros(2)).astype(int)//100;ay=np.clip(yy+delta[1],0,999);ax=np.clip(xx+delta[0],0,799)
 if np.any(newshopmask[ay,ax]):extra.append(f);occ[ay,ax]-=1
for f in sorted(extra,key=lambda f:-len(f['tall'][0])):
 yy,xx=f['tall'];y0=int(yy.min());x0=int(xx.min());kernel=np.zeros((np.ptp(yy)+1,np.ptp(xx)+1),np.float32);kernel[yy-y0,xx-x0]=1;bad=(occ>0)|roadmask|shopmask|~flatok;score=fftconvolve(bad.astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(score<.15);assert len(xs),f['source'];delta0=moves.get(f['source'],np.zeros(2))/100;ds=(ys-y0-delta0[1])**2+(xs-x0-delta0[0])**2;k=int(np.argmin(ds));dy=int(ys[k]-y0);dx=int(xs[k]-x0);moves[f['source']]=np.array([dx*100,dy*100]);occ[yy+dy,xx+dx]+=1
print('ADDITIONAL_SHOP_CLEARANCE_BUILDINGS',len(extra),flush=True)
(P/'final_building_moves.json').write_text(json.dumps([dict(source=k,delta_cm=v.tolist(),distance_m=float(np.linalg.norm(v)/100)) for k,v in moves.items()]))
# Actual access walks join the same sidewalk network without crossing architecture.
from scipy.ndimage import label
from heapq import heappop,heappush
walkpoly=outer.difference(asphalt);free=(occ==0)&flatok&~raster(asphalt);walkmask=raster(walkpoly)&free;ys,xs=np.where(walkmask);tree=cKDTree(np.column_stack([ys,xs]));links=[]
for s in shops:
 yaw=math.radians(s['yaw']);back=np.array([-math.sin(yaw),math.cos(yaw)]);door=np.array(s['entrance'][:2])-back*150;start=tuple(np.rint(((door-origin)/100)[::-1]).astype(int));goal=tuple(tree.data[tree.query(start)[1]].astype(int));queue=[(0,start)];cost={start:0};prev={};found=False
 while queue:
  _,x=heappop(queue)
  if x==goal:found=True;break
  for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
   y=(x[0]+dy,x[1]+dx)
   if not(0<=y[0]<1000 and 0<=y[1]<800 and free[y]) or (dx and dy and not(free[x[0]+dy,x[1]] and free[x[0],x[1]+dx])):continue
   ng=cost[x]+math.hypot(dx,dy)
   if ng<cost.get(y,1e30):cost[y]=ng;prev[y]=x;heappush(queue,(ng+math.dist(y,goal),y))
 if not found:raise RuntimeError('No walking access '+s['name'])
 path=[goal]
 while path[-1]!=start:path.append(prev[path[-1]])
 q=[(np.array(p[::-1])*100+origin).tolist() for p in path[::-1]];q=[door.tolist()]+q+[list(LineString(list(walkpoly.exterior.coords)).interpolate(0).coords[0])] if False else [door.tolist()]+q
 line=LineString(q).simplify(35);s['walk_link']=[[*p,20] for p in line.coords];links.append(line.buffer(100,join_style=1))
outer=unary_union([outer]+links);walk=outer.difference(asphalt);assert asphalt.geom_type=='Polygon'
for it in m['instances']:
 delta=moves.get(it['source'])
 if delta is not None:
  it['location'][0]+=float(delta[0])/100;it['location'][1]-=float(delta[1])/100
  for b in it.get('bounds',[]):b[0]+=float(delta[0])/100;b[1]-=float(delta[1])/100
# Roads that intersect share identical grades at their intersection; main roads stay at their existing datum.
mainnet=unary_union(mainp)
for r in roads:
 q=np.array(r['samples']);z=np.array(r['heights_cm']);dist=np.array([mainnet.distance(Point(p)) for p in q]);z*=np.clip(dist/800,0,1);r['heights_cm']=z.tolist()
for repeat in range(3):
 for i,a in enumerate(roads):
  la=LineString(a['samples']);ta=cKDTree(a['samples'])
  for b in roads[i+1:]:
   inter=la.intersection(LineString(b['samples']));points=[inter] if inter.geom_type=='Point' else list(inter.geoms) if inter.geom_type=='MultiPoint' else []
   for pt in points:
    ia=int(ta.query(pt.coords[0])[1]);ib=int(cKDTree(b['samples']).query(pt.coords[0])[1]);z=min(a['heights_cm'][ia],b['heights_cm'][ib]);a['heights_cm'][ia]=z;b['heights_cm'][ib]=z
 for r in roads:
  q=np.array(r['samples']);z=np.array(r['heights_cm']);ds=np.linalg.norm(np.diff(q,axis=0),axis=1)
  for i in range(1,len(z)):z[i]=min(z[i],z[i-1]+.20*ds[i-1])
  for i in range(len(z)-2,-1,-1):z[i]=min(z[i],z[i+1]+.20*ds[i])
  r['heights_cm']=z.tolist()
xyz=np.concatenate([np.column_stack([r['samples'],r['heights_cm']]) for r in roads]);ztree=cKDTree(xyz[:,:2]);mainpoints=np.concatenate([np.array(r['center'])*[100,-100,100] for r in m['roads']]);mtree=cKDTree(mainpoints[:,:2])
def heights(points):
 pts=np.array(points);dist,idx=ztree.query(pts);z=xyz[idx,2];inside=np.array([mainnet.covers(Point(p)) for p in pts]);z[inside]=0;return z
meshes=[]
def begin(name):return dict(name=name,verts=[],faces=[],colors=[])
def face(o,pts,col):
 i=len(o['verts']);o['verts'] += [(float(x/100),float(-y/100),float(z/100)) for x,y,z in pts];o['faces'].append(list(reversed(range(i,i+len(pts)))));o['colors'].append(col)
def flat(o,poly,offset,color):
 if poly.is_empty:return
 for tri in constrained_delaunay_triangles(poly).geoms:
  q=np.array(list(tri.exterior.coords)[:3]);z=heights(q)+offset;face(o,np.column_stack([q,z]),color)
def edges(o,poly):
 for p in [poly] if poly.geom_type=='Polygon' else poly.geoms:
  for ring in [p.exterior]+list(p.interiors):
   q=np.array(ring.coords);z=heights(q)
   for i,(a,b) in enumerate(zip(q,q[1:])):face(o,[(a[0],a[1],z[i]),(b[0],b[1],z[i+1]),(b[0],b[1],z[i+1]+20),(a[0],a[1],z[i]+20)],[.38,.32,.24,1])
ap=Polygon();aw=Polygon()
for i,(p,o) in enumerate(zip(mainp,maino)):
 spec=begin('SM_Mapa_Road_'+str(i));part=p.difference(ap);side=walk.intersection(o).difference(aw);flat(spec,part,4,[.12,.15,.17,1]);flat(spec,side,20,[.68,.69,.66,1]);edges(spec,side);meshes.append(spec);ap=unary_union([ap,part]);aw=unary_union([aw,side])
spec=begin('SM_Bogota_CallesSecundarias');part=asphalt.difference(ap);side=walk.difference(aw);flat(spec,part,4,[.12,.15,.17,1]);flat(spec,side,20,[.55,.36,.18,1]);edges(spec,side)
for r in roads:
 line=LineString(r['samples'])
 for t in np.arange(400,line.length-400,900):flat(spec,LineString([line.interpolate(t),line.interpolate(t+280)]).buffer(5,cap_style=2).intersection(part),4.7,[.8,.6,.08,1])
meshes.append(spec)
(P/'road_meshes.json').write_text(json.dumps(meshes));(P/'manifest.json').write_text(json.dumps(m));(P/'shops.json').write_text(json.dumps(shops));(P/'streets.json').write_text(json.dumps(dict(secondary_roads=roads)));(P/'asphalt.wkt').write_text(asphalt.wkt);(P/'sidewalks.wkt').write_text(walk.wkt);(P/'outer.wkt').write_text(outer.wkt);np.save(P/'road_grade_samples.npy',xyz);np.save(P/'clip_mask.npy',raster(outer.buffer(20),20));Image.fromarray((raster(outer,100)*255).astype(np.uint8)).save(P/'ground_priority.png');print('V2_UNIFIED_GEOMETRY_READY',[(s['name'],len(s['faces'])) for s in meshes],flush=True)
