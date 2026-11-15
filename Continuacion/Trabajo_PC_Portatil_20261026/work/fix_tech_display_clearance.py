import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];file=root/'outputs/DeliveryArt/Shops/SM_TechInterior.blend';bpy.ops.wm.open_mainfile(filepath=str(file));obj=bpy.data.objects['SM_TechInterior'];changed=0
for i in range(0,len(obj.data.vertices),8):
 group=list(obj.data.vertices[i:i+8]);lo=Vector([min(v.co[a] for v in group) for a in range(3)]);hi=Vector([max(v.co[a] for v in group) for a in range(3)]);c=(lo+hi)*.5;s=hi-lo
 if abs(abs(c.x)-7.5)<.001 and abs(c.y)<.001 and ((abs(s.x-1.5)<.001 and abs(s.z-.96)<.001) or (abs(s.x-1.55)<.001 and abs(s.z-.06)<.001)):
  width=.90 if s.z>.5 else .95
  for v in group:v.co.x=c.x+(v.co.x-c.x)*width/s.x
  changed+=1
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.export_scene.fbx(filepath=str(file.with_suffix('.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE',axis_forward='-Y',axis_up='Z');print('TECH_PEDESTALS_NARROWED',changed,flush=True)
