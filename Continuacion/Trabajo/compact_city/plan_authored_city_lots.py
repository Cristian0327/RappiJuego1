import json,math,sys,shutil,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.signal import fftconvolve
from scipy.ndimage import distance_transform_edt,label,binary_dilation
from scipy.spatial import cKDTree
R=Path.cwd();C=R/'compact_city';B=C/'before';W=R/'new_map_audit';O=R/'urban_refresh';U=R/'urban_corrections';sys.path.insert(0,str(O/'python_deps'))
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
m=json.loads((W/'before_spacing_expansion/manifest.json').read_text());m['spacing_expansion']=1.;(W/'manifest.json').write_text(json.dumps(m));exec(compile((R/'plan_new_map.py').read_text(),'OriginalRoutes','exec'),{});p=json.loads((W/'integration_plan.json').read_text());old=json.loads((B/'new_map_audit/integration_plan.json').read_text());flat=np.array(Image.open(O/'flat_urban_terrain.png'))>0;sh=(1000,800);labels=np.load(C/'original_labels.npy');occupied=np.load(C/'original_occupied.npy');sources=json.loads((C/'object_sources.json').read_text());raw=[dict(source=v) for v in sources];pixels=[list(np.where(labels==i+1)) for i in range(len(sources))]
def maskpoly(corners):
 im=Image.new('L',(800,1000));ImageDraw.Draw(im).polygon([((q[0]+40000)/100,(q[1]+50000)/100) for q in corners],fill=255);return np.array(im)>0
roads=[]
for rd in m['roads']:
 cc=np.array(rd['center'])*[100,-100,100];side=np.array(rd['side'])*[1,-1,1];ww=np.array(rd['halfwidth'])*100;left=cc[:,:2]+side[:,:2]*ww[:,None];rt=cc[:,:2]-side[:,:2]*ww[:,None];roads.extend(Polygon([left[i],rt[i],rt[i+1],left[i+1]]).buffer(0) for i in range(len(cc)-1))
secondary=json.loads((O/'secondary_road_plan.json').read_text())['secondary_roads'];secondary_reserve=unary_union([LineString(np.array(v['samples'])[:,:2]).buffer(380,quad_segs=16) for v in secondary]);roadpoly=unary_union(roads+[secondary_reserve]);roadmask=np.zeros(sh,bool)
for poly in roadpoly.geoms if roadpoly.geom_type=='MultiPolygon' else [roadpoly]:
 rm=maskpoly(poly.exterior.coords)
 for hole in poly.interiors:rm &= ~maskpoly(hole.coords)
 roadmask|=rm
from scipy.signal import fftconvolve
from scipy.ndimage import distance_transform_edt,label
import heapq
c=np.array(m['roads'][0]['center'])*[100,-100,100];t=np.gradient(c,axis=0);t[:,2]=0;t/=np.linalg.norm(t,axis=1)[:,None];rr=np.stack([-t[:,1],t[:,0],np.zeros(len(t))],1);hw=np.array(m['roads'][0]['halfwidth'])*100;tree=cKDTree(c[:,:2]);physical=occupied>0;clear=distance_transform_edt(~physical)*100;free=(clear>100)&flat
# Pedestrians can use the existing sidewalk component; avoid adding roads through empty lots.
inner=[]
for rd in m['roads']:
 cc=np.array(rd['center'])*[100,-100,100];side=np.array(rd['side'])*[1,-1,1];ww=np.array(rd['innerwidth'])*100;l=cc[:,:2]+side[:,:2]*ww[:,None];rt=cc[:,:2]-side[:,:2]*ww[:,None];inner.extend(Polygon([l[i],rt[i],rt[i+1],l[i+1]]).buffer(0) for i in range(len(cc)-1))
asphalt=unary_union(inner);amask=np.zeros(sh,bool)
for poly in asphalt.geoms if asphalt.geom_type=='MultiPolygon' else [asphalt]:
 mm=maskpoly(poly.exterior.coords)
 for hole in poly.interiors:mm &= ~maskpoly(hole.coords)
 amask|=mm
free &= ~amask;labs,n=label(free);goals={}
for i in range(1,len(c)-1):
 for sign in [-1,1]:
  q=c[i]+rr[i]*sign*(hw[i]-110);x=int(round((q[0]+40000)/100));y=int(round((q[1]+50000)/100))
  if 0<=x<800 and 0<=y<1000 and labs[y,x]:goals.setdefault(int(labs[y,x]),[]).append((y,x))
