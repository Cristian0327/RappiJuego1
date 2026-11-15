import bpy,shutil
from pathlib import Path
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/AnimationRebuild';src=out/'AN_CrowdEnterCar_Rebuilt.blend';full=out/'AN_CrowdEnterCar_FullMixamo.blend'
if not full.exists():shutil.copy2(src,full)
bpy.ops.wm.open_mainfile(filepath=str(full));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');sc=bpy.context.scene;action=rig.animation_data.action;start,end=action.frame_range;poses=[]
for f in range(61):
 t=start+(end-start)*min(f/33,1);sc.frame_set(int(t),subframe=t-int(t));bpy.context.view_layer.update();poses.append({b.name:(b.rotation_quaternion.copy(),b.location.copy(),b.scale.copy()) for b in rig.pose.bones})
rig.animation_data.action=bpy.data.actions.new('AN_CrowdEnterCar_Rebuilt');sc.frame_start=1;sc.frame_end=61;sc.render.fps=30
for f,pose in enumerate(poses,1):
 sc.frame_set(f)
 for b in rig.pose.bones:
  b.rotation_mode='QUATERNION';b.rotation_quaternion,b.location,b.scale=pose[b.name];b.keyframe_insert('rotation_quaternion',frame=f,group=b.name);b.keyframe_insert('location',frame=f,group=b.name)
sc['animation_timing']='Full Mixamo action mapped to 1.1 seconds plus 0.9 second seated hold. Existing entering playback 0.55 completes action at 2 seconds; reverse playback holds during door opening then exits.'
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(src));bpy.ops.export_scene.fbx(filepath=str(out/'AN_CrowdEnterCar_Rebuilt.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z');print('ENTER_EXIT_TIMING_REBUILD_PASS',flush=True)
