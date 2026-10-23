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
def maskpoly(corners):
 im=Image.new('L',(800,1000));ImageDraw.Draw(im).polygon([((q[0]+40000)/100,(q[1]+50000)/100) for q in corners],fill=255);return np.array(im)>0
# Place real-size stores in clear lots; preserve buildings instead of globally moving them.
for si,oldshop in enumerate(old['shops']):
 counts=[0]*6; margins=[]
 target=np.array(oldshop['center'])/np.array([1.72,1.72,1]);found=None
 for i in sorted(range(10,len(c)-10,5),key=lambda i:np.linalg.norm(c[i,:2]-target[:2])):
  for side in [-1,1]:
   right=t[i,:2];back=rr[i,:2]*side
   for extra in [1900,2400,3200,4200,5500,7000,8500,10500]:
    q=c[i,:2]+back*(hw[i]+extra);corners=[q+right*x+back*y for x,y in [(-1300,-1700),(1300,-1700),(1300,1700),(-1300,1700)]];mask=maskpoly(corners)
    if mask.sum()<650 or np.any(occ[mask]) or not np.all(flat[mask]) or any(np.linalg.norm(q-a)<3600 for a in used):continue
    # Avoid other principal sections crossing the full store plot.
    near=np.linalg.norm(c[:,:2]-q,axis=1)
    margins.append((float(np.min(near-hw)),q.tolist()));counts[0]+=1
    if np.any(near<hw+1600):continue
    counts[1]+=1
    ent=q-back*1600;door=c[i,:2]+back*(hw[i]-110);link=[[*door,20],[*ent,20]]
    corridor=maskpoly([door+right*110,door-right*110,ent-right*110,ent+right*110])
    counts[2]+=1
    if np.any(occ[corridor]):continue
    counts[3]+=1
    found=dict(center=[*q,0],road_index=i,side=side,store_axes=[right.tolist(),back.tolist()],back=back.tolist(),entrance=[*ent,20],store_yaw=math.degrees(math.atan2(right[1],right[0])),walk_link=link);used.append(q);occ[mask]=True;break
   if found:break
  if found:break
 if not found:print(counts,sorted(margins,reverse=True)[:5]);raise RuntimeError('No clear store plot '+str(si))
 shops.append(found)
p['shops']=shops;p['spacing_expansion']=1.;p['stations']=[dict(s,position=[s['position'][0]/1.72,s['position'][1]/1.72,s['position'][2]]) for s in old['stations']];(W/'integration_plan.json').write_text(json.dumps(p));print('ORIGINAL_DENSITY_PREPARED',len(m['instances']),len(shops),len(p['pedestrians']),flush=True)
# Move the road planner onto the original, non-expanded physical wall raster.
for name in ['route_secondary_roads.py','plan_urban_refresh.py']:
 s=(O/name).read_text().replace('68800','40000').replace('86000','50000')
 if name=='plan_urban_refresh.py':s=s.replace("json.loads((W/'spacing_expansion_selected.json').read_text())['shops']","p['shops']")
 (O/name).write_text(s)
(O/'plan_secondary_roads.py').write_text((O/'plan_secondary_roads.py').read_text().replace('*5.16','*3.0'))
for name in ['plan_curved_corridors.py','curve_roads.py']:
 s=(U/name).read_text().replace('68800','40000').replace('86000','50000');(U/name).write_text(s)
