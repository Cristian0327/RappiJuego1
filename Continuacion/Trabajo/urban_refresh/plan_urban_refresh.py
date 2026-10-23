import json,numpy as np,math
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt
from PIL import Image
W=Path('new_map_audit');U=Path('urban_refresh');m=json.loads((W/'manifest.json').read_text());p=json.loads((W/'integration_plan.json').read_text());r=m['roads'][0];c=np.array(r['center'])*[100,-100,100];hw=np.array(r['halfwidth'])*100;tan=np.roll(c,-1,axis=0)-np.roll(c,1,axis=0);tan[:,2]=0;tan/=np.maximum(np.linalg.norm(tan,axis=1)[:,None],1e-6);right=np.stack([-tan[:,1],tan[:,0],np.zeros(len(c))],axis=1);houses=np.array([v[:4] for v in p['building_footprints']]);walk=cKDTree(np.array([v[:2] for route in p['walk_routes'] for v in route]+[v[:2] for shop in p['shops'] for v in shop['walk_link']]));shop=np.array([v['center'][:2] for v in p['shops']]);st=np.array([v['position'][:2] for v in p['stations']]);physical=np.array(Image.open(W/'obstacles.png'))>0;dist=distance_transform_edt(~physical)*100

def clear(q,radius):
 x=int((q[0]+40000)/100);y=int((q[1]+50000)/100)
 return not np.any((q[0]+radius>houses[:,0])&(q[0]-radius<houses[:,2])&(q[1]+radius>houses[:,1])&(q[1]-radius<houses[:,3])) and 0<=x<physical.shape[1] and 0<=y<physical.shape[0] and dist[y,x]>radius and np.min(np.linalg.norm(shop-q[:2],axis=1))>2900
cross=[]
for i in range(25,len(c)-25,9):
 if abs(hw[i]-1528)>200 or np.dot(tan[i-6],tan[i+6])<.998:continue
 if any(np.linalg.norm(c[i,:2]-np.array(s['position'][:2]))<9500 for s in cross):continue
 if np.min(np.linalg.norm(st-c[i,:2],axis=1))<4500:continue
 if not all(clear(c[i]+tan[i]*a+right[i]*b,85) for a in [-850,0,850] for b in [-hw[i]-70,hw[i]+70]):continue
 if any(np.min(np.linalg.norm(c[np.r_[0:max(0,i-20),min(len(c),i+20):len(c)],:2]-c[i,:2],axis=1))<1800 for _ in [0]):continue
 cross.append({'position':[float(c[i,0]),float(c[i,1]),0.0],'yaw':math.degrees(math.atan2(tan[i,1],tan[i,0])),'forward':tan[i].tolist(),'halfwidth':float(hw[i]),'road_index':i})
 if len(cross)>=18:break
items=[];placed=[]
for i in range(6,len(c)-6,12):
 for sign in [-1,1]:
  if np.min(np.linalg.norm(st-c[i,:2],axis=1))<3000:continue
  if any(math.dist(c[i,:2],s['position'][:2])<1800 for s in cross):continue
  for typ,offset,rad,period in [('Farola',90,40,1),('Banca',230,160,3),('Caneca',170,65,2)]:
   if i//12%period:continue
   q=c[i]+right[i]*sign*(hw[i]+offset)+tan[i]*(400 if typ=='Banca' else -300 if typ=='Caneca' else 0);q[2]=0
   if not clear(q,rad+50) or walk.query(q[:2])[0]<rad+75:continue
   if any(math.dist(q[:2],v[:2])<rad+100 for v in placed):continue
   yaw=math.degrees(math.atan2(tan[i,1],tan[i,0]));items.append({'type':typ,'position':q.tolist(),'yaw':yaw if sign>0 else yaw+180});placed.append(q)
   if typ=='Farola' and sum(v['type']=='Farola' for v in items)>=160:break
for cr in cross:
 at=np.array(cr['position']);t=np.array(cr['forward']);rr=np.array([-t[1],t[0],0])
 for side in [-1,1]:
  for offset in [-520,0,520]:
   q=at+t*offset+rr*side*(cr['halfwidth']-35);q[2]=20;items.append({'type':'Bolardo','position':q.tolist(),'yaw':cr['yaw']})
(U/'placement_plan.json').write_text(json.dumps({'crossings':cross,'furniture':items,'stations':p['stations']},indent=2));print('CROSSINGS',len(cross),'FURNITURE', {t:sum(v['type']==t for v in items) for t in ['Farola','Banca','Caneca','Bolardo']})


