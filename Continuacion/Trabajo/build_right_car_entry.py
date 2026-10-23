import bpy,json
from pathlib import Path
from mathutils import Matrix
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');base=r/'outputs/DeliveryArt/AnimationRebuild/CarAligned';out=base;out.mkdir(exist_ok=True);mirror=Matrix.Diagonal((-1,1,1,1))
for kind in ['Car']:
 name='AN_HeroEnterCar_Aligned';bpy.ops.wm.open_mainfile(filepath=str(base/(name+'.blend')));rig=next(x for x in bpy.data.objects if x.type=='ARMATURE');s=bpy.context.scene;frames=[]
 for frame in range(s.frame_start,s.frame_end+1):
  s.frame_set(frame);bpy.context.view_layer.update();frames.append({b.name:b.matrix.copy() for b in rig.pose.bones})
 rig.animation_data_clear()
 for frame,pose in enumerate(frames,1):
  s.frame_set(frame)
  for b in rig.pose.bones:
   pair=b.name[:-2]+('_r' if b.name.endswith('_l') else '_l') if b.name.endswith(('_l','_r')) else b.name;b.rotation_mode='QUATERNION';b.matrix=mirror@pose.get(pair,pose[b.name])@mirror;bpy.context.view_layer.update();b.keyframe_insert('location',frame=frame);b.keyframe_insert('rotation_quaternion',frame=frame);b.keyframe_insert('scale',frame=frame)
 name='AN_HeroEnterCar_Right';rig.animation_data.action.name=name;bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z')
print('BOTH_SIDE_MOUNTS_EXPORTED')

