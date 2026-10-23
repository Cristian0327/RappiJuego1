import json,math,numpy as np
from pathlib import Path
W=Path('new_map_audit');m=json.loads((W/'before_spacing_expansion/manifest.json').read_text());p=json.loads((W/'before_spacing_expansion/integration_plan.json').read_text());base=np.array([v[:4] for v in p['building_footprints']]);orig={v['source']:np.array(v['location'])*[100,-100,100] for v in m['instances']};anchors=np.array([orig[v[4]][:2] for v in p['building_footprints']]);rd=np.array(m['roads'][0]['center'])*[100,-100,100];half=np.array(m['roads'][0]['halfwidth'])*100;out=[]
for factor in [1.68,1.70,1.72,1.75]:
 boxes=base.copy();boxes[:,[0,2]]+=(factor-1)*anchors[:,0,None];boxes[:,[1,3]]+=(factor-1)*anchors[:,1,None];count=0
 for i in range(25,len(rd)-25,6):
  tangent=rd[i+1,:2]-rd[i-1,:2];tangent/=np.linalg.norm(tangent);right=np.array([-tangent[1],tangent[0]])
  for side in [-1,1]:
   for extra in [1900,2400,3000,3800,4800,6000]:
    xy=rd[i,:2]*factor+right*side*(half[i]+extra);x,y=xy
    if np.any((x+2050>boxes[:,0])&(x-2050<boxes[:,2])&(y+2050>boxes[:,1])&(y-2050<boxes[:,3])):continue
    if any(math.dist(xy,np.array(s['position'][:2])*factor)<4000 for s in p['stations']):continue
    out.append({'factor':factor,'center':[float(x),float(y),0.],'road_index':i,'side':side,'extra':extra,'back':[float(z) for z in right*side]});count+=1
 print('FACTOR_CANDIDATES',factor,count)
(W/'spacing_expansion_candidates.json').write_text(json.dumps(out))

