import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');out=r/'outputs/DeliveryArt/AnimationRebuild';bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH');rig.animation_data_clear()
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='QUATERNION'
def global_rotation(b,q):
 p=b.parent.matrix.to_quaternion() if b.parent else Quaternion();rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion();b.rotation_quaternion=rest.inverted()@p.inverted()@q;bpy.context.view_layer.update()
def aim(b,direction):global_rotation(b,(b.bone.tail_local-b.bone.head_local).normalized().rotation_difference(direction.normalized())@b.bone.matrix_local.to_quaternion())
def ik(upper,lower,target,pole):
 a=rig.pose.bones[upper];b=rig.pose.bones[lower];start=a.head.copy();delta=Vector(target)-start;length=min(delta.length,(a.bone.length+b.bone.length)*.995);direction=delta.normalized();along=(a.bone.length**2-b.bone.length**2+length**2)/(2*length);height=math.sqrt(max(0,a.bone.length**2-along**2));p=Vector(pole);p=(p-direction*p.dot(direction)).normalized();joint=start+direction*along+p*height;aim(a,joint-start);aim(b,Vector(target)-b.head)
sc=bpy.context.scene;sc.frame_start=1;sc.frame_end=31;sc.render.fps=30
for f in range(1,32):
 for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
 root=rig.pose.bones['root'];root.location=root.bone.matrix_local.to_quaternion().inverted()@Vector((0,9,24.75));bpy.context.view_layer.update()
 for name in ['spine_01','spine_02','spine_03']:
  b=rig.pose.bones[name];global_rotation(b,Quaternion((1,0,0),math.radians(18+math.sin((f-1)/30*math.tau)*.3))@b.bone.matrix_local.to_quaternion())
 for sign,side in [(1,'l'),(-1,'r')]:
  ik('thigh_'+side,'calf_'+side,(sign*24,18,56.75),(0,-1,0));global_rotation(rig.pose.bones['foot_'+side],rig.pose.bones['foot_'+side].bone.matrix_local.to_quaternion());ik('upperarm_'+side,'lowerarm_'+side,(sign*24,-36,111),(sign*.2,0,-1))
  global_rotation(rig.pose.bones['hand_'+side],rig.pose.bones['hand_'+side].parent.matrix.to_quaternion())
 global_rotation(rig.pose.bones['head'],rig.pose.bones['head'].bone.matrix_local.to_quaternion())
 for b in rig.pose.bones:b.keyframe_insert('rotation_quaternion',frame=f,group=b.name);b.keyframe_insert('location',frame=f,group=b.name)
rig.animation_data.action.name='AN_HeroMotoRide_Rebuilt';rig.name='Armature';bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/'AN_HeroMotoRide_Rebuilt.blend'));bpy.ops.export_scene.fbx(filepath=str(out/'AN_HeroMotoRide_Rebuilt.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z');print('HEROMOTORIDE_PASS',flush=True)
