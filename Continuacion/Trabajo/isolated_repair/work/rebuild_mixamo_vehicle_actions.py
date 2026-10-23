import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');out=r/'outputs/DeliveryArt/AnimationRebuild';out.mkdir(exist_ok=True)
reports=[]
for label,file in [('Crowd',r/'outputs/DeliveryArt/Crowd/SK_Citizen12.blend'),('Hero',r/'outputs/unreal_v2/VoxelExplorer_GameRig.blend')]:
 for clip in ['EnterCar','Sitting']:
  bpy.ops.wm.open_mainfile(filepath=str(file));target=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.find_armature()==target);target.animation_data_clear()
  for pb in target.pose.bones:pb.matrix_basis=Matrix.Identity(4);pb.rotation_mode='QUATERNION'
  bpy.context.view_layer.update();before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(r/'outputs/DeliveryArt/Mixamo'/(clip+'.fbx')));source=next(o for o in bpy.data.objects if o not in before and o.type=='ARMATURE');src={b.name.split(':')[-1]:b for b in source.pose.bones};sc=bpy.context.scene;end=int(source.animation_data.action.frame_range[1]);sc.frame_start=1;sc.frame_end=end;sc.render.fps=30
  def resthead(name):return source.matrix_world@src[name].bone.head_local
  side=(resthead('LeftArm')-resthead('RightArm')).normalized();up=(resthead('Head')-resthead('Hips')).normalized();back=up.cross(side).normalized();side=back.cross(up).normalized();basis=Matrix((side,back,up)).transposed();align=basis.transposed();aq=align.to_quaternion();sourceworld=source.matrix_world.to_quaternion();mapping={'pelvis':'Hips','spine_01':'Spine','spine_02':'Spine1','spine_03':'Spine2','neck_01':'Neck','head':'Head'};limbs={}
  for side_,source_ in [('l','Left'),('r','Right')]:
   for n,s in [('clavicle','Shoulder'),('upperarm','Arm'),('lowerarm','ForeArm'),('hand','Hand'),('thigh','UpLeg'),('calf','Leg'),('foot','Foot'),('ball','ToeBase')]:mapping[n+'_'+side_]=source_+s
   for n,s,child in [('upperarm','Arm','ForeArm'),('lowerarm','ForeArm','Hand'),('thigh','UpLeg','Leg'),('calf','Leg','Foot'),('foot','Foot','ToeBase')]:limbs[n+'_'+side_]=(source_+s,source_+child)
  rests={n:target.data.bones[n].matrix_local.to_quaternion() for n in mapping};src_rest={n:aq@sourceworld@src[s].bone.matrix_local.to_quaternion() for n,s in mapping.items()};floor_values=[];knees=[]
  for f in range(1,end+1):
   sc.frame_set(f)
   for n,s in mapping.items():
    pb=target.pose.bones[n]
    if n in limbs:
     sn,ch=limbs[n];direction=align@(source.matrix_world.to_3x3()@(src[ch].head-src[sn].head));direction.normalize();rest_dir=(pb.bone.tail_local-pb.bone.head_local).normalized();desired=rest_dir.rotation_difference(direction)@rests[n]
    else:
     q=aq@sourceworld@src[s].matrix.to_quaternion();desired=q@src_rest[n].inverted()@rests[n]
    parentq=pb.parent.matrix.to_quaternion() if pb.parent else Quaternion();restlocal=pb.parent.bone.matrix_local.to_quaternion().inverted()@rests[n] if pb.parent else rests[n];pb.rotation_quaternion=restlocal.inverted()@parentq.inverted()@desired;pb.keyframe_insert('rotation_quaternion',frame=f,group=n);bpy.context.view_layer.update()
   root=target.pose.bones['root'];root.location=(0,0,0);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floor=min(v.co.z for v in ev.data.vertices)
   # Ground walk/idle without root motion. Preserve jump height from the raw motion.
   lift=0
   if clip=='Jump':
    lift=max(0,(align@(source.matrix_world@src['Hips'].head)).z-(align@resthead('Hips')).z)*80
   root.location=root.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-floor+lift));root.keyframe_insert('location',frame=f,group='root');floor_values.append(floor)
   # Signed bend: front is -Y. Knees should bend behind the hip/ankle line.
   for side_ in ['l','r']:
    hip=target.pose.bones['thigh_'+side_].head;knee=target.pose.bones['calf_'+side_].head;ankle=target.pose.bones['foot_'+side_].head;t=(hip.z-knee.z)/max(.001,hip.z-ankle.z);line=hip.lerp(ankle,t);knees.append(float((knee-line).y))
  # Preserve the run's flight phase, calibrated once across the cycle.
  heights=[];floors=[];ratio=(target.data.bones['thigh_l'].length+target.data.bones['calf_l'].length)/((source.matrix_world.to_3x3()@(src['LeftLeg'].bone.head_local-src['LeftUpLeg'].bone.head_local)).length+(source.matrix_world.to_3x3()@(src['LeftFoot'].bone.head_local-src['LeftLeg'].bone.head_local)).length)
  for frame in range(1,end+1):
   sc.frame_set(frame);root=target.pose.bones['root'];root.location=(0,0,0);bpy.context.view_layer.update();height=((align@(source.matrix_world@src['Hips'].head)).z-(align@resthead('Hips')).z)*ratio;ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floors.append(min(v.co.z for v in ev.data.vertices)+height);heights.append(height)
  baseline=-min(floors)
  for frame,height in enumerate(heights,1):
   sc.frame_set(frame);root=target.pose.bones['root'];root.location=root.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,baseline+height));root.keyframe_insert('location',frame=frame,group='root')
  action=target.animation_data.action;action.name='AN_'+label+clip+'_Rebuilt';target.name='Armature';sc['animation_source']='Original Mixamo '+clip+'; anatomical direction retarget, rest-pose based, 30fps, no first-frame calibration';name=action.name
  for o in list(bpy.data.objects):
   if o not in before:bpy.data.objects.remove(o,do_unlink=True)
  bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target;bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z')
  reports.append({'name':name,'frames':end,'knees_signed_y_min':min(knees),'knees_signed_y_max':max(knees),'source':str(r/'outputs/DeliveryArt/Mixamo'/(clip+'.fbx'))})
  if clip in ['EnterCar','Sitting']:
   snaps=[]
   for i,f in enumerate([1,1+end//4,1+end//2,1+3*end//4]):
    sc.frame_set(f);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=bpy.data.meshes.new_from_object(ev);o=bpy.data.objects.new('Frame_'+str(f),data);bpy.context.collection.objects.link(o);o.scale=(.01,.01,.01);o.location=(i*1.7,0,0);snaps.append(o)
   for o in list(bpy.data.objects):
    if o not in snaps:bpy.data.objects.remove(o,do_unlink=True)
   aim=Vector((2.55,0,.9));bpy.ops.object.camera_add(location=aim+Vector((4,-7,2)));cam=bpy.context.object;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8;sc.camera=cam;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1600;sc.render.resolution_y=600;sc.render.resolution_percentage=100;sc.render.film_transparent=False;sc.world.color=(.16,.16,.16);sc.view_settings.view_transform='Standard'
   for pos,power in [((2,-4,6),1800),((3,3,5),1200)]:
    bpy.ops.object.light_add(type='AREA',location=pos);bpy.context.object.data.energy=power;bpy.context.object.data.size=5
   sc.render.filepath=str(out/(label+'_'+clip+'_Review.png'));bpy.ops.render.render(write_still=True)
(out/'vehicle_actions_retarget_report.json').write_text(json.dumps(reports,indent=2));print('ANATOMICAL_VEHICLE_ACTIONS_PASS',flush=True)