kernels=[]
for angle in range(0,360,45):
 a=math.radians(angle);right=np.array([math.cos(a),math.sin(a)]);back=np.array([-right[1],right[0]]);corners=np.array([right*x+back*y for x,y in [(-1300,-1700),(1300,-1700),(1300,1700),(-1300,1700)]]);lo=np.floor(corners.min(0)/100).astype(int);hi=np.ceil(corners.max(0)/100).astype(int);im=Image.new('L',tuple((hi-lo+1).tolist()));ImageDraw.Draw(im).polygon([tuple(v/100-lo) for v in corners],fill=1);kernel=np.array(im,np.float32);kernels.append((angle,right,back,corners,lo,kernel))
secondary_mask=np.zeros(sh,bool)
for poly in secondary_reserve.geoms if secondary_reserve.geom_type=='MultiPolygon' else [secondary_reserve]:
 mm=maskpoly(poly.exterior.coords)
 for hole in poly.interiors:mm &= ~maskpoly(hole.coords)
 secondary_mask|=mm
large_names={v['source'] for v in json.loads((C/'large_building_tall_footprints.json').read_text())};large_ids={i for i,v in enumerate(sources) if v in large_names};forced={int(v)-1 for v in np.unique(labels[secondary_mask]) if v and int(v)-1 not in large_ids}
for j in forced:
 yy,xx=pixels[j];occupied[yy,xx]-=1
