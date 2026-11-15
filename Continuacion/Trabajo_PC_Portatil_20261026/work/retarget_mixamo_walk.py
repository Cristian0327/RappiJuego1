import bpy,math
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/People'
for name in ['CustomerStudent','CustomerOffice','CustomerNeighbor']:
 bpy.ops.wm.open_mainfile(filepath=str(out/('SK_'+name+'.blend')));target=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');target.animation_data_clear()
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(root/'outputs/DeliveryArt/Mixamo/Walk.fbx'));source=next(o for o in bpy.data.objects if o not in before and o.type=='ARMATURE');sc=bpy.context.scene;sc.frame_start=1;sc.frame_end=42;sc.render.fps=30
 mapping={'pelvis':'Hips','spine':'Spine2','head':'Head'}
 for side,src in [('L','Right'),('R','Left')]:
  for a,b in [('thigh','UpLeg'),('shin','Leg'),('foot','Foot'),('upperarm','Arm'),('forearm','ForeArm'),('hand','Hand')]:mapping[a+'_'+side]=src+b
 sc.frame_set(1);basis=source.matrix_world.to_quaternion();rests={n:(basis@source.data.bones['mixamorig:'+s].matrix_local.to_quaternion()) for n,s in mapping.items()}
 # Arm reference is the natural first frame, because target binds with arms lowered.
 for n,s in mapping.items():
  if n.startswith(('upperarm','forearm','hand')):rests[n]=basis@source.pose.bones['mixamorig:'+s].matrix.to_quaternion()
 for f in range(1,43):
  sc.frame_set(f)
  for n,s in mapping.items():
   b=target.pose.bones[n];q=basis@source.pose.bones['mixamorig:'+s].matrix.to_quaternion();delta=q@rests[n].inverted();desired=delta@b.bone.matrix_local.to_quaternion()
   if b.parent:local=b.parent.matrix.to_quaternion().inverted()@desired;restlocal=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion()
   else:local=desired;restlocal=b.bone.matrix_local.to_quaternion()
   b.rotation_mode='QUATERNION';b.rotation_quaternion=restlocal.inverted()@local;b.keyframe_insert('rotation_quaternion',frame=f,group=n);bpy.context.view_layer.update()
  rootbone=target.pose.bones['root'];rootbone.location=(0,0,0);bpy.context.view_layer.update()
  mesh=next(o for o in before if o.type=='MESH' and o.parent==target);evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());floor=min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices)
  rootbone.location=rootbone.bone.matrix_local.to_quaternion().inverted()@Vector((0,0,-floor));rootbone.keyframe_insert('location',frame=f,group='root');bpy.context.view_layer.update()
 target.animation_data.action.name='Mixamo_Walk';sc['animation_source']='Mixamo / Unarmed Walk Forward / In Place / 30 FPS'
 for o in list(bpy.data.objects):
  if o in before:continue
  bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
 bpy.ops.wm.save_as_mainfile(filepath=str(out/('A_'+name+'_Walk.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/('A_'+name+'_Walk.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
print('MIXAMO_RETARGETED_THREE_CUSTOMERS')
