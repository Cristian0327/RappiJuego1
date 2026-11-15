import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');src=r/'outputs/DeliveryArt/AnimationRebuild';out=src/'Upright';out.mkdir(exist_ok=True);report=[]
files=[src/('AN_'+who+clip+'_Rebuilt.blend') for who in ['Hero','Crowd'] for clip in ['Idle','Walk']]+[src/'AN_HeroRun_Rebuilt.blend']
files += [src/('AN_'+role+clip+'_Rebuilt.blend') for role in ['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor'] for clip in ['Walk','Idle']]
for file in files:
 if not file.exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(file));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');sc=bpy.context.scene;frames=range(sc.frame_start,sc.frame_end+1);before=[];after=[];chain=[n for n in ['spine_01','spine_02','spine_03','spine','neck_01','neck'] if n in rig.pose.bones]
 poses=[]
 for frame in frames:
  sc.frame_set(frame);bpy.context.view_layer.update();poses.append({b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in rig.pose.bones})
 for frame,pose in zip(frames,poses):
  sc.frame_set(frame)
  for b in rig.pose.bones:b.location,b.rotation_quaternion=pose[b.name]
  bpy.context.view_layer.update();base=rig.pose.bones[chain[0]].head.copy();v=rig.pose.bones['head'].head-base;before.append(math.degrees(v.angle(Vector((0,0,1)))))
  for name in chain:
   b=rig.pose.bones[name];direction=(b.tail-b.head).normalized();target=Vector((0,-math.sin(math.radians(3 if 'Idle' not in file.name else 1)),math.cos(math.radians(3 if 'Idle' not in file.name else 1))));correction=direction.rotation_difference(target);desired=correction@b.matrix.to_quaternion();parent=b.parent.matrix.to_quaternion() if b.parent else Quaternion();rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion();b.rotation_quaternion=rest.inverted()@parent.inverted()@desired;b.keyframe_insert('rotation_quaternion',frame=frame,group=name);bpy.context.view_layer.update()
  v=rig.pose.bones['head'].head-rig.pose.bones[chain[0]].head;after.append(math.degrees(v.angle(Vector((0,0,1)))))
 rig.name='Armature' if file.name.startswith(('AN_Hero','AN_Crowd')) else 'Rig_'+file.stem[3:].replace('Idle_Rebuilt','').replace('Walk_Rebuilt','');sc['posture_revision']='Mixamo motion retained; torso chain upright, elderly cane clip untouched';bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.wm.save_as_mainfile(filepath=str(out/file.name));bpy.ops.export_scene.fbx(filepath=str(out/(file.stem+'.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z');report.append({'clip':file.stem,'before_max_torso_degrees':max(before),'after_max_torso_degrees':max(after),'frames':len(poses)});print('UPRIGHT_CLIP '+file.stem,flush=True)
(out/'posture_validation.json').write_text(json.dumps(report,indent=2));print('UPRIGHT_POSTURE_SOURCES_PASS',flush=True)
