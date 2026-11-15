import json,re,math,sys,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent;D=json.load(open(P/'defaults.json'))['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager'];meta=json.load(open(P.parent/'isolated_repair/work/pure_traffic_vehicle_foundation.json'))['models'];frames={};path=Path(sys.argv[1])
for line in path.read_text(errors='replace').splitlines():
 if 'V2CAR|' in line:
  t,i,d,s,p,y=line.split('V2CAR|')[1].split('|')[:6];frames.setdefault(float(t),{})[int(i)]=(np.array([float(v) for v in re.findall(r'[XYZ]=([-+\d.]+)',p)])[:2],math.radians(float(y)))
if re.search(r'v(?:[7-9]|[1-9][0-9]+)$',path.stem):
 indices=[int(i*140/80) for i in range(80)]+list(range(140,150))
 D['ModelIndices']=[D['ModelIndices'][i] for i in indices]
report=[]
for t,frame in frames.items():
 overlap=[]
 for i,(p,yaw) in frame.items():
  if i>=len(D['ModelIndices']):continue
  mi=meta[D['ModelIndices'][i]];f=np.array([math.cos(yaw),math.sin(yaw)]);r=np.array([-f[1],f[0]])
  for j,(q,angle) in frame.items():
   if j<=i or j>=len(D['ModelIndices']) or np.linalg.norm(q-p)>2400:continue
   mj=meta[D['ModelIndices'][j]];g=np.array([math.cos(angle),math.sin(angle)]);s=np.array([-g[1],g[0]]);delta=q-p
   if all(abs(delta@a)<mi['half_length']*abs(f@a)+mi['half_width']*abs(r@a)+mj['half_length']*abs(g@a)+mj['half_width']*abs(s@a)-25 for a in [f,r,g,s]):overlap.append((i,j))
 report.append(dict(time=t,overlaps=len(overlap),examples=overlap[:10]))
result=dict(max_overlaps=max([r['overlaps'] for r in report],default=0),frames=report);path.with_name(path.stem+'_body_overlaps.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(max_overlaps=result['max_overlaps'],bad_frames=[r for r in report if r['overlaps']][:8]),indent=2))
