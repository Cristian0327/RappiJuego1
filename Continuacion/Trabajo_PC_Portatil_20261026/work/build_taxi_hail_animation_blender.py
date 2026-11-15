import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
r=Path(__file__).resolve().parents[1];out=r/'outputs/DeliveryArt/AnimationRebuild';bpy.ops.wm.open_mainfile(filepath=str(out/'Upright/Standing/AN_CrowdIdle_Rebuilt.blend'));rig=next(x for x in bpy.data.objects if x.type=='ARMATURE');sc=bpy.context.scene;start=sc.frame_start;end=sc.frame_end;poses=[]
for i in range(61):
 sc.frame_set(start+(i%(end-start+1)));bpy.context.view_layer.update();poses.append({b.name:(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()) for b in rig.pose.bones})
rig.animation_data_clear();sc.frame_start=1;sc.frame_end=61;sc.render.fps=30
lower='lowerarm_r' if 'lowerarm_r' in rig.pose.bones else 'forearm_r'
def aim(b,d):
 parent=b.parent.matrix.to_quaternion() if b.parent else Quaternion();rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion();q=(b.bone.tail_local-b.bone.head_local).normalized().rotation_difference(d.normalized())@b.bone.matrix_local.to_quaternion();b.rotation_quaternion=rest.inverted()@parent.inverted()@q;bpy.context.view_layer.update()
for frame in range(1,62):
 sc.frame_set(frame)
 for b in rig.pose.bones:
  loc,rot,scale=poses[frame-1][b.name];b.rotation_mode='QUATERNION';b.location=loc;b.rotation_quaternion=rot;b.scale=scale
 bpy.context.view_layer.update();t=(frame-1)/60;factor=min(1.,t/.18,(1.-t)/.18);factor=max(0,factor);factor=factor*factor*(3-2*factor)
 for n,d in [('upperarm_r',Vector((.12,-1,.14))),(lower,Vector((.08,-1,.22))),('hand_r',Vector((.03,-1,.26)))]:
  b=rig.pose.bones[n];before=b.rotation_quaternion.copy();aim(b,d);b.rotation_quaternion=before.slerp(b.rotation_quaternion,factor);bpy.context.view_layer.update()
 for b in rig.pose.bones:
  b.keyframe_insert('location',frame=frame,group=b.name);b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name);b.keyframe_insert('scale',frame=frame,group=b.name)
rig.animation_data.action.name='AN_CrowdTaxiHail_MixamoAdapted';bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/'AN_CrowdTaxiHail.blend'));bpy.ops.export_scene.fbx(filepath=str(out/'AN_CrowdTaxiHail.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z');print('TAXI_HAIL_MIXAMO_ADAPTED_READY',flush=True)
