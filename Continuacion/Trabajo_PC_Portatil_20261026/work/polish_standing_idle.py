import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');folder=r/'outputs/DeliveryArt/AnimationRebuild/Upright';out=folder/'Standing';out.mkdir(exist_ok=True);reports=[]
def align_bone(b,direction):
 current=(b.tail-b.head).normalized();desired=current.rotation_difference(direction.normalized())@b.matrix.to_quaternion();parent=b.parent.matrix.to_quaternion() if b.parent else Quaternion();rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion();b.rotation_quaternion=rest.inverted()@parent.inverted()@desired;bpy.context.view_layer.update()
def knee_angle(rig,names):
 h,k,a=[rig.pose.bones[x].head.copy() for x in names];return (k-h).angle(a-k)
for file in sorted(folder.glob('*Idle_Rebuilt.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(file));rig=next(x for x in bpy.data.objects if x.type=='ARMATURE');meshes=[x for x in bpy.data.objects if x.type=='MESH' and x.find_armature()==rig];assert meshes;scene=bpy.context.scene;legs=[]
 for side in (['l','r'] if 'thigh_l' in rig.pose.bones else ['L','R']):legs.append(['thigh_'+side,('calf_' if 'calf_'+side in rig.pose.bones else 'shin_')+side,'foot_'+side])
 poses=[]
 for frame in range(scene.frame_start,scene.frame_end+1):
  scene.frame_set(frame);bpy.context.view_layer.update();poses.append((frame,{b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in rig.pose.bones}))
 before=[];after=[];ground=[]
 for frame,pose in poses:
  scene.frame_set(frame)
  for b in rig.pose.bones:b.location,b.rotation_quaternion=pose[b.name]
  bpy.context.view_layer.update();feet={n[2]:rig.pose.bones[n[2]].matrix.to_quaternion().copy() for n in legs}
  for names in legs:
   before.append(math.degrees(knee_angle(rig,names)));thigh,calf,foot=[rig.pose.bones[n] for n in names];old=(thigh.tail-thigh.head).normalized();align_bone(thigh,old.slerp(Vector((0,0,-1)),.85));upper=(calf.head-thigh.head).normalized();lower=(foot.head-calf.head).normalized();angle=upper.angle(lower);target=min(math.radians(10),angle*.3)
   if angle>.00001:align_bone(calf,upper.slerp(lower,target/angle))
   parent=foot.parent.matrix.to_quaternion();rest=foot.parent.bone.matrix_local.to_quaternion().inverted()@foot.bone.matrix_local.to_quaternion();foot.rotation_quaternion=rest.inverted()@parent.inverted()@feet[names[2]];bpy.context.view_layer.update()
   for b in [thigh,calf,foot]:b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name)
   after.append(math.degrees(knee_angle(rig,names)))
  head=rig.pose.bones.get('head')
  if head:align_bone(head,Vector((0,0,1)));head.keyframe_insert('rotation_quaternion',frame=frame,group='head')
  root=rig.pose.bones['root'];root.location=(0,0,0);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();floor=min(v.co.z for mesh in meshes for v in mesh.evaluated_get(dg).data.vertices);root.location=root.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-floor));root.keyframe_insert('location',frame=frame,group='root');bpy.context.view_layer.update();ground.append(min(v.co.z for mesh in meshes for v in mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices))
  assert after[-1]<10.05,(file.name,frame,after[-1])
 assert max(abs(x) for x in ground)<.02,(file.name,min(ground),max(ground));scene['idle_posture_revision']='Original Mixamo idle with relaxed straight legs, neutral head and grounded feet; cane motion untouched';bpy.ops.wm.save_as_mainfile(filepath=str(out/file.name));bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.export_scene.fbx(filepath=str(out/(file.stem+'.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z');row={'clip':file.stem,'frames':len(poses),'before_max_knee_degrees':max(before),'after_max_knee_degrees':max(after),'minimum_floor':min(ground),'maximum_floor':max(ground)};reports.append(row);print('STANDING_IDLE '+json.dumps(row),flush=True)
(out/'standing_idle_validation.json').write_text(json.dumps(reports,indent=2));assert len(reports)==10;print('STANDING_IDLE_MIXAMO_POLISH_PASS clips=10',flush=True)
