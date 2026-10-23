import bpy,math,json
from pathlib import Path
from mathutils import Quaternion,Vector
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');base=r/'outputs/DeliveryArt/AnimationRebuild';out=r/'outputs/DeliveryArt/AnimationRebuild/CarAligned';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(base/'AN_HeroSitting_Rebuilt.blend'));rig=next(x for x in bpy.data.objects if x.type=='ARMATURE');bpy.context.scene.frame_set(1);bpy.context.view_layer.update();sit={b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in rig.pose.bones}
bpy.ops.wm.open_mainfile(filepath=str(base/'AN_HeroEnterCar_Rebuilt.blend'));rig=next(x for x in bpy.data.objects if x.type=='ARMATURE');s=bpy.context.scene;end=s.frame_end;frames=[]
for f in range(1,end+1):
 s.frame_set(f);frames.append({b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in rig.pose.bones})
rig.animation_data_clear()
for f,p in enumerate(frames,1):
 s.frame_set(f);t=(f-1)/(end-1);u=max(0,min(1,(t-.55)/.45));u=u*u*(3-2*u)
 for b in rig.pose.bones:
  l,q=p[b.name];sl,sq=sit[b.name];b.rotation_mode='QUATERNION';b.location=l.lerp(sl,u);b.rotation_quaternion=q.slerp(sq,u);b.keyframe_insert('location',frame=f);b.keyframe_insert('rotation_quaternion',frame=f)
# Turn toward the open driver door first, then face forward into the seat.
for f in range(1,end+1):
 s.frame_set(f);bpy.context.view_layer.update();t=(f-1)/(end-1);u=t*t*(3-2*t);v=(rig.pose.bones['hand_l'].head+rig.pose.bones['hand_r'].head)*.5-rig.pose.bones['pelvis'].head;current=math.atan2(v.y,v.x);desired=-math.pi+math.pi*.5*u;delta=(desired-current+math.pi)%(2*math.pi)-math.pi;root=rig.pose.bones['root'];rest=root.bone.matrix_local.to_quaternion();root.rotation_quaternion=rest.inverted()@Quaternion((0,0,1),delta)@rest@root.rotation_quaternion;root.keyframe_insert('rotation_quaternion',frame=f)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out/'AN_HeroEnterCar_Aligned.blend'));bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(out/'AN_HeroEnterCar_Aligned.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z')
print('CAR_ALIGNED_EXPORT_PASS')


