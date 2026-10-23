import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/DeliveryArt/Shops/SM_FreshMarketInterior.blend'));obj=bpy.data.objects['SM_FreshMarketInterior'];counts={}
for p in obj.data.polygons:
 c=p.center
 if (abs(c.x)>9.8 or c.y>8.8) and c.z>1:
  m=obj.data.materials[p.material_index];key=m.name;counts[key]=counts.get(key,0)+1
print('WALLS',counts,flush=True)
for m in obj.data.materials:print('MAT',m.name,list(m.diffuse_color),flush=True)
print('OBJECTS',[(o.name,o.type) for o in bpy.context.scene.objects][:20],flush=True)
