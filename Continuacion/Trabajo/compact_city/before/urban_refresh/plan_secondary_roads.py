import json,numpy as np,math
from pathlib import Path
from PIL import Image,ImageDraw
U=Path(__file__).parent;W=U.parent/'new_map_audit';m=json.loads((W/'manifest.json').read_text());p=json.loads((W/'integration_plan.json').read_text());src=json.loads((U/'source_lines.json').read_text());lines=[]
for o in src:
 if o.get('type')!='CURVE':continue
 for i,s in enumerate(o['splines']):
  a=np.array(s['points'])
  if np.max(abs(a[:,2]))>.01 or np.max(a[:,0])<10:continue
  q=(a[:,:2]-[121.6244,55.6001])*5.16; q[:,1]*=-1;lines.append(dict(name=o['name']+'_'+str(i),points=(q*100).tolist(),width=700,sidewalk=220))
def dist(q,a,b):
 t=np.clip(np.dot(q-a,b-a)/np.dot(b-a,b-a),0,1);v=q-(a+t*(b-a));return np.linalg.norm(v)
roadsegments=[(np.array(a),np.array(b)) for s in lines for a,b in zip(s['points'],s['points'][1:])]
# Preserve existing models: identify modest lateral relocations only for the new road reserve.
boxes=p['building_footprints'];moves=[]
for box in boxes:
 a=np.array(box[:2]);b=np.array(box[2:4]);c=(a+b)/2;rad=np.linalg.norm(b-a)/2
 near=[(x,y) for x,y in roadsegments if dist(c,x,y)<rad+570]
 if not near:continue
 # Corner and sampled road center clearance against a conservative expanded box.
 def blocked(c0):
  half=(b-a)/2+620
  for x,y in near:
   n=max(2,int(np.linalg.norm(y-x)/200));v=np.linspace(x,y,n)
   if np.any(np.all(abs(v-c0)<half,axis=1)):return True
  return False
 if not blocked(c):continue
 moves.append(dict(source=box[4],center=c.tolist(),half=((b-a)/2).tolist()))
report=dict(secondary_roads=lines,road_conflicts=moves)
(U/'secondary_road_plan.json').write_text(json.dumps(report,indent=2))
im=Image.new('RGB',(1376,1720),'#ceb48e');d=ImageDraw.Draw(im)
def pt(v):return((v[0]+68800)/100,(v[1]+86000)/100)
for box in boxes:d.rectangle([pt(box[:2]),pt(box[2:4])],fill='#7a6350')
for road in m['roads']:
 q=np.array(road['center']);q[:,1]*=-1;d.line([pt(v[:2]*100) for v in q],fill='#475969',width=30)
for s in lines:d.line([pt(v) for v in s['points']],fill='#ca4e29',width=7)
for s in p['stations']:
 x,y=pt(s['position']);d.ellipse((x-6,y-6,x+6,y+6),fill='yellow')
im.save(U/'secondary_roads_plan.png');print('SECONDARY_ROADS',len(lines),'BUILDING_CONFLICTS',len(moves));print([(s['name'],len(s['points'])) for s in lines])
