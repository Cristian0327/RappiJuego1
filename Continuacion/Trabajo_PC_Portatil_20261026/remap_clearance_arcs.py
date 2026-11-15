import json,sys,math,bisect
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'python_deps'))
import numpy as np
from shapely.geometry import LineString,Polygon
from shapely.ops import unary_union
S=R.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2';old=json.loads((S/'actual_lanes.json').read_text());new=json.loads((R/'clearance_lanes.json').read_text());data=json.loads((S/'arc_conflicts.json').read_text())
lengths=[];oldcum=[];newcum=[]
for a,b in zip(old,new):
 def cumulative(q):return np.r_[0,np.cumsum(np.linalg.norm(np.roll(np.array(q)[:,:2],-1,axis=0)-np.array(q)[:,:2],axis=1))]
 oldcum.append(cumulative(a));newcum.append(cumulative(b));lengths.append(float(newcum[-1][-1]))
def remap(li,d):
 a,b=oldcum[li],newcum[li];d=d%a[-1];i=min(len(a)-2,bisect.bisect_right(a,d)-1);u=(d-a[i])/max(a[i+1]-a[i],1e-9);return float(b[i]+u*(b[i+1]-b[i]))
lines=[LineString([p[:2] for p in q+[q[0]]]) for q in new]
for li,row in enumerate(data['lanes']):
 row['length']=lengths[li]
 for e in row['events']:
  e['entry']=remap(li,e['entry']);e['exit']=remap(li,e['exit']);e['span']=(e['exit']-e['entry'])%row['length'];l=lines[li];d=np.array(l.interpolate((e['entry']+100)%l.length).coords[0])-np.array(l.interpolate((e['entry']-100)%l.length).coords[0]);e['direction']=(d/np.linalg.norm(d)).tolist()
for mid,m in enumerate(data['movements']):
 li=m['lane'];e=next(e for e in data['lanes'][li]['events'] if e['movement']==mid);m['entry']=e['entry'];m['exit']=e['exit'];m['path']=[list(lines[li].interpolate((e['entry']+d)%lengths[li]).coords[0]) for d in np.linspace(0,e['span'],max(3,int(e['span']/100)+1))]
shapes=[];movelines=[]
for m in data['movements']:
 q=np.array(m['path']);movelines.append(LineString(q));hl=1000 if m['lane']==6 else 340;hw=155;boxes=[]
 for k,p in enumerate(q):
  f=q[min(k+1,len(q)-1)]-q[max(0,k-1)];f/=max(np.linalg.norm(f),.0001);n=np.array([-f[1],f[0]]);boxes.append(Polygon([p+f*hl+n*hw,p-f*hl+n*hw,p-f*hl-n*hw,p+f*hl-n*hw]))
 shapes.append(unary_union(boxes).buffer(15))
N=len(shapes);matrix=np.eye(N,dtype=bool)
for i,a in enumerate(data['movements']):
 for j,b in enumerate(data['movements'][:i]):
  same=movelines[i].hausdorff_distance(movelines[j])<120 and np.dot(np.array(a['path'][-1])-np.array(a['path'][0]),np.array(b['path'][-1])-np.array(b['path'][0]))>0
  safe=a['junction']!=b['junction'] or same or not shapes[i].intersects(shapes[j]);matrix[i,j]=matrix[j,i]=safe
data['compatible']=matrix.ravel().tolist();(R/'clearance_arc_conflicts.json').write_text(json.dumps(data,indent=2));(R/'clearance_arc_distance_mapping.json').write_text(json.dumps(dict(old=[a.tolist() for a in oldcum],new=[a.tolist() for a in newcum])));print('Arc data updated',N,'movements',len(data['centers']),'zones')