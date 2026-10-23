import bpy, math, json
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/RigComparison';out.mkdir(exist_ok=True)
name='CustomerStudent';bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/DeliveryArt/People/SK_CustomerStudent.blend'));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
# Match articulation pivots to the actual cuts of the original voxel clothes.
bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for side,sgn in [('L',-1),('R',1)]:
 x=sgn*.105
 for bone,head,tail in [('thigh',(x,0,.735),(x,0,.46125)),('shin',(x,0,.46125),(x,0,.23625)),('foot',(x,0,.23625),(x,-.16,.10)),('upperarm',(sgn*.24,0,1.20),(sgn*.28,-.01,.99)),('forearm',(sgn*.28,-.01,.99),(sgn*.28,-.01,.78)),('hand',(sgn*.28,-.01,.78),(sgn*.28,-.025,.66))]:
  b=rig.data.edit_bones[bone+'_'+side];b.head=head;b.tail=tail
bpy.ops.object.mode_set(mode='OBJECT')
# Internal faceted joint volumes, fully rigid, matching garment/skin palette.
parts=[mesh]
for side,sgn in [('L',-1),('R',1)]:
 for bone,pos,radius,depth,color in [('thigh',(sgn*.105,0,.46125),.080,.18,19),('shin',(sgn*.105,0,.23625),.075,.18,18),('upperarm',(sgn*.28,-.01,.99),.078,.18,20),('forearm',(sgn*.28,-.01,.78),.065,.15,20)]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=1,location=pos);o=bpy.context.object;o.scale=(radius,depth/2,radius);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mesh.data.materials[0]);uv=o.data.uv_layers.active;uv.name=mesh.data.uv_layers.active.name
  for loop in uv.data:loop.uv=((color%8+.5)/8,(color//8+.5)/8)
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
  hip=rig.pose.bones['thigh_'+side].head.copy();ankle=Vector((sgn*.105,y,.23625+lift));knee=solve(hip,ankle,.27375,.225)
  orient('thigh_'+side,hip,knee);orient('shin_'+side,knee,ankle);orient('foot_'+side,ankle,ankle+Vector((0,-.16,-.13625)))
  shoulder=rig.pose.bones['upperarm_'+side].head.copy();swing=.11*math.sin(2*math.pi*phase);elbow=shoulder+Vector((sgn*.025,swing,-.205));wrist=elbow+Vector((sgn*.007,-.045,-.204))
  orient('upperarm_'+side,shoulder,elbow);orient('forearm_'+side,elbow,wrist);orient('hand_'+side,wrist,wrist+Vector((0,-.015,-.12)))
 for b in rig.pose.bones:
  b.keyframe_insert('location',frame=f);b.keyframe_insert('rotation_quaternion',frame=f);b.keyframe_insert('scale',frame=f)
rig.animation_data.action.name='Blender_PlantedWalk';sc['method']='Blender manual pivots, closed rigid panels, internal joints and planted-foot IK'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Blender_Corrected.blend'))
print('MANUAL_RIG_COMPARISON_READY')
