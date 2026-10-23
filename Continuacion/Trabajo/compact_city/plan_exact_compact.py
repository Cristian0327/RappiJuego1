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
c=np.array(m['roads'][0]['center'])*[100,-100,100];t=np.gradient(c,axis=0);t[:,2]=0;t/=np.linalg.norm(t,axis=1)[:,None];rr=np.stack([-t[:,1],t[:,0],np.zeros(len(t))],1);hw=np.array(m['roads'][0]['halfwidth'])*100;candidates=[]
for i in range(12,len(c)-12,2):
 for sign in [-1,1]:
  right=t[i,:2];back=rr[i,:2]*sign
  for extra in [1850,2250,2800,3500,4500,6000]:
   q=c[i,:2]+back*(hw[i]+extra);corners=[q+right*x+back*y for x,y in [(-1300,-1700),(1300,-1700),(1300,1700),(-1300,1700)]];poly=Polygon(corners);mask=maskpoly(corners)
   if mask.sum()<650 or not np.all(flat[mask]) or poly.intersection(roadpoly).area>1:continue
   ent=q-back*1600;door=c[i,:2]+back*(hw[i]-110);corridor=LineString([door,ent]).buffer(120);reserved=poly.union(corridor);both=mask|maskpoly(corridor.exterior.coords);hits=set(int(v)-1 for v in np.unique(labels[both]) if v)
   # Avoid moving blocks extending far beyond this shop's neighborhood.
   if len(hits)>12 or any(len(pixels[j][0])>1500 or (len(pixels[j][0]) and max(np.ptp(pixels[j][0]),np.ptp(pixels[j][1]))>45) or any(word in raw[j]['source'] for word in ['Parque','Unicentro','Universidad','Colegio']) for j in hits):continue
   candidates.append(dict(i=i,sign=sign,right=right,back=back,q=q,poly=reserved,hits=hits,mask=both,entrance=ent,door=door))
print('EXACT_STORE_CANDIDATES',len(candidates),flush=True)
reserved=[];reserve_mask=np.zeros(sh,bool);relocate=set();shops=[]
for si,prev in enumerate(old['shops']):
 target=np.array(prev['center'][:2])/1.72
 options=sorted(candidates,key=lambda v:len(v['hits'])*4000+sum(len(pixels[j][0]) for j in v['hits'])*2+np.linalg.norm(v['q']-target))
 for row in options:
  if any(row['poly'].distance(b)<250 for b in reserved):continue
  reserved.append(row['poly']);reserve_mask|=row['mask'];relocate.update(row['hits']);q=row['q'];back=row['back'];right=row['right'];shops.append(dict(center=[*q,0],road_index=row['i'],side=row['sign'],store_axes=[right.tolist(),back.tolist()],back=back.tolist(),entrance=[*row['entrance'],20],store_yaw=math.degrees(math.atan2(right[1],right[0])),walk_link=[[*row['door'],20],[*row['entrance'],20]]));break
 else:raise RuntimeError('No reserve for store '+str(si))
for j in relocate:
 yy,xx=pixels[j];occupied[yy,xx]-=1
moves=[]
print('ROADMASK_COVERAGE',int(roadmask.sum()),'BUILDING_WALLS_ON_ROAD',int(np.sum(roadmask & (occupied>0))),'FLAT',int(flat.sum()),'RELOCATE',len(relocate),flush=True)
from scipy.signal import fftconvolve
for j in sorted(relocate,key=lambda j:-len(pixels[j][0])):
 yy,xx=pixels[j];y0=int(yy.min());x0=int(xx.min());kernel=np.zeros((int(np.ptp(yy))+1,int(np.ptp(xx))+1),np.float32);kernel[yy-y0,xx-x0]=1
 blocked=(~flat)|roadmask|reserve_mask|(occupied>0);score=fftconvolve(blocked.astype(np.float32),kernel[::-1,::-1],mode='valid');ys,xs=np.where(score<.15)
 if not len(xs):raise RuntimeError('No physical plot anywhere '+raw[j]['source'])
 ds=(ys-y0)**2+(xs-x0)**2;k=int(np.argmin(ds));dy=int(ys[k]-y0);dx=int(xs[k]-x0)
 if ds[k]>180**2:raise RuntimeError('Relocation exceeds neighborhood '+raw[j]['source'])
 y=yy+dy;x=xx+dx;occupied[y,x]+=1;pixels[j]=[y,x];item=next(v for v in m['instances'] if v['source']==raw[j]['source']);item['location'][0]+=dx;item['location'][1]-=dy
 for bound in item['bounds']:bound[0]+=dx;bound[1]-=dy
 moves.append(dict(source=item['source'],delta_cm=[dx*100,dy*100],distance_m=math.hypot(dx,dy)))
Image.fromarray(((occupied>0)*255).astype(np.uint8)).save(W/'obstacles.png');(C/'local_building_adjustments.json').write_text(json.dumps(moves,indent=2));(W/'manifest.json').write_text(json.dumps(m));p['shops']=shops;p['stations']=[dict(s,position=[s['position'][0]/1.72,s['position'][1]/1.72,s['position'][2]]) for s in old['stations']];p['spacing_expansion']=1.;p['building_footprints']=[]
for item in m['instances']:
 if 'bounds' not in item or 'Relieve' in item['source']:continue
 lo,hi=np.array(item['bounds'])*100
 if hi[2]-lo[2]>230:p['building_footprints'].append([lo[0],-hi[1],hi[0],-lo[1],item['source']])
(W/'integration_plan.json').write_text(json.dumps(p));print('COMPACT_CITY_READY',len(m['instances']),len(shops),'moved',len(moves),'median',np.median([v['distance_m'] for v in moves]),flush=True)
for name in ['route_secondary_roads.py','plan_urban_refresh.py']:
 s=(O/name).read_text().replace('68800','40000').replace('86000','50000')
 if name=='plan_urban_refresh.py':s=s.replace("json.loads((W/'spacing_expansion_selected.json').read_text())['shops']","p['shops']")
 (O/name).write_text(s)
(O/'plan_secondary_roads.py').write_text((O/'plan_secondary_roads.py').read_text().replace('*5.16','*3.0'))
for name in ['plan_curved_corridors.py','curve_roads.py']:(U/name).write_text((U/name).read_text().replace('68800','40000').replace('86000','50000'))
