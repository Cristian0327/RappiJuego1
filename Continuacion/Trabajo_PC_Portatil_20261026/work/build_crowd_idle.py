import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd'
bpy.ops.wm.open_mainfile(filepath=str(out/'SK_Citizen00.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH')
action=bpy.data.actions['Idle'].copy();action.name='AN_CrowdIdle';rig.animation_data.action=action;end=int(action.frame_range[1]);bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=end
for f in range(1,end+1):
 bpy.context.scene.frame_set(f);pb=rig.pose.bones['root'];pb.location=(0,0,0);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floor=min(v.co.z for v in ev.data.vertices);pb.location=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-floor));pb.keyframe_insert('location',frame=f,group='root')
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AN_CrowdIdle.blend'))
bpy.ops.export_scene.fbx(filepath=str(out/'AN_CrowdIdle.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
print('CROWD_IDLE_READY')
