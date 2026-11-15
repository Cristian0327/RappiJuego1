import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/AnimationRebuild';reports=[]
exec(compile((r/'work/rebuild_crowd_bike_pedal.py').read_text(),str(r/'work/rebuild_crowd_bike_pedal.py'),'exec'))
for who in ['Hero','Crowd']:
 for vehicle in ['Bike','Moto']:
  bpy.ops.wm.open_mainfile(filepath=str(out/('AN_'+who+'Idle_Rebuilt.blend')));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');bpy.context.scene.frame_set(1);bpy.context.view_layer.update();start={b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in rig.pose.bones};origin=Vector((0 if who=='Hero' else -55,0,0));hands={side:rig.pose.bones['hand_'+side].head.copy()+origin for side in ['l','r']};feet={side:rig.pose.bones['foot_'+side].head.copy()+origin for side in ['l','r']}
  # Retain captured Mixamo weight shifts through the torso; adapt the supports to the vehicle.
  entryfile=out/('AN_'+who+'EnterCar'+('_FullMixamo' if who=='Crowd' else '_Rebuilt')+'.blend');bpy.ops.wm.open_mainfile(filepath=str(entryfile));entryrig=next(o for o in bpy.data.objects if o.type=='ARMATURE');entryscene=bpy.context.scene;entryend=entryscene.frame_end;entryposes=[]
  for i in range(73):
   entryscene.frame_set(1+round((entryend-1)*i/72));bpy.context.view_layer.update();entryposes.append({b.name:b.rotation_quaternion.copy() for b in entryrig.pose.bones})
  source='AN_'+who+('BikePedal' if vehicle=='Bike' else 'MotoRide')+'_Rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(out/source));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH');sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update();finish={b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in rig.pose.bones};targethands={side:rig.pose.bones['hand_'+side].head.copy() for side in ['l','r']};targetfeet={side:rig.pose.bones['foot_'+side].head.copy() for side in ['l','r']};rig.animation_data_clear();sc.frame_start=1;sc.frame_end=73;sc.render.fps=30
  def smooth(t,a=0,b=1):
   u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
  def rotate(b,q):
   parent=b.parent.matrix.to_quaternion() if b.parent else Quaternion();rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion();b.rotation_quaternion=rest.inverted()@parent.inverted()@q;bpy.context.view_layer.update()
  def aim(b,d):rotate(b,(b.bone.tail_local-b.bone.head_local).normalized().rotation_difference(d.normalized())@b.bone.matrix_local.to_quaternion())
  def ik(upper,lower,target,pole):
   a=rig.pose.bones[upper];b=rig.pose.bones[lower];point=a.head.copy();delta=target-point;length=max(.001,min(delta.length,(a.bone.length+b.bone.length)*.995));direction=delta.normalized();along=(a.bone.length**2-b.bone.length**2+length**2)/(2*length);height=math.sqrt(max(0,a.bone.length**2-along**2));p=Vector(pole);p=(p-direction*p.dot(direction)).normalized();joint=point+direction*along+p*height;aim(a,joint-point);aim(b,target-b.head)
  maxstep=0;previous=None;finite=True;worst=None
  for frame in range(1,74):
   sc.frame_set(frame);t=(frame-1)/72;body=smooth(t,.15,.9)
   for b in rig.pose.bones:
    l,q=start[b.name];el,eq=finish[b.name];b.rotation_mode='QUATERNION';b.rotation_quaternion=q.slerp(eq,body);b.location=l.lerp(el,body)
    if b.name in ['spine_01','spine_02','spine_03','neck_01','head']:b.rotation_quaternion=b.rotation_quaternion.slerp(entryposes[frame-1][b.name],math.sin(math.pi*t)*.25)
   root=rig.pose.bones['root'];root.location+=root.bone.matrix_local.to_quaternion().inverted()@(origin*(1-body));bpy.context.view_layer.update()
   if 0<t<1:
    for sign,side in [(1,'l'),(-1,'r')]:
     reach=smooth(t,.05,.4);ik('upperarm_'+side,'lowerarm_'+side,hands[side].lerp(targethands[side],reach),(sign*.2,0,-1));leg=smooth(t,.25,.85) if side=='l' else smooth(t,.6,1);ankle=feet[side].lerp(targetfeet[side],leg)
     if side=='l':ankle.z+=math.sin(math.pi*leg)*75
     ik('thigh_'+side,'calf_'+side,ankle,(sign*math.sin(math.pi*leg)*1.5,-1,0));rotate(rig.pose.bones['foot_'+side],rig.pose.bones['foot_'+side].bone.matrix_local.to_quaternion())
   for b in rig.pose.bones:b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name);b.keyframe_insert('location',frame=frame,group=b.name)
   points=[b.head.copy() for b in rig.pose.bones];finite=finite and all(math.isfinite(v) for p in points for v in p)
   if previous:
    step=max((a-b).length for a,b in zip(points,previous))
    if step>maxstep:maxstep=step;worst={'frame':frame,'bone':list(rig.pose.bones)[max(range(len(points)),key=lambda i:(points[i]-previous[i]).length)].name}
   previous=points
  # Smooth the swing's bend-plane transition, preserving exact endpoint poses.
  poseframes=[]
  for f in range(1,74):
   sc.frame_set(f);poseframes.append({b.name:b.rotation_quaternion.copy() for b in rig.pose.bones})
  for f in range(1,74):
   sc.frame_set(f)
   for b in rig.pose.bones:
    if f in [1,73]:q=poseframes[f-1][b.name]
    else:
     samples=[(math.exp(-.5*(k/2)**2),poseframes[max(0,min(72,f-1+k))][b.name]) for k in range(-5,6)];q=samples[0][1].copy();weight=samples[0][0]
     for w,quat in samples[1:]:q=q.slerp(quat,w/(weight+w));weight+=w
    b.rotation_quaternion=q;b.keyframe_insert('rotation_quaternion',frame=f,group=b.name)
  rawstep=maxstep;maxstep=0;previous=None
  for f in range(1,74):
   sc.frame_set(f);bpy.context.view_layer.update();points=[b.head.copy() for b in rig.pose.bones]
   if previous:maxstep=max(maxstep,max((a-b).length for a,b in zip(points,previous)))
   previous=points
  name='AN_'+who+'Mount'+vehicle;rig.animation_data.action.name=name;rig.name='Armature';bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z');reports.append({'name':name,'frames':73,'duration_seconds':2.4,'max_joint_step_cm':maxstep,'before_smoothing_cm':rawstep,'source':'Mixamo Idle + Entering Car; vehicle contacts and swing adapted in Blender','finite':finite,'worst':worst});assert finite and maxstep<10,reports[-1]
(out/'mount_animation_validation.json').write_text(json.dumps(reports,indent=2));print('FOUR_MOUNT_ANIMATIONS_AND_CROWD_PEDAL_READY',flush=True)
