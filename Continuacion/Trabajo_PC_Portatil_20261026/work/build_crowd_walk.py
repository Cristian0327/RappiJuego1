import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd'
bpy.ops.wm.open_mainfile(filepath=str(out/'SK_Citizen00.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH')
with bpy.data.libraries.load(str(root/'outputs/DeliveryArt/Animation/AN_MixamoWalk.blend'),link=False) as (a,b):b.actions=[n for n in a.actions if n.startswith('AN_MixamoWalk')]
action=b.actions[0];action.name='AN_CrowdWalk';rig.animation_data.action=action;end=int(action.frame_range[1]);print('MIXAMO_CYCLE_FRAMES',end)
for f in range(1,end+1):
 bpy.context.scene.frame_set(f);pb=rig.pose.bones['root'];pb.location=(0,0,0);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floor=min(v.co.z for v in ev.data.vertices);pb.location=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-floor));pb.keyframe_insert('location',frame=f,group='root')
if bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=end
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AN_CrowdWalk.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'AN_CrowdWalk.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
for f in sorted(out.glob('SK_*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(f));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
 with bpy.data.libraries.load(str(out/'AN_CrowdWalk.blend'),link=False) as (a,b):b.actions=['AN_CrowdWalk']
 rig.animation_data.action=b.actions[0];bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=end;bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(f))


