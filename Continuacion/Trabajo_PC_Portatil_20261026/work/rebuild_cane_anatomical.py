import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd'
bpy.ops.wm.open_mainfile(filepath=str(out/'SK_Citizen06.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
with bpy.data.libraries.load(str(root/'outputs/DeliveryArt/AnimationRebuild/AN_CrowdWalk_Rebuilt.blend'),link=False) as (a,b):b.actions=['AN_CrowdWalk_Rebuilt']
action=b.actions[0].copy();action.name='AN_CrowdCane_Rebuilt';rig.animation_data.action=action;end=int(action.frame_range[1]);scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=end;scene.frame_set(1);bpy.context.view_layer.update()
goal=bpy.data.objects.new('Cane grip IK target',None);bpy.context.collection.objects.link(goal);goal.rotation_mode='QUATERNION';goal.rotation_quaternion=rig.pose.bones['hand_l'].matrix.to_quaternion()
ik=rig.pose.bones['lowerarm_l'].constraints.new('IK');ik.target=goal;ik.chain_count=2;ik.use_stretch=False
rotation=rig.pose.bones['hand_l'].constraints.new('COPY_ROTATION');rotation.target=goal;rotation.owner_space='WORLD';rotation.target_space='WORLD'
for f in range(1,end+1):
 scene.frame_set(f);t=(f-1)/(end-1)
 if t<=.6:dy=-16+32*t/.6;lift=0
 else:q=(t-.6)/.4;dy=16-32*q;lift=6*math.sin(math.pi*q)
 root_z=rig.pose.bones['root'].matrix.translation.z
 pb=rig.pose.bones['cane'];pb.location=pb.bone.matrix_local.to_quaternion().inverted()@Vector((0,dy,lift-root_z));pb.keyframe_insert('location',frame=f,group='cane')
 goal.location=(32,-19+dy,81+lift);goal.keyframe_insert('location',frame=f)
 spine=rig.pose.bones['spine_02'];axis=spine.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0));spine.rotation_quaternion=Quaternion(axis,math.radians(7))@spine.rotation_quaternion;spine.keyframe_insert('rotation_quaternion',frame=f,group='spine_02')
 bpy.context.view_layer.update()
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.nla.bake(frame_start=1,frame_end=end,step=1,only_selected=False,visual_keying=True,clear_constraints=True,use_current_action=True,bake_types={'POSE'})
bpy.data.objects.remove(goal,do_unlink=True);scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'outputs/DeliveryArt/AnimationRebuild/AN_CrowdCane_Rebuilt.blend'))
rig.name='Armature'
bpy.ops.export_scene.fbx(filepath=str(root/'outputs/DeliveryArt/AnimationRebuild/AN_CrowdCane_Rebuilt.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
print('ANATOMICAL_CANE_REBUILD_PASS',flush=True)