# Low walls and fences in the new street reserve are trimmed from per-instance Blender variants.
trim=secondary_mask & np.isin(labels,[v+1 for v in large_ids]);occupied[trim]=0
(C/'street_clearance_large_sources.json').write_text(json.dumps([sources[j] for j in large_ids if np.any(labels[secondary_mask]==j+1)]));print('FORCED_STREET_RELOCATIONS',len(forced),'LARGE_FRONTAGE_VARIANTS',len(json.loads((C/'street_clearance_large_sources.json').read_text())),flush=True)
basebad=(~flat)|roadmask|(occupied>0);movable=set(forced);unmovable=np.zeros(sh,bool)
for j,(yy,xx) in enumerate(pixels):
 if not len(yy):continue
 if j not in forced and (max(np.ptp(yy),np.ptp(xx))>18 or len(yy)>300 or any(w in sources[j] for w in ['Parque','Unicentro','Universidad','Colegio'])):unmovable[yy,xx]=True;continue
 y0=int(yy.min());x0=int(xx.min());kernel=np.zeros((int(np.ptp(yy))+1,int(np.ptp(xx))+1),np.float32);kernel[yy-y0,xx-x0]=1;bad=basebad.copy();bad[yy,xx]=(occupied[yy,xx]>1)|roadmask[yy,xx]|~flat[yy,xx];scores=fftconvolve(bad.astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(scores<.15)
 if len(xs) and np.min((ys-y0)**2+(xs-x0)**2)<70**2:movable.add(j)
 else:unmovable[yy,xx]=True
print('NEARBY_MOVABLE_BUILDINGS',len(movable),flush=True)
reserve=np.zeros(sh,bool);shops=[];relocate=set(forced)
for si,prev in enumerate(old['shops']):
 target=np.array(prev['center'][:2])/1.72;best=[];bad=(~flat)|roadmask|unmovable|reserve
 for angle,right,back,corners,lo,kernel in kernels:
  score=fftconvolve(bad.astype(np.float32),kernel[::-1,::-1],mode='valid');load=fftconvolve((occupied>0).astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(score<.15)
  if not len(xs):continue
  cx=xs-lo[0];cy=ys-lo[1];qcost=np.sqrt((cx*100-40000-target[0])**2+(cy*100-50000-target[1])**2)+np.maximum(0,load[ys,xs])*1500
  for k in np.argsort(qcost)[:30]:best.append((qcost[k],angle,right,back,corners,np.array([cx[k]*100-40000,cy[k]*100-50000])))
 for _,angle,right,back,corners,q in sorted(best,key=lambda v:v[0]):
  mask=maskpoly(corners+q);hits=set(int(v)-1 for v in np.unique(labels[mask]) if v)
  if not hits<=movable:continue
  reserve|=binary_dilation(mask,iterations=2);relocate.update(hits);ent=q-back*1600;shops.append(dict(center=[*q,0],road_index=int(tree.query(q)[1]),side=1,store_axes=[right.tolist(),back.tolist()],back=back.tolist(),entrance=[*ent,20],store_yaw=angle));break
 else:raise RuntimeError('No local shop plot '+str(si))
 print('LOCAL_SHOP',si,'affected',len(hits),flush=True)
for j in relocate:
 if j not in forced:
  yy,xx=pixels[j];occupied[yy,xx]-=1
moves=[]
for j in sorted(relocate,key=lambda j:-len(pixels[j][0])):
 yy,xx=pixels[j];y0=int(yy.min());x0=int(xx.min());kernel=np.zeros((int(np.ptp(yy))+1,int(np.ptp(xx))+1),np.float32);kernel[yy-y0,xx-x0]=1;bad=(~flat)|roadmask|reserve|(occupied>0);score=fftconvolve(bad.astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(score<.15)
 if not len(xs):raise RuntimeError('Cannot relocate '+sources[j])
 ds=(ys-y0)**2+(xs-x0)**2;k=int(np.argmin(ds));dy=int(ys[k]-y0);dx=int(xs[k]-x0)
 if ds[k]>150**2:raise RuntimeError('Distant relocation '+sources[j])
 occupied[yy+dy,xx+dx]+=1;pixels[j]=[yy+dy,xx+dx];item=next(v for v in m['instances'] if v['source']==sources[j]);item['location'][0]+=dx;item['location'][1]-=dy
 for bound in item['bounds']:bound[0]+=dx;bound[1]-=dy
 moves.append(dict(source=item['source'],delta_cm=[dx*100,dy*100],distance_m=math.hypot(dx,dy)))
print('BUILDINGS_MOVED',len(moves),'MEDIAN_METERS',float(np.median([v['distance_m'] for v in moves])),flush=True)
# Find coherent pedestrian links to each existing sidewalk after the local relocations.
physical=occupied>0;free=(distance_transform_edt(~physical)*100>100)&flat&~amask;labs,n=label(free);goals={}
for i in range(1,len(c)-1):
 for sign in [-1,1]:
  q=c[i]+rr[i]*sign*(hw[i]-110);x=int(round((q[0]+40000)/100));y=int(round((q[1]+50000)/100))
  if 0<=x<800 and 0<=y<1000 and labs[y,x]:goals.setdefault(int(labs[y,x]),[]).append((y,x))
exec((C/'local_astar.txt').read_text());reserve=np.zeros(sh,bool)
for row in shops:
 ent=np.array(row['entrance'][:2]);back=np.array(row['back']);q=ent-back*200;start=(int(round((q[1]+50000)/100)),int(round((q[0]+40000)/100)));lab=int(labs[start]);path=astar(start,goals.get(lab,[])) if lab in goals else []
 if not path:
  nearby=np.array([(y,x) for y,x in zip(*np.where(free)) if int(labs[y,x]) in goals]);dist=np.linalg.norm(nearby-np.array(start),axis=1);k=int(np.argmin(dist));start=tuple(nearby[k]);path=astar(start,goals[int(labs[start])])
 if not path:raise RuntimeError('Store lacks walk access')
 row['walk_link']=[[x*100-40000,y*100-50000,20] for y,x in path[::-1]]+[row['entrance']]
p['shops']=shops;p['stations']=[dict(s,position=[s['position'][0]/1.72,s['position'][1]/1.72,s['position'][2]]) for s in old['stations']];p['spacing_expansion']=1.;p['building_footprints']=[]
for item in m['instances']:
 if 'bounds' not in item or 'Relieve' in item['source']:continue
 lo,hi=np.array(item['bounds'])*100
 if hi[2]-lo[2]>230:p['building_footprints'].append([lo[0],-hi[1],hi[0],-lo[1],item['source']])
(W/'manifest.json').write_text(json.dumps(m));(W/'integration_plan.json').write_text(json.dumps(p,default=lambda v:v.item() if isinstance(v,np.generic) else list(v)));(C/'local_building_adjustments.json').write_text(json.dumps(moves,indent=2,default=lambda v:v.item() if isinstance(v,np.generic) else list(v)));Image.fromarray((physical*255).astype(np.uint8)).save(W/'obstacles.png');print('COMPACT_LOCAL_LOTS_READY',len(shops),flush=True)
