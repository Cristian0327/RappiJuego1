import bpy,json
from pathlib import Path
from mathutils import Vector
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');p=json.loads((U/'placement_plan.json').read_text());terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));inv=terrain.matrix_world.inverted();direc=inv.to_3x3()@Vector((0,0,-1));keep=[];bad=[]
for item in p['furniture']:
 x,y,z=item['position'];hit,co,n,j=terrain.ray_cast(inv@Vector((x/100,-y/100,200)),direc);zz=(terrain.matrix_world@co).z*100 if hit else 99999
 if abs(zz)<35:keep.append(item)
 else:bad.append(item)
p['furniture']=keep;(U/'placement_plan.json').write_text(json.dumps(p,indent=2));(U/'rejected_furniture.json').write_text(json.dumps(bad));print('FLAT_FURNITURE',len(keep),'REJECTED',len(bad))
