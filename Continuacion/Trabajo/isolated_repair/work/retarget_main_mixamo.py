import bpy,math
from pathlib import Path
from mathutils import Quaternion,Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Animation';out.mkdir(exist_ok=True)
for clip in ['Walk','Jump']:
 bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'));target=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');sc=bpy.context.scene
 target.animation_data.action=bpy.data.actions['Walk_InPlace'];sc.frame_set(1);bpy.context.view_layer.update();neutral={b.name:b.matrix.to_quaternion().copy() for b in target.pose.bones};target.animation_data_clear()
 for b in target.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion();b.location=(0,0,0);b.scale=(1,1,1)
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(root/'outputs/DeliveryArt/Mixamo'/f'{clip}.fbx'));source=next(o for o in bpy.data.objects if o not in before and o.type=='ARMATURE');end=int(source.animation_data.action.frame_range[1]);sc.frame_start=1;sc.frame_end=end;sc.render.fps=30
 mapping={'pelvis':'Hips','spine_01':'Spine','spine_02':'Spine1','spine_03':'Spine2','neck_01':'Neck','head':'Head'}
 for side,src in [('l','Left'),('r','Right')]:
  for a,b in [('clavicle','Shoulder'),('upperarm','Arm'),('lowerarm','ForeArm'),('hand','Hand'),('thigh','UpLeg'),('calf','Leg'),('foot','Foot'),('ball','ToeBase')]:mapping[a+'_'+side]=src+b
 basis=source.matrix_world.to_quaternion();sc.frame_set(1);references={n:basis@source.pose.bones['mixamorig:'+sn].matrix.to_quaternion() for n,sn in mapping.items()}
 # The reference is the protagonist's authored locomotion pose, not the Mixamo T-pose.
 for f in range(1,end+1):
  sc.frame_set(f)
  for n,sn in mapping.items():
   b=target.pose.bones[n];q=basis@source.pose.bones['mixamorig:'+sn].matrix.to_quaternion();desired=q@references[n].inverted()@neutral[n]
   local=b.parent.matrix.to_quaternion().inverted()@desired if b.parent else desired;rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion()
   b.rotation_quaternion=rest.inverted()@local;b.keyframe_insert('rotation_quaternion',frame=f,group=n);bpy.context.view_layer.update()
  rootbone=target.pose.bones['root'];rootbone.location=(0,0,0);bpy.context.view_layer.update()
  mesh=next(o for o in before if o.type=='MESH' and o.parent==target);evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floor=min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices)
  rootbone.location=rootbone.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-floor));rootbone.keyframe_insert('location',frame=f,group='root');bpy.context.view_layer.update()
 target.animation_data.action.name='AN_Mixamo'+clip
 for o in list(bpy.data.objects):
  if o not in before:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
 bpy.ops.wm.save_as_mainfile(filepath=str(out/f'AN_Mixamo{clip}.blend'))
 bpy.ops.export_scene.fbx(filepath=str(out/f'AN_Mixamo{clip}.fbx'),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
 print('MAIN_RETARGET',clip,end)
