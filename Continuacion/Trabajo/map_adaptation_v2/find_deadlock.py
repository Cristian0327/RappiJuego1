import json,re,math,sys,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent;D=json.load(open(P/'defaults.json'))['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager'];E=json.load(open(P/'arc_conflicts.json'));meta=json.load(open(P.parent/'isolated_repair/work/pure_traffic_vehicle_foundation.json'))['models'];cars={};causes={}
for line in Path(sys.argv[1]).read_text(errors='replace').splitlines():
 if 'V2CAR|' in line:
  t,i,d,s,p,y=line.split('V2CAR|')[1].split('|')[:6];cars.setdefault(float(t),{})[int(i)]=[float(d),float(s),np.array([float(q) for q in re.findall(r'[XYZ]=([-+\d.]+)',p)])[:2],float(y)]
 if 'V2CAUSE|' in line:
  t,i,n,j,l,o=line.split('V2CAUSE|')[1].split('|')[:6];causes.setdefault(float(t),{})[int(i)]=[float(n),float(j),float(l),o]
t=max(set(cars)&set(causes));f=cars[t];c=causes[t];edges={};print('TIME',t)
for i,a in f.items():
 li=D['LaneIndices'][i];mi=meta[D['ModelIndices'][i]];fw=np.array([math.cos(math.radians(a[3])),math.sin(math.radians(a[3]))]);hw=mi['half_width'];hl=mi['half_length'];blocks=[]
 for j,b in f.items():
  if i==j:continue
  lj=D['LaneIndices'][j];mj=meta[D['ModelIndices'][j]]
  if {4:0,5:1}.get(li,li)=={4:0,5:1}.get(lj,lj):gap=(b[0]-a[0])%E['lanes'][li]['length']-hl-mj['half_length']-190
  else:
   delta=b[2]-a[2];ahead=delta@fw;side=abs(np.cross(delta,fw));angle=math.radians(b[3]-a[3]);ol=mj['half_length']*abs(math.cos(angle))+mj['half_width']*abs(math.sin(angle));ow=mj['half_length']*abs(math.sin(angle))+mj['half_width']*abs(math.cos(angle))
   gap=ahead-hl-ol-190 if 0<ahead<5000 and side<hw+ow+50 else 1e8
  if gap<2:blocks.append(j)
 if c[i][0]<2 and a[1]<20:edges[i]=blocks
cycles=[]
for start in edges:
 def walk(i,path):
  if i in path:
   cyc=path[path.index(i):];key=tuple(sorted(cyc))
   if key not in cycles:cycles.append(key)
   return
  if len(path)>15:return
  for j in edges.get(i,[]):walk(j,path+[i])
 walk(start,[])
print('CYCLES',len(cycles))
for cyc in cycles[:25]:
 print([(i,D['LaneIndices'][i],round(f[i][3]),c[i][3],edges.get(i)) for i in cyc])
print('OWNERS',[(i,D['LaneIndices'][i],c[i],edges.get(i)) for i in f if c[i][3]!='None'])
