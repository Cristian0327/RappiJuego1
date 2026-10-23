import json,shutil,math,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt
R=Path.cwd();C=R/'compact_city';B=C/'before';B.mkdir(exist_ok=True)
for folder in ['new_map_audit','urban_refresh','urban_corrections']:
 for src in (R/folder).iterdir():
  if src.is_file() and src.suffix in ['.json','.png','.wkt','.py']:
   dst=B/folder/src.name;dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists():shutil.copy2(src,dst)
W=R/'new_map_audit';O=R/'urban_refresh';U=R/'urban_corrections';m=json.loads((W/'before_spacing_expansion/manifest.json').read_text());m['spacing_expansion']=1.;(W/'manifest.json').write_text(json.dumps(m));shutil.copy2(W/'before_spacing_expansion/obstacles.png',W/'obstacles.png')
Image.open(B/'urban_refresh/flat_urban_terrain.png').resize((800,1000),Image.Resampling.NEAREST).save(O/'flat_urban_terrain.png');(O/'accepted_infill.json').write_text('[]')
exec(compile((R/'plan_new_map.py').read_text(),'OriginalDensityRoutes','exec'),{})
p=json.loads((W/'integration_plan.json').read_text());old=json.loads((B/'new_map_audit/integration_plan.json').read_text());occ=np.array(Image.open(W/'obstacles.png'))>0;flat=np.array(Image.open(O/'flat_urban_terrain.png'))>0;c=np.array(m['roads'][0]['center'])*[100,-100,100];t=np.gradient(c,axis=0);t[:,2]=0;t/=np.linalg.norm(t,axis=1)[:,None];rr=np.stack([-t[:,1],t[:,0],np.zeros(len(t))],1);hw=np.array(m['roads'][0]['halfwidth'])*100;shops=[];used=[]
import sys
sys.path.insert(0,str(O/'python_deps'))
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
roads=[]
for rd in m['roads']:
 cc=np.array(rd['center'])*[100,-100,100];side=np.array(rd['side'])*[1,-1,1];ww=np.array(rd['halfwidth'])*100;left=cc[:,:2]+side[:,:2]*ww[:,None];right0=cc[:,:2]-side[:,:2]*ww[:,None];roads.extend(Polygon([left[i],right0[i],right0[i+1],left[i+1]]).buffer(0) for i in range(len(cc)-1))
roadpoly=unary_union(roads);models=[]
for item in m['instances']:
 if 'bounds' not in item or 'Relieve' in item['source']:continue
 aa,bb=np.array(item['bounds'])*[100,-100,100];lo=np.minimum(aa,bb);hi=np.maximum(aa,bb)
 if hi[2]-lo[2]<230:continue
 models.append([item,box(*lo[:2],*hi[:2])])
def maskpoly(corners):
 im=Image.new('L',(800,1000));ImageDraw.Draw(im).polygon([((q[0]+40000)/100,(q[1]+50000)/100) for q in corners],fill=255);return np.array(im)>0
candidates=[]
for i in range(12,len(c)-12,2):
 for sign in [-1,1]:
  right=t[i,:2];back=rr[i,:2]*sign
  for extra in [1900,2500,3400,4500,6000,7500,9000]:
   q=c[i,:2]+back*(hw[i]+extra);corners=[q+right*x+back*y for x,y in [(-1300,-1700),(1300,-1700),(1300,1700),(-1300,1700)]];poly=Polygon(corners);mask=maskpoly(corners)
   if mask.sum()<650 or not np.all(flat[mask]) or poly.intersection(roadpoly).area>1:continue
   hits=[j for j,(it,bb) in enumerate(models) if bb.intersects(poly)]
   if len(hits)>8 or any(models[j][1].area>3500000 for j in hits):continue
   candidates.append((i,sign,right,back,q,poly,hits))
