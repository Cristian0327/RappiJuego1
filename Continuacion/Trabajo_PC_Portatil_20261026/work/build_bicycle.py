import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
BASE=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
OUT=BASE/'outputs/unreal_v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'VoxelExplorer_Unreal.blend'))
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH')
rig.animation_data_clear()
scene=bpy.context.scene;scene.render.fps=30;scene.frame_start=1;scene.frame_end=31
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.location=(0,0,0)
action=bpy.data.actions.new('BikePedal');action.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=action
def rot(n,axis,degrees):
 p=rig.pose.bones[n];p.rotation_quaternion=Quaternion(p.bone.matrix_local.to_3x3().inverted()@Vector(axis),math.radians(degrees))
def aim(n,target):
 bpy.context.view_layer.update();p=rig.pose.bones[n];m=p.matrix.copy();v=(p.tail-p.head).normalized();q=v.rotation_difference((Vector(target)-p.head).normalized());m=q.to_matrix().to_4x4()@m;m.translation=p.head;p.matrix=m;bpy.context.view_layer.update()
def two_bone(a,b,target,pole):
 bpy.context.view_layer.update();pa,pb=rig.pose.bones[a],rig.pose.bones[b];origin=pa.head.copy();target=Vector(target);d=(target-origin);L=d.length;u=d.normalized();l1=pa.length;l2=pb.length;L=min(L,l1+l2-.05);along=(l1*l1-l2*l2+L*L)/(2*L);height=math.sqrt(max(.001,l1*l1-along*along));v=Vector(pole)-origin;v=(v-u*v.dot(u)).normalized();joint=origin+u*along+v*height;aim(a,joint);aim(b,target)
for f in range(1,32):
 scene.frame_set(f)
 for p in rig.pose.bones:p.rotation_quaternion=(1,0,0,0);p.location=(0,0,0)
 rig.pose.bones['pelvis'].location=rig.pose.bones['pelvis'].bone.matrix_local.to_3x3().inverted()@Vector((0,9,11))
 rot('spine_01',(1,0,0),12);rot('spine_02',(1,0,0),6);rot('neck_01',(1,0,0),-10)
 for sign,s in [(1,'l'),(-1,'r')]:
  phase=(f-1)/30*2*math.pi+(0 if sign==1 else math.pi)
  # Feet follow opposed cranks; ankle sits above the pedal by the boot's height.
  two_bone('thigh_'+s,'calf_'+s,(sign*11,-8-11*math.cos(phase),49+11*math.sin(phase)),(sign*15,-70,60))
  p=rig.pose.bones['foot_'+s];m=p.bone.matrix_local.copy();m.translation=p.head;p.matrix=m;bpy.context.view_layer.update()
  two_bone('upperarm_'+s,'lowerarm_'+s,(sign*24,-36,111),(sign*60,-20,108))
  rot('hand_'+s,(1,0,0),-12)
 for p in rig.pose.bones:
  p.keyframe_insert('rotation_quaternion',frame=f,group=p.name)
  if p.name=='pelvis':p.keyframe_insert('location',frame=f,group=p.name)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(OUT/'AN_BikePedal.fbx'),use_selection=True,object_types={'ARMATURE'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_armature_deform_only=True,armature_nodetype='NULL',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
rig.animation_data.action=None
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'VoxelExplorer_GameRig.blend'),compress=True)

# Voxel bicycle in UE coordinates (+X front), native centimetres.
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
colors={'Teal':(.015,.62,.56,1),'Charcoal':(.025,.035,.035,1),'Steel':(.3,.38,.4,1),'Orange':(1,.19,.02,1),'Glow':(1,.8,.38,1)}
mats={}
for n,c in colors.items():
 m=bpy.data.materials.new(n);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;mats[n]=m
def cube(p,s,mat,parts):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat]);parts.append(o)
def line(a,b,width,mat,parts,step=6):
 a,b=Vector(a),Vector(b);n=math.ceil((b-a).length/min(step,width*.8))
 for i in range(n+1):cube(a.lerp(b,i/max(n,1)),(width,width,width),mat,parts)
parts=[]
for a,b in [((-62,0,33),(-15,0,69)),((-62,0,33),(0,0,34)),((0,0,34),(-15,0,69)),((-15,0,69),(38,0,80)),((38,0,80),(0,0,34)),((38,0,80),(62,0,33))]:line(a,b,5,'Teal',parts)
line((-15,0,69),(-18,0,78),5,'Steel',parts);cube((-22,0,80),(27,21,7),'Charcoal',parts)
line((38,0,80),(34,0,109),4,'Steel',parts);line((34,-24,109),(34,24,109),4,'Steel',parts)
for s in [-1,1]:cube((34,s*24,110),(12,12,7),'Charcoal',parts)
cube((38,0,107),(8,9,7),'Glow',parts)
def join(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
frame=join('SM_BicycleFrame',parts)
wheelparts=[]
for x in range(-32,33,4):
 for z in range(-32,33,4):
  d=math.sqrt((x+2)**2+(z+2)**2)
  if 25<d<33:cube((x+2,0,z+2),(4,9,4),'Charcoal',wheelparts)
for a,b in [((-25,0,0),(25,0,0)),((0,0,-25),(0,0,25)),((-18,0,-18),(18,0,18)),((-18,0,18),(18,0,-18))]:line(a,b,2,'Steel',wheelparts,4)
cube((0,0,0),(7,13,7),'Orange',wheelparts);wheel=join('SM_BicycleWheel',wheelparts)
opt=dict(use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',bake_anim=False)
for o in [frame,wheel]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),**opt)
wheel.location=(62,0,33);rear=wheel.copy();rear.data=wheel.data.copy();scene.collection.objects.link(rear);rear.location=(-62,0,33)
pedals=[]
for s in [-1,1]:cube((8+s*11,s*13,33),(20,13,5),'Orange',pedals)
whole=join('SM_Bicycle',[frame,wheel,rear]+pedals);bpy.ops.export_scene.fbx(filepath=str(OUT/'SM_Bicycle.fbx'),**opt)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'VoxelBicycle.blend'),compress=True)
print('BICYCLE_ASSETS_COMPLETE',flush=True)
