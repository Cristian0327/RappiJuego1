import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');out=r/'outputs/DeliveryArt/AnimationRebuild';bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/Crowd/SK_Citizen12.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH');rig.animation_data_clear()
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='QUATERNION'
def global_rotation(b,q):
 p=b.parent.matrix.to_quaternion() if b.parent else Quaternion();rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion();b.rotation_quaternion=rest.inverted()@p.inverted()@q;bpy.context.view_layer.update()
def aim(b,direction):global_rotation(b,(b.bone.tail_local-b.bone.head_local).normalized().rotation_difference(direction.normalized())@b.bone.matrix_local.to_quaternion())
def ik(upper,lower,target,pole):
 a=rig.pose.bones[upper];b=rig.pose.bones[lower];start=a.head.copy();delta=Vector(target)-start;length=min(delta.length,(a.bone.length+b.bone.length)*.995);direction=delta.normalized();along=(a.bone.length**2-b.bone.length**2+length**2)/(2*length);height=math.sqrt(max(0,a.bone.length**2-along**2));p=Vector(pole);p=(p-direction*p.dot(direction)).normalized();joint=start+direction*along+p*height;aim(a,joint-start);aim(b,Vector(target)-b.head)
sc=bpy.context.scene;sc.frame_start=1;sc.frame_end=60;sc.render.fps=30
for f in range(1,61):
 for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
 root=rig.pose.bones['root'];root.location=root.bone.matrix_local.to_quaternion().inverted()@Vector((0,25,27.25));bpy.context.view_layer.update()
 for name in ['spine_01','spine_02','spine_03']:
  b=rig.pose.bones[name];global_rotation(b,Quaternion((1,0,0),math.radians(25+math.sin(f/60*math.tau)*.3))@b.bone.matrix_local.to_quaternion())
 for sign,side in [(1,'l'),(-1,'r')]:
  ik('thigh_'+side,'calf_'+side,(sign*22,20,60.25),(0,-1,0));global_rotation(rig.pose.bones['foot_'+side],rig.pose.bones['foot_'+side].bone.matrix_local.to_quaternion());ik('upperarm_'+side,'lowerarm_'+side,(sign*28,-36,116),(sign*.2,0,-1))
  global_rotation(rig.pose.bones['hand_'+side],rig.pose.bones['hand_'+side].parent.matrix.to_quaternion())
 global_rotation(rig.pose.bones['head'],rig.pose.bones['head'].bone.matrix_local.to_quaternion())
 for b in rig.pose.bones:b.keyframe_insert('rotation_quaternion',frame=f,group=b.name);b.keyframe_insert('location',frame=f,group=b.name)
rig.animation_data.action.name='AN_CrowdMotoRide_Rebuilt';rig.name='Armature';bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/'AN_CrowdMotoRide_Rebuilt.blend'));bpy.ops.export_scene.fbx(filepath=str(out/'AN_CrowdMotoRide_Rebuilt.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z');print('VOXEL_MOTORCYCLE_RIDER_POSE_PASS',flush=True)
# Review in the coordinate system of the motorcycle authored in meters.
rig.rotation_euler.z=math.pi/2;rig.scale=(.01,.01,.01);sc.frame_set(1);bpy.context.view_layer.update()
with bpy.data.libraries.load(str(r/'outputs/DeliveryArt/Services/SK_MotoCivilBlue.blend'),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith(('SK_MotoCivilBlue','Armature'))]
for o in b.objects:
 if o:bpy.context.collection.objects.link(o)
aimpoint=Vector((0,0,1));bpy.ops.object.camera_add(location=(3,-5,2.7));cam=bpy.context.object;cam.rotation_euler=(aimpoint-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.5;sc.camera=cam;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1000;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.world.color=(.15,.15,.15);sc.view_settings.view_transform='Standard'
for pos,power in [((1,-3,5),1200),((-2,2,4),900)]:bpy.ops.object.light_add(type='AREA',location=pos);bpy.context.object.data.energy=power;bpy.context.object.data.size=4
sc.render.filepath=str(out/'Motorcycle_Rider_Review.png');bpy.ops.render.render(write_still=True)

