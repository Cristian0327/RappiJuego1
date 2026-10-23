import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/AnimationRebuild';reports=[]
for role in ['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']:
 bpy.ops.wm.open_mainfile(filepath=str(out/('AN_'+role+'Idle_Rebuilt.blend')));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH');sc=bpy.context.scene
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 height=max(v.co.z for v in mesh.data.vertices)-min(v.co.z for v in mesh.data.vertices)
 def rotate(b,q):
  parent=b.parent.matrix.to_quaternion() if b.parent else Quaternion();rest=b.parent.bone.matrix_local.to_quaternion().inverted()@b.bone.matrix_local.to_quaternion() if b.parent else b.bone.matrix_local.to_quaternion();b.rotation_quaternion=rest.inverted()@parent.inverted()@q;bpy.context.view_layer.update()
 def aim(b,d):rotate(b,(b.bone.tail_local-b.bone.head_local).normalized().rotation_difference(d.normalized())@b.bone.matrix_local.to_quaternion())
 def ik(a,b,target,pole):
  start=a.head.copy();delta=target-start;length=min(delta.length,(a.bone.length+b.bone.length)*.99);direction=delta.normalized();along=(a.bone.length**2-b.bone.length**2+length**2)/(2*length);alt=math.sqrt(max(0,a.bone.length**2-along**2));p=Vector(pole);p=(p-direction*p.dot(direction)).normalized();joint=start+direction*along+p*alt;aim(a,joint-start);aim(b,target-b.head)
 upper=[b for b in rig.pose.bones if b.name.startswith('upperarm')];end=sc.frame_end
 for frame in range(1,end+1):
  sc.frame_set(frame);bpy.context.view_layer.update();phase=(frame-1)/max(1,end-1)*math.tau*2
  for a in upper:
   suffix=a.name[len('upperarm'):];b=rig.pose.bones['forearm'+suffix];sign=1 if a.bone.head_local.x>0 else -1
   active=role in ['Cashier','Chef','TechClerk','Pharmacist','Florist'] or sign>0
   if not active:continue
   wave=math.sin(phase+(0 if sign>0 else math.pi));front=.18;drop=.22;x=.075
   if role=='Cashier':front+=.025*wave;x+=.035*wave
   elif role=='Chef':front+=.025*math.cos(phase);x+=.025*wave
   elif role=='TechClerk':drop+=.006*wave
   elif role=='Pharmacist':drop=.14 if sign>0 else .23;front=.15+.012*wave
   elif role=='Florist':x=.055+.012*wave;drop=.21+.008*wave
   else:drop=.17;front=.13+.008*wave;x=.04
   target=Vector((sign*height*x,-height*front,a.head.z-height*drop));ik(a,b,target,(sign,.1,-1))
   a.keyframe_insert('rotation_quaternion',frame=frame,group=a.name);b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name)
 name='AN_'+role+'Work_Rebuilt';rig.animation_data.action.name=name;bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;sc['animation_source']='Mixamo breathing idle with newly authored Blender task gestures and anatomical arm IK';bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,axis_forward='-Y',axis_up='Z');reports.append({'role':role,'frames':end,'source':sc['animation_source']})
(out/'work_gesture_report.json').write_text(json.dumps(reports,indent=2));print('ALL_WORK_GESTURES_REBUILT_PASS',flush=True)
