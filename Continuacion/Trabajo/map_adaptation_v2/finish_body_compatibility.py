import json,sys,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'urban_refresh/python_deps'))
from shapely.geometry import LineString,Polygon
from shapely.ops import unary_union
j=json.loads((P/'body_arc_conflicts.json').read_text());moves=j['movements'];shapes=[];lines=[]
for m in moves:
 q=np.array(m['path']);lines.append(LineString(q));length=1000 if m['lane']==6 else 340;width=155;boxes=[]
 for k,p in enumerate(q):
  direction=q[min(k+1,len(q)-1)]-q[max(0,k-1)];direction/=max(np.linalg.norm(direction),.0001);normal=np.array([-direction[1],direction[0]]);boxes.append(Polygon([p+direction*length+normal*width,p-direction*length+normal*width,p-direction*length-normal*width,p+direction*length-normal*width]))
 shapes.append(unary_union(boxes).buffer(15))
N=len(moves);matrix=np.eye(N,dtype=bool);shared=0
for i,a in enumerate(moves):
 for k,b in enumerate(moves[:i]):
  same_flow=lines[i].hausdorff_distance(lines[k])<120 and np.dot(np.array(a['path'][-1])-np.array(a['path'][0]),np.array(b['path'][-1])-np.array(b['path'][0]))>0
  safe=a['junction']!=b['junction'] or same_flow or not shapes[i].intersects(shapes[k]);matrix[i,k]=matrix[k,i]=safe
  if same_flow:shared+=1
j['compatible']=matrix.ravel().tolist();(P/'body_arc_conflicts.json').write_text(json.dumps(j,indent=2));print('BODY_MATRIX',N,'same_flow_pairs',shared,'safe_pairs',int(matrix.sum()))
