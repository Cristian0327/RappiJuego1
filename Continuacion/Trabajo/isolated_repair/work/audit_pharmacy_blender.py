import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/DeliveryArt/Shops/SM_PharmacyInterior.blend'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
r=[]
for p in o.data.polygons:
 if abs(p.center.z-.024)<.001 and p.normal.z>.9:
  m=o.data.materials[p.material_index];r.append({'position':list(p.center),'index':p.material_index,'material':m.name,'color':list(m.diffuse_color)})
  if len(r)==10:break
(root/'work/pharmacy_blender_material_audit.json').write_text(json.dumps(r,indent=2))
