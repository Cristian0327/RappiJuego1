import bpy,bmesh
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/TrafficDetailed'
for name in ['SK_TransMilenio','SK_TransMilenioG66']:
 f=out/(name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(f));obj=bpy.data.objects[name];rig=obj.find_armature();bpy.context.scene.frame_set(1)
 if not bpy.context.scene.get('platform_doors_unreal_negative_y',False):
  for v in obj.data.vertices:v.co.y*=-1
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
  bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
  for bone in rig.data.edit_bones:bone.head.y*=-1;bone.tail.y*=-1
  bpy.ops.object.mode_set(mode='OBJECT');bpy.context.scene['platform_doors_unreal_negative_y']=True
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE');bpy.ops.wm.save_as_mainfile(filepath=str(f))
print('BUS_PLATFORM_SIDE_PASS',flush=True)
