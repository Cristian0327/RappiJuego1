import json,math,sys,shutil,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.spatial import cKDTree
R=Path.cwd();C=R/'compact_city';B=C/'before';W=R/'new_map_audit';O=R/'urban_refresh';U=R/'urban_corrections';sys.path.insert(0,str(O/'python_deps'))
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
m=json.loads((W/'before_spacing_expansion/manifest.json').read_text());m['spacing_expansion']=1.;(W/'manifest.json').write_text(json.dumps(m));exec(compile((R/'plan_new_map.py').read_text(),'OriginalRoutes','exec'),{});p=json.loads((W/'integration_plan.json').read_text());old=json.loads((B/'new_map_audit/integration_plan.json').read_text());raw=json.loads((C/'original_object_wall_polygons.json').read_text());flat=np.array(Image.open(O/'flat_urban_terrain.png'))>0;sh=(1000,800);labels=np.zeros(sh,np.int32);occupied=np.zeros(sh,np.int16);pixels=[];lookup={}
for idx,row in enumerate(raw):
 im=Image.new('L',(800,1000));dr=ImageDraw.Draw(im)
 for poly in row['polygons']:dr.polygon([((q[0]+40000)/100,(q[1]+50000)/100) for q in poly],fill=255)
 yy,xx=np.where(np.array(im)>0);pixels.append([yy,xx]);lookup[row['source']]=idx;labels[yy,xx]=idx+1;occupied[yy,xx]+=1
print('OBJECT_MASKS',len(raw),'WALL_PIXELS',np.sum(occupied>0),flush=True)
np.save(C/'original_occupied.npy',occupied);np.save(C/'original_labels.npy',labels);(C/'object_sources.json').write_text(json.dumps([v['source'] for v in raw]))
def maskpoly(corners):
 im=Image.new('L',(800,1000));ImageDraw.Draw(im).polygon([((q[0]+40000)/100,(q[1]+50000)/100) for q in corners],fill=255);return np.array(im)>0
roads=[]
for rd in m['roads']:
 cc=np.array(rd['center'])*[100,-100,100];side=np.array(rd['side'])*[1,-1,1];ww=np.array(rd['halfwidth'])*100;left=cc[:,:2]+side[:,:2]*ww[:,None];rt=cc[:,:2]-side[:,:2]*ww[:,None];roads.extend(Polygon([left[i],rt[i],rt[i+1],left[i+1]]).buffer(0) for i in range(len(cc)-1))
roadpoly=unary_union(roads);roadmask=np.zeros(sh,bool)
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
reserve=np.zeros(sh,bool);shops=[]
def astar(start,goalset):
 gt=cKDTree(np.array(goalset));heap=[(gt.query(start)[0],0,start)];cost={start:0};prev={};closed=set();targets=set(goalset)
 while heap:
  _,g,v=heapq.heappop(heap)
  if v in closed:continue
  closed.add(v)
  if v in targets:
   path=[v]
   while v in prev:v=prev[v];path.append(v)
   return path[::-1]
  for dy,dx in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   w=(v[0]+dy,v[1]+dx)
   if not(0<=w[0]<1000 and 0<=w[1]<800 and free[w]) or (reserve[w] and math.dist(w,start)>4):continue
   if dx and dy and not(free[v[0]+dy,v[1]] and free[v[0],v[1]+dx]):continue
   ng=g+math.hypot(dx,dy)
   if ng<cost.get(w,1e30):cost[w]=ng;prev[w]=v;heapq.heappush(heap,(ng+gt.query(w)[0],ng,w))
 return []
for si,oldshop in enumerate(old['shops']):
 target=np.array(oldshop['center'][:2])/1.72;best=[];bad=(~flat)|roadmask|physical|reserve
 for angle,right,back,corners,lo,kernel in kernels:
  score=fftconvolve(bad.astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(score<.15)
  if not len(xs):continue
  # Origins at the center of the full rectangular shop reserve.
  centerx=xs-lo[0];centery=ys-lo[1];ex=np.rint(centerx-back[0]*17.5).astype(int);ey=np.rint(centery-back[1]*17.5).astype(int);inside=(ex>=0)&(ex<800)&(ey>=0)&(ey<1000);ys=ys[inside];xs=xs[inside];centerx=centerx[inside];centery=centery[inside];ex=ex[inside];ey=ey[inside];valid=np.isin(labs[ey,ex],list(goals));ys=ys[valid];xs=xs[valid];centerx=centerx[valid];centery=centery[valid];ex=ex[valid];ey=ey[valid]
  dist=(centerx*100-40000-target[0])**2+(centery*100-50000-target[1])**2
  for j in np.argsort(dist)[:10]:best.append((dist[j],angle,right,back,corners,np.array([centerx[j]*100-40000,centery[j]*100-50000]),(int(ey[j]),int(ex[j]))))
 for _,angle,right,back,corners,q,entcell in sorted(best,key=lambda v:v[0]):
  path=astar(entcell,goals[int(labs[entcell])])
  if not path:continue
  mask=maskpoly(corners+q);reserve|=mask;ent=q-back*1600;worldpath=[[x*100-40000,y*100-50000,20] for y,x in path[::-1]];worldpath.append([*ent,20]);shops.append(dict(center=[*q,0],road_index=int(tree.query(q)[1]),side=1,store_axes=[right.tolist(),back.tolist()],back=back.tolist(),entrance=[*ent,20],store_yaw=angle,walk_link=worldpath));break
 else:raise RuntimeError('No existing free urban lot '+str(si))
 print('FREE_STORE',si,len(path),flush=True)
p['shops']=shops;p['stations']=[dict(s,position=[s['position'][0]/1.72,s['position'][1]/1.72,s['position'][2]]) for s in old['stations']];p['spacing_expansion']=1.;(W/'integration_plan.json').write_text(json.dumps(p));(C/'local_building_adjustments.json').write_text('[]');Image.fromarray((physical*255).astype(np.uint8)).save(W/'obstacles.png');print('COMPACT_FREE_LOTS_READY',len(shops),flush=True)
for name in ['route_secondary_roads.py','plan_urban_refresh.py']:
 s=(O/name).read_text().replace('68800','40000').replace('86000','50000')
 if name=='plan_urban_refresh.py':s=s.replace("json.loads((W/'spacing_expansion_selected.json').read_text())['shops']","p['shops']")
 (O/name).write_text(s)
(O/'plan_secondary_roads.py').write_text((O/'plan_secondary_roads.py').read_text().replace('*5.16','*3.0'))
for name in ['plan_curved_corridors.py','curve_roads.py']:(U/name).write_text((U/name).read_text().replace('68800','40000').replace('86000','50000'))
