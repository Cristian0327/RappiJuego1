import bpy,math
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd'
for clip in ['AN_CrowdEnterCar']:
 bpy.ops.wm.open_mainfile(filepath=str(out/'AN_CrowdIdle.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');bpy.context.scene.frame_set(1);bpy.context.view_layer.update();neutral={p.name:(p.rotation_quaternion.copy(),p.location.copy()) for p in rig.pose.bones}
 action=bpy.data.actions.new(clip);rig.animation_data.action=action;scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=37;scene.render.fps=30
 def rotate(name,axis,degrees):
  p=rig.pose.bones[name];local=p.bone.matrix_local.to_3x3().inverted()@Vector(axis);p.rotation_quaternion=Quaternion(local,math.radians(degrees))@p.rotation_quaternion
 for f in range(1,38):
  t=(f-1)/36;scene.frame_set(f)
  for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.rotation_quaternion=neutral[p.name][0];p.location=neutral[p.name][1]
  if clip=='AN_CrowdEnterCar':
   sit=max(0,(t-.35)/.65);reach=math.sin(math.pi*min(1,t/.5))
   pelvis=rig.pose.bones['pelvis'];pelvis.location+=pelvis.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-32*sit));rotate('spine_02',(1,0,0),15*math.sin(math.pi*t))
   for side in ['l','r']:rotate('thigh_'+side,(1,0,0),-58*sit);rotate('calf_'+side,(1,0,0),85*sit)
   rotate('upperarm_l',(1,0,0),-55*reach);rotate('lowerarm_l',(1,0,0),-35*reach)
  else:
   w=math.sin(math.pi*t);rotate('thigh_l',(1,0,0),-35*w);rotate('calf_l',(1,0,0),40*w);rotate('upperarm_l',(1,0,0),-45*w);rotate('lowerarm_l',(1,0,0),-25*w)
  for p in rig.pose.bones:p.keyframe_insert('rotation_quaternion',frame=f,group=p.name);p.keyframe_insert('location',frame=f,group=p.name)
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/(clip+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(clip+'.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
 print('VEHICLE_ACTION_READY',clip)
