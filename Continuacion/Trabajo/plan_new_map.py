import json,math,numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
W=Path('new_map_audit');m=json.loads((W/'manifest.json').read_text());road=m['roads'][0];c=np.array(road['center'])*[100,-100,100];c[:,2]=4
# Join open ends to existing intersections instead of teleporting or inventing straight roads through houses.
closed=[]
for start,end in [(0,867),(489,len(c)-1)]:
 p=c[start:end+1].copy()
 for _ in range(4):p=.5*p+.25*np.roll(p,1,axis=0)+.25*np.roll(p,-1,axis=0)
 closed.append(p)
def offset(p,amount):
 t=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0);t[:,2]=0;t/=np.linalg.norm(t,axis=1)[:,None];right=np.stack([-t[:,1],t[:,0],np.zeros(len(t))],axis=1);return p+right*amount
lanes=[]
for i in range(6):
 p=closed[(i//2)%2];p=p[::-1] if i%2 else p;lanes.append(offset(p,900).tolist())
# Combined main-road transit circuit covers both lobes of the city.
bus=np.concatenate([c,c[489:868]],axis=0)
for _ in range(5):bus=.5*bus+.25*np.roll(bus,1,axis=0)+.25*np.roll(bus,-1,axis=0)
lanes.append(offset(bus,330).tolist())
buildings=[]
for a in m['instances']:
 if 'bounds' not in a or 'Relieve' in a['source']:continue
 lo,hi=np.array(a['bounds'])*100
 if hi[2]-lo[2]<230:continue
 buildings.append([lo[0],-hi[1],hi[0],-lo[1],a['source']])
def blocked(p,hx=50,hy=50):return any(p[0]+hx>b[0] and p[0]-hx<b[2] and p[1]+hy>b[1] and p[1]-hy<b[3] for b in buildings)
tree=cKDTree(c[:,:2]);half=np.array(road['halfwidth'])*100
routes=[];spawn=[];rejected=0
for start in range(5,len(c)-22,22):
 seg=c[start:start+16];t=np.gradient(seg,axis=0);t[:,2]=0;t/=np.linalg.norm(t,axis=1)[:,None];r=np.stack([-t[:,1],t[:,0],np.zeros(len(t))],axis=1)
 for sign in [-1,1]:
  hw=half[start:start+16];mid=hw-120
  p1=seg+r*(sign*mid-32)[:,None];p2=seg+r*(sign*mid+32)[:,None];path=np.concatenate([p1,p2[::-1]]);path[:,2]=20
  if any(blocked(p,45,45) for p in path):rejected+=1;continue
  rid=len(routes);routes.append(path.tolist())
  for s in [3,13,23]:
   p=path[s].copy();p[2]+=88;delta=path[(s+1)%32]-path[s];spawn.append({'route':rid,'next':(s+1)%32,'position':p.tolist(),'yaw':math.degrees(math.atan2(delta[1],delta[0])),'model':len(spawn)%60})
# Shop sites: collision-free plots adjoining a sidewalk, spread along the road network.
shops=[];stations=[]
t=np.gradient(c,axis=0);t[:,2]=0;t/=np.linalg.norm(t,axis=1)[:,None];rr=np.stack([-t[:,1],t[:,0],np.zeros(len(t))],axis=1)
for candidate in range(5*((len(c)-50)//12)):
 i=25+(candidate%((len(c)-50)//12))*12
 extra=[1800,2800,4200,6000,8500][candidate//((len(c)-50)//12)]
 for sign in [-1,1]:
  p=c[i]+rr[i]*sign*(half[i]+extra);p[2]=0
  if abs(p[0])>36500 or abs(p[1])>44000 or blocked(p,1300,1300):continue
  near,_=tree.query(p[:2]);
  if near<half[i]+1350:continue
  if any(math.dist(p[:2],s['center'][:2])<3400 for s in shops):continue
  door=c[i]+rr[i]*sign*(half[i]+650);door[2]=20
  shops.append({'center':p.tolist(),'door':door.tolist(),'yaw':math.degrees(math.atan2(-rr[i,1]*sign,-rr[i,0]*sign)),'road_index':i,'side':sign})
  if len(shops)>=40:break
 if len(shops)>=40:break
# Stops on locally straight sections, with a free platform footprint beside the bus lane.
bp=np.array(lanes[6]);bt=np.roll(bp,-1,axis=0)-np.roll(bp,1,axis=0);bt[:,2]=0;bt/=np.linalg.norm(bt,axis=1)[:,None];br=np.stack([-bt[:,1],bt[:,0],np.zeros(len(bt))],axis=1)
for i in range(30,len(bp)-30,8):
 if np.dot(bt[i-6],bt[i+6])<.995:continue
 p=bp[i]-br[i]*330;p[2]=20
 if blocked(p,1400,500):continue
 if any(math.dist(p[:2],s['position'][:2])<15000 for s in stations):continue
 if any(math.dist(p[:2],s['center'][:2])<3000 for s in shops):continue
 stations.append({'position':p.tolist(),'bus_stop':bp[i].tolist(),'yaw':math.degrees(math.atan2(bt[i,1],bt[i,0])),'route_index':i})
 if len(stations)==4:break
plan={'lanes':lanes,'walk_routes':routes,'pedestrians':spawn,'shops':shops,'stations':stations,'building_footprints':buildings,'rejected_walk_routes':rejected,'player_start':spawn[len(spawn)//2]['position'] if spawn else [0,0,200]}
(W/'integration_plan.json').write_text(json.dumps(plan))
print('PLAN',len(routes),'walk loops',len(spawn),'pedestrians',len(shops),'shops',len(stations),'stations','rejected',rejected)



