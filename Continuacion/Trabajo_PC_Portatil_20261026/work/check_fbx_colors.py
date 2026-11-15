import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(root/'outputs/DeliveryArt/TrafficDetailed/SK_Private.fbx'))
for o in bpy.data.objects:
 if o.type=='MESH':
  print('COLORS',[(c.name,len(c.data)) for c in o.data.color_attributes],flush=True)
  for a in o.data.color_attributes:print('SAMPLES',[(d.color[:]) for d in list(a.data)[::max(1,len(a.data)//12)]],flush=True)
