import json,sys,math,pickle
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes,distance_transform_edt,map_coordinates,gaussian_filter1d
from scipy.signal import fftconvolve
R=Path(__file__).resolve().parent.parent;P=R/'map_adaptation_v2';sys.path.insert(0,str(R/'urban_refresh/python_deps'))
from shapely.geometry import LineString,Polygon,Point,box
from shapely.ops import unary_union,nearest_points
rows=json.loads((P/'authored_streets_ground.json').read_text());m=json.loads((R/'urban_safety/leveled_manifest.json').read_text());origin=np.array([-40000,-50000]);shape=(1000,800)
roads=[]
for r in rows:
 q=np.array(r['samples'])[:,:2];z=np.array(r['terrain_heights'],float);z=np.maximum(z,0);z=gaussian_filter1d(z,8);ds=np.linalg.norm(np.diff(q,axis=0),axis=1)
 for repeat in range(3):
  for i in range(1,len(z)):z[i]=min(z[i],z[i-1]+.19*ds[i-1])
  for i in range(len(z)-2,-1,-1):z[i]=min(z[i],z[i+1]+.19*ds[i])
 roads.append(dict(name=r['name'],samples=q.tolist(),heights_cm=z.tolist(),width=480,sidewalk=140))
reserve=unary_union([LineString(r['samples']).buffer(440) for r in roads])
def raster(poly):
 im=Image.new('1',(800,1000));d=ImageDraw.Draw(im)
 for p in [poly] if poly.geom_type=='Polygon' else poly.geoms:
  if p.is_empty:continue
  d.polygon([tuple((np.array(q)-origin)/100) for q in p.exterior.coords],fill=1)
  for ring in p.interiors:d.polygon([tuple((np.array(q)-origin)/100) for q in ring.coords],fill=0)
 return np.array(im)
roadmask=raster(reserve)
cache=P/'footprint_cache.pkl'
if cache.exists():foot=pickle.loads(cache.read_bytes())
else:
 sections=json.loads((P/'current_building_sections.json').read_text());foot=[]
 for row in sections:
  out=dict(source=row['source'],mesh=row['mesh'])
  for key in ['low','tall']:
   polys=row['polygons'][key]
   if not polys:out[key]=None;continue
   pts=np.concatenate(polys);lo=np.floor((pts.min(0)-origin)/100).astype(int)-1;hi=np.ceil((pts.max(0)-origin)/100).astype(int)+1;lo=np.maximum(lo,0);hi=np.minimum(hi,[799,999]);size=hi-lo+1
   if np.any(size<=0):out[key]=None;continue
   im=Image.new('1',tuple(size));dr=ImageDraw.Draw(im)
   for poly in polys:
    coords=[tuple((np.array(q)-origin)/100-lo) for q in poly];dr.polygon(coords,fill=1);dr.line(coords+[coords[0]],fill=1,width=1)
   mask=binary_fill_holes(np.array(im));yy,xx=np.where(mask);out[key]=(yy+lo[1],xx+lo[0])
  foot.append(out)
 cache.write_bytes(pickle.dumps(foot))
occupied=np.zeros(shape,np.int16);conflicts=[]
for f in foot:
 a=f['tall']
 if a is None:continue
 yy,xx=a;occupied[yy,xx]+=1
 if np.any(roadmask[yy,xx]):conflicts.append((f,int(roadmask[yy,xx].sum())))
print('TALL_BUILDINGS_ON_AUTHORED_STREETS',len(conflicts),flush=True)
print([(f['source'],n,len(f['tall'][0])) for f,n in conflicts if len(f['tall'][0])>350],flush=True)
# Reserve existing, actual shop buildings, which are absent from the scenery manifest.
actors=json.loads((P/'actors.json').read_text());shopmask=np.zeros(shape,bool);shops=[]
for a in actors:
 if a['cls']!='BP_DeliveryStore_C':continue
 yaw=math.radians(a['rotation'][1]);t=np.array([math.cos(yaw),math.sin(yaw)]);back=np.array([-t[1],t[0]]);pos=np.array(a['position'][:2]);poly=Polygon([pos+t*x+back*y for x,y in [(-1350,-100),(1350,-100),(1350,3400),(-1350,3400)]]);shopmask|=raster(poly);shops.append(dict(name=a['name'],entrance=a['position'],yaw=a['rotation'][1],conflict=poly.intersection(reserve).area))
print('SHOP_STREET_CONFLICTS',[(s['name'],round(s['conflict']/10000)) for s in shops if s['conflict']>1],flush=True)
flat=np.load(R/'compact_city/original_terrain_heights_2m.npy');flat=np.array(Image.fromarray(np.nan_to_num(flat,nan=99999).astype(np.float32)).resize((800,1000),Image.Resampling.BILINEAR));flatok=np.abs(flat)<35
# Keep terrain at the original scale and move only architecture obstructing a street.
for f,n in conflicts:
 yy,xx=f['tall'];occupied[yy,xx]-=1
moves=[]
for f,n in sorted(conflicts,key=lambda r:-len(r[0]['tall'][0])):
 yy,xx=f['tall'];y0=int(yy.min());x0=int(xx.min());kernel=np.zeros((np.ptp(yy)+1,np.ptp(xx)+1),np.float32);kernel[yy-y0,xx-x0]=1;bad=(occupied>0)|roadmask|shopmask|~flatok
 score=fftconvolve(bad.astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(score<.15)
 if not len(xs):raise RuntimeError('No safe lot for '+f['source'])
 ds=(ys-y0)**2+(xs-x0)**2;k=int(np.argmin(ds));dy=int(ys[k]-y0);dx=int(xs[k]-x0);occupied[yy+dy,xx+dx]+=1
 moves.append(dict(source=f['source'],delta_cm=[dx*100,dy*100],distance_m=math.hypot(dx,dy),street_overlap_cells=n))
print('NECESSARY_LOCAL_MOVES',len(moves),'median',np.median([v['distance_m'] for v in moves]),'max',max(v['distance_m'] for v in moves),flush=True)
(P/'streets.json').write_text(json.dumps(dict(secondary_roads=roads)));(P/'building_moves.json').write_text(json.dumps(moves,indent=2));(P/'actual_shops.json').write_text(json.dumps(shops,indent=2));Image.fromarray((roadmask*255).astype('uint8')).save(P/'exact_street_reserve.png')
print('EXACT_STREET_PLAN_READY',len(roads),flush=True)