print('LOCAL_STORE_CANDIDATES',len(candidates),flush=True)
reserved=[];relocate=set()
for si,oldshop in enumerate(old['shops']):
 target=np.array(oldshop['center'][:2])/1.72;options=sorted(candidates,key=lambda v:len(v[6])*5000+np.linalg.norm(v[4]-target))
 for i,sign,right,back,q,poly,hits in options:
  if any(poly.distance(bb)<300 for bb in reserved):continue
  ent=q-back*1600;door=c[i,:2]+back*(hw[i]-110);link=[[*door,20],[*ent,20]]
  corridor=LineString([door,ent]).buffer(120);linkhits=[j for j,(it,bb) in enumerate(models) if bb.intersects(corridor)]
  if len(set(hits+linkhits))>8 or any(models[j][1].area>3500000 for j in linkhits):continue
  reserved.append(poly.union(corridor));relocate.update(hits+linkhits);shops.append(dict(center=[*q,0],road_index=i,side=sign,store_axes=[right.tolist(),back.tolist()],back=back.tolist(),entrance=[*ent,20],store_yaw=math.degrees(math.atan2(right[1],right[0])),walk_link=link));break
 else:raise RuntimeError('No local store reserve '+str(si))
# Shift only the buildings occupying selected shop plots, to nearby clear land.
moves=[]
from shapely.affinity import translate
for j in sorted(relocate,key=lambda j:-models[j][1].area):
 item,bb=models[j];center=np.array(bb.centroid.coords[0]);found=False
 for radius in [800,1200,1800,2400,3200,4200,5500,7000,9000]:
  for ang in np.linspace(0,2*math.pi,32,endpoint=False):
   delta=np.array([math.cos(ang),math.sin(ang)])*radius;dest=translate(bb,*delta);mask=maskpoly(np.array(dest.exterior.coords))
   if mask.sum()<max(4,bb.area/10000*.8) or not np.all(flat[mask]):continue
   if dest.intersects(roadpoly) or any(dest.distance(v)<150 for v in reserved):continue
   if any(dest.distance(other)<80 for k,(it,other) in enumerate(models) if k!=j and k not in relocate):continue
   if any(dest.distance(models[k][1])<80 for k in sorted(relocate) if k<j):continue
   models[j][1]=dest;item['location'][0]+=delta[0]/100;item['location'][1]-=delta[1]/100
   for bound in item['bounds']:bound[0]+=delta[0]/100;bound[1]-=delta[1]/100
   moves.append(dict(source=item['source'],delta_cm=delta.tolist()));found=True;break
  if found:break
 if not found:print('RELOCATION_DIAGNOSTIC',len(relocate),len(moves),bb.area,flush=True);raise RuntimeError('No local relocation '+item['source'])
(C/'local_building_adjustments.json').write_text(json.dumps(moves,indent=2));(W/'manifest.json').write_text(json.dumps(m))
# Update the physical planning mask conservatively for the few relocated objects.
im=Image.open(W/'obstacles.png');draw=ImageDraw.Draw(im)
for mv in moves:
 it=next(v for v in m['instances'] if v['source']==mv['source']);a,b=np.array(it['bounds'])*[100,-100,100];lo=np.minimum(a,b);hi=np.maximum(a,b);d=np.array(mv['delta_cm']);draw.rectangle(((lo[0]-d[0]+40000)/100,(lo[1]-d[1]+50000)/100,(hi[0]-d[0]+40000)/100,(hi[1]-d[1]+50000)/100),fill=0);draw.rectangle(((lo[0]+40000)/100,(lo[1]+50000)/100,(hi[0]+40000)/100,(hi[1]+50000)/100),fill=255)
im.save(W/'obstacles.png');print('LOCAL_BUILDINGS_ADJUSTED',len(moves),flush=True)
p['shops']=shops;p['spacing_expansion']=1.;p['stations']=[dict(s,position=[s['position'][0]/1.72,s['position'][1]/1.72,s['position'][2]]) for s in old['stations']];(W/'integration_plan.json').write_text(json.dumps(p));print('ORIGINAL_DENSITY_PREPARED',len(m['instances']),len(shops),len(p['pedestrians']),flush=True)
# Move the road planner onto the original, non-expanded physical wall raster.
for name in ['route_secondary_roads.py','plan_urban_refresh.py']:
 s=(O/name).read_text().replace('68800','40000').replace('86000','50000')
 if name=='plan_urban_refresh.py':s=s.replace("json.loads((W/'spacing_expansion_selected.json').read_text())['shops']","p['shops']")
 (O/name).write_text(s)
(O/'plan_secondary_roads.py').write_text((O/'plan_secondary_roads.py').read_text().replace('*5.16','*3.0'))
for name in ['plan_curved_corridors.py','curve_roads.py']:
 s=(U/name).read_text().replace('68800','40000').replace('86000','50000');(U/name).write_text(s)
