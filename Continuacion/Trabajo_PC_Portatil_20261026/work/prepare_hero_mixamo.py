import bpy, json
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parents[1]
out=root/'outputs/DeliveryArt/Mixamo'
out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig.animation_data_clear()
for bone in rig.pose.bones: bone.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
report={'bones':{b.name:[list(b.head_local),list(b.tail_local)] for b in rig.data.bones},'meshes':[]}
for obj in meshes:
 bpy.context.view_layer.objects.active=obj
 report['meshes'].append({'name':obj.name,'vertices':len(obj.data.vertices)})
 for mod in list(obj.modifiers):
  if mod.type=='ARMATURE':bpy.ops.object.modifier_apply(modifier=mod.name)
 world=obj.matrix_world.copy();obj.parent=None;obj.matrix_world=world;obj.vertex_groups.clear()
bpy.ops.object.select_all(action='DESELECT')
for obj in meshes:obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'Hero_Mixamo_Input.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Z',axis_up='Y',path_mode='COPY',embed_textures=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Hero_Mixamo_Input.blend'))
(out/'Hero_Mixamo_Input.json').write_text(json.dumps(report,indent=2))
print('HERO_MIXAMO_READY',report['meshes'])
