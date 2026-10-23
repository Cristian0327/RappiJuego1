import bpy,json,math
from pathlib import Path
from mathutils import Vector
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');m=json.loads((W/'manifest.json').read_text());road=m['roads'][0];terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));inv=terrain.matrix_world.inverted();direction=inv.to_3x3()@Vector((0,0,-1));out=[]
raw=json.loads((W/'full_store_candidates.json').read_text())
for item in raw:
 p=Vector(item['center']);zs=[]
 i=item['road_index'];q=Vector((road['center'][i][0]*100,-road['center'][i][1]*100,0));back=(p-q).normalized();right=Vector((back.y,-back.x,0))
 for u,v in [(0,0),(-1300,-1700),(-1300,1700),(1300,-1700),(1300,1700),(0,-1700),(0,1700),(-1300,0),(1300,0)]:
  dx=right.x*u+back.x*v;dy=right.y*u+back.y*v
  origin=Vector(((p.x+dx)/300+121.6244,-(p.y+dy)/300+55.6001,200));hit,co,n,j=terrain.ray_cast(inv@origin,direction);zs.append((terrain.matrix_world@co).z*300 if hit else 99999)
 if max(zs)<30 and min(zs)>-300:item['ground_samples']=zs;out.append(item)
(W/'full_store_flat.json').write_text(json.dumps(out));print('FULL_STORE_FLAT',len(out))
