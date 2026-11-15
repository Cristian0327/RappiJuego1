import json,math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;actors=json.loads((P/'actors.json').read_text());q=np.array(json.loads((P/'actual_lanes.json').read_text())[6]);stations=[a for a in actors if a['cls']=='BP_BogotaTransmiStation_C'];report=[]
def overlap(p,t,s,compact):
 angle=math.radians(s['rotation'][1]);u=np.array([math.cos(angle),math.sin(angle)]);v=np.array([-u[1],u[0]]);n=np.array([-t[1],t[0]]);delta=p-np.array(s['position'][:2]);half=1212.5 if compact and s['name'].endswith('_2') else 2425
 for axis in [t,n,u,v]:
  r=915*abs(np.dot(t,axis))+135*abs(np.dot(n,axis))+half*abs(np.dot(u,axis))+181*abs(np.dot(v,axis))
  if abs(np.dot(delta,axis))>=r+20:return False
 return True
for s in stations:
 counts=[]
 for compact in [False,True]:
  bad=[]
  for i,p in enumerate(q):
   t=q[(i+1)%len(q),:2]-p[:2];t/=np.linalg.norm(t)
   if overlap(p[:2],t,s,compact):bad.append(i)
  counts.append(bad)
 report.append(dict(name=s['name'],full_station_overlaps=len(counts[0]),compact_station_overlaps=len(counts[1]),sample_indices=counts[1]))
(P/'station_bus_overlap_before.json').write_text(json.dumps(report,indent=2));print([(r['name'],r['full_station_overlaps'],r['compact_station_overlaps']) for r in report])
