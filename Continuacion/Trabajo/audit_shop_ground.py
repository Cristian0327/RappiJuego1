import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/integration_plan.json');d=json.loads(p.read_text());terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));inv=terrain.matrix_world.inverted()
for s in d['shops']:
 v=s['center'];o=Vector((v[0]/300+121.6244,-v[1]/300+55.6001,200));hit,co,n,idx=terrain.ray_cast(inv@o,inv.to_3x3()@Vector((0,0,-1)))
 z=(terrain.matrix_world@co).z*300 if hit else None;s['ground_height_cm']=z;print('SHOP_GROUND',d['shops'].index(s),z)
p.write_text(json.dumps(d))
