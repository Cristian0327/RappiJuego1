import re,json,sys,math
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;path=Path(sys.argv[1]) if len(sys.argv)>1 else P/'baseline_traffic2.log';text=path.read_text(errors='replace');cars={};services={}
def vector(s):return np.array([float(v) for v in re.findall(r'[XYZ]=([-+\d.]+)',s)])
for line in text.splitlines():
 if 'V2CAR|' in line:
  t,i,d,s,p,y=line.split('V2CAR|')[1].split('|')[:6];cars.setdefault(float(t),{})[int(i)]=dict(distance=float(d),speed=float(s),position=vector(p).tolist(),yaw=float(y))
 if 'V2SERVICE|' in line:
  t,n,p,v,f=line.split('V2SERVICE|')[1].split('|')[:5]
  if any(x in n for x in ['Motorcycle','RoadPatrol','TwoWheeler']):services.setdefault(float(t),{})[n]=dict(position=vector(p).tolist(),velocity=vector(v).tolist(),forward=vector(f).tolist())
summary=[]
for t,vs in cars.items():
 if re.search(r'v(?:[7-9]|[1-9][0-9]+)$',path.stem):vs={i:v for i,v in vs.items() if i<90}
 if len(vs)<(60 if re.search(r'v(?:[7-9]|[1-9][0-9]+)$',path.stem) else 140):continue
 moving=sum(v['speed']>20 for v in vs.values());summary.append(dict(time=t,cars=len(vs),moving=moving,stopped=len(vs)-moving))
bad=[]
for t,vs in services.items():
 for n,v in vs.items():
  speed=np.linalg.norm(v['velocity'][:2]);dot=np.dot(v['velocity'],v['forward'])/max(speed,1)
  if speed>50 and dot<-.2:bad.append(dict(time=t,name=n,speed=speed,dot=dot))
result=dict(windows=summary,reverse_service_samples=len(bad),reverse_examples=bad[:8]);(P/(path.stem+'_analysis.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
