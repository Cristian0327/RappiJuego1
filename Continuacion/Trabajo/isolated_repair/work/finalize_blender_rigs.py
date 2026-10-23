characters=['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']
spec=[(.68,1.15,.40),(.72,1.24,.52),(.77,1.26,.36),(.75,1.23,.36),(.73,1.20,.38),(.77,1.26,.39),(.75,1.23,.39),(.72,1.24,.39)]
for role,character_name in enumerate(characters):
 leg,shoulder,width=spec[role];hip_x=.145 if role==1 else .105
 import bpy, math, json
 from pathlib import Path
 from mathutils import Vector,Matrix
 root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/People';out.mkdir(exist_ok=True)
 name=character_name;bpy.ops.wm.open_mainfile(filepath=str(out/('SK_'+name+'.blend')));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
 for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
 # Match articulation pivots to the actual cuts of the original voxel clothes.
 bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for side,sgn in [('L',-1),('R',1)]:
  x=sgn*hip_x
  for bone,head,tail in [('thigh',(x,0,leg-.035),(x,0,.46125)),('shin',(x,0,.46125),(x,0,.23625)),('foot',(x,0,.23625),(x,-.16,.10)),('upperarm',(sgn*width*.615,0,shoulder-.06),(sgn*width*.72,-.01,shoulder-.27)),('forearm',(sgn*width*.72,-.01,shoulder-.27),(sgn*width*.72,-.01,shoulder-.48)),('hand',(sgn*width*.72,-.01,shoulder-.48),(sgn*width*.72,-.025,shoulder-.60))]:
   b=rig.data.edit_bones[bone+'_'+side];b.head=head;b.tail=tail
 bpy.ops.object.mode_set(mode='OBJECT')
 # Internal faceted joint volumes, fully rigid, matching garment/skin palette.
 parts=[mesh]
 for side,sgn in [('L',-1),('R',1)]:
  for bone,pos,radius,depth,color in [('thigh',(sgn*hip_x,0,.46125),.080,.18,19),('shin',(sgn*hip_x,0,.23625),.075,.18,18),('upperarm',(sgn*width*.72,-.01,shoulder-.27),.078,.18,20),('forearm',(sgn*width*.72,-.01,shoulder-.48),.065,.15,20)]:
   bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=1,location=pos);o=bpy.context.object;o.scale=(radius,depth/2,radius);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mesh.data.materials[0])
   group=mesh.vertex_groups.get(bone+'_'+side)
   candidates=[p for p in mesh.data.polygons if any(any(g.group==group.index for g in mesh.data.vertices[v].groups) for v in p.vertices)]
   nearest=min(candidates,key=lambda p:(p.center-Vector(pos)).length)
   sample=mesh.data.uv_layers.active.data[nearest.loop_indices[0]].uv.copy()
   uv=o.data.uv_layers.active;uv.name=mesh.data.uv_layers.active.name
   for loop in uv.data:loop.uv=sample
   o.vertex_groups.new(name=bone+'_'+side).add(list(range(len(o.data.vertices))),1,'REPLACE');parts.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join()
 # Bake a slow walk with explicit stance contact. No target-space rotation copying.
 sc=bpy.context.scene;sc.render.fps=30;sc.frame_start=1;sc.frame_end=43
 rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
 def orient(n,head,tail):
  b=rig.pose.bones[n];r=rest[n];q=(r.to_3x3()@Vector((0,1,0))).rotation_difference((tail-head).normalized())@r.to_quaternion();b.matrix=Matrix.LocRotScale(head,q,Vector((1,1,1)));bpy.context.view_layer.update()
 def solve(hip,foot,l1,l2):
  delta=foot-hip;d=min(delta.length,l1+l2-.001);axis=delta.normalized();bend=Vector((0,-1,0));bend=(bend-axis*bend.dot(axis)).normalized();a=(l1*l1-l2*l2+d*d)/(2*d);return hip+axis*a+bend*math.sqrt(max(0,l1*l1-a*a))
 for f in range(1,44):
  sc.frame_set(f);t=(f-1)/42
  for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='QUATERNION'
  rig.pose.bones['root'].location.z=-.035+.005*math.cos(t*4*math.pi);bpy.context.view_layer.update()
  for side,sgn,offset in [('L',-1,0),('R',1,.5)]:
   phase=(t+offset)%1
   y=-.21+.42*phase/.6 if phase<.6 else .21-.42*(phase-.6)/.4
   lift=0 if phase<.6 else .065*math.sin(math.pi*(phase-.6)/.4)
   hip=rig.pose.bones['thigh_'+side].head.copy();ankle=Vector((sgn*hip_x,y,.23625+lift));knee=solve(hip,ankle,leg-.035-.46125,.225)
   orient('thigh_'+side,hip,knee);orient('shin_'+side,knee,ankle);orient('foot_'+side,ankle,ankle+Vector((0,-.16,-.13625)))
   shoulder=rig.pose.bones['upperarm_'+side].head.copy();swing=.11*math.sin(2*math.pi*phase);elbow=shoulder+Vector((sgn*.025,swing,-.205));wrist=elbow+Vector((sgn*.007,-.045,-.204))
   orient('upperarm_'+side,shoulder,elbow);orient('forearm_'+side,elbow,wrist);orient('hand_'+side,wrist,wrist+Vector((0,-.015,-.12)))
  for b in rig.pose.bones:
   b.keyframe_insert('location',frame=f);b.keyframe_insert('rotation_quaternion',frame=f);b.keyframe_insert('scale',frame=f)
 rig.animation_data.action.name='A_'+name+'_Walk';sc['method']='Blender manual pivots, closed rigid panels, internal joints and planted-foot IK'
 
 sc.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.wm.save_as_mainfile(filepath=str(out/('SK_'+name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/('SK_'+name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 mesh.select_set(False)
 bpy.ops.wm.save_as_mainfile(filepath=str(out/('A_'+name+'_Walk.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/('A_'+name+'_Walk.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
 rig.animation_data_clear();sc.frame_start=1;sc.frame_end=121
 for f in range(1,122,4):
  sc.frame_set(f);phase=(f-1)/120*math.tau
  for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4);b.rotation_mode='XYZ'
  rig.pose.bones['head'].rotation_euler[1]=math.sin(phase)*.025
  rig.pose.bones['head'].rotation_euler[2]=math.sin(phase)*.07
  for side,offset in [('L',0),('R',1.1)]:
   rig.pose.bones['upperarm_'+side].rotation_euler[0]=-.04-.035*math.sin(phase+offset)
   rig.pose.bones['forearm_'+side].rotation_euler[0]=-.05-.04*math.sin(phase+offset)
  for b in rig.pose.bones:b.keyframe_insert('rotation_euler',frame=f);b.keyframe_insert('location',frame=f)
 rig.animation_data.action.name='A_'+name+'_Work'
 bpy.ops.wm.save_as_mainfile(filepath=str(out/('A_'+name+'_Work.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/('A_'+name+'_Work.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
 print('CORRECTED_RIG',name)