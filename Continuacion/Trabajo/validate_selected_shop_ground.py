import bpy,json,math
from pathlib import Path
from mathutils import Vector
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));inv=terrain.matrix_world.inverted();direction=inv.to_3x3()@Vector((0,0,-1));data=json.loads((W/'spacing_expansion_selected.json').read_text());raw=data['shops'];flat=[]
for item in raw:item['back']=item['store_axes'][1]
for item in raw:
 p=Vector(item['center']);f=item['factor'];back=Vector((*item['back'],0));right=Vector((back.y,-back.x,0));zs=[]
 for u,v in [(0,0),(-1300,-1700),(-1300,1700),(1300,-1700),(1300,1700),(0,-1700),(0,1700),(-1300,0),(1300,0)]:
  at=p+right*u+back*v;origin=Vector((at.x/f/300+121.6244,-at.y/f/300+55.6001,200));hit,co,n,j=terrain.ray_cast(inv@origin,direction);zs.append((terrain.matrix_world@co).z*300 if hit else 99999)
 if max(zs)<30 and min(zs)>-30:item['ground_samples']=zs;flat.append(item)
(W/'selected_shop_ground_validation.json').write_text(json.dumps(flat))
for factor in sorted(set(s['factor'] for s in raw)):print('EXPANSION_FLAT',factor,sum(s['factor']==factor for s in flat))
