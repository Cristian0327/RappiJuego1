import bpy,math
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Cargo';out.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/unreal_v2/VoxelExplorer_GameRig.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear()
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
hero=next(o for o in bpy.context.scene.objects if o.type=='MESH');hero.hide_render=True
materials={}
for name,c in {'CargoInk':(.025,.04,.055,1),'CargoTeal':(.015,.38,.43,1),'CargoOrange':(.95,.22,.025,1),'CargoReflector':(.83,.86,.70,1),'CargoMetal':(.26,.29,.30,1)}.items():
 m=bpy.data.materials.new(name);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.76;materials[name]=m
parts=[]
def box(n,p,s,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(materials[mat]);parts.append(o);return o
def pack(cx,cy,cz,w,d,h):
 box('Stepped shell',(cx,cy,cz),(w-4,d,h),'CargoInk');box('Stepped side',(cx,cy,cz),(w,d-4,h-4),'CargoTeal');box('Lid',(cx,cy,cz+h/2),(w-2,d-2,3),'CargoInk')
 for x in [-w/2+5,w/2-5]:
  box('Load strap',(cx+x,cy+d/2,cz),(3,1.5,h),'CargoInk');box('Latch',(cx+x,cy+d/2+1,cz+6),(5,2,5),'CargoMetal');box('Latch center',(cx+x,cy+d/2+2.2,cz+6),(2,1,2),'CargoOrange')
 box('Reflective band',(cx,cy+d/2+.6,cz-5),(w-12,1.5,3),'CargoReflector')
 for z in [-h/2+4,h/2-5]:box('Stitched seam',(cx,cy+d/2+.6,cz+z),(w-5,1,1),'CargoOrange')
 box('Carry handle',(cx,cy,cz+h/2+3),(10,3,3),'CargoMetal')
assets=[]
for name,bone in [('CargoBackpack','spine_03'),('CargoWaist','pelvis'),('CargoPanniers',None)]:
 parts=[]
 if name=='CargoBackpack':
  pack(0,39,95,44,24,44)
  for x in [-24,24]:box('Bottle pocket',(x,37,84),(6,14,17),'CargoInk');box('Pocket orange lip',(x,37,93),(7,15,2),'CargoOrange')
 elif name=='CargoWaist':
  # Hero faces -Y in the Blender source; the waist pouch sits in front.
  pack(0,-19,72,32,13,16)
  for x in [-21,21]:box('Waist belt',(x,0,75),(3,32,4),'CargoInk')
 else:
  for side in [-1,1]:
   pack(-54,side*40,76,36,24,37);box('Mounting bracket',(-50,side*26,77),(34,3,6),'CargoMetal')
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=('SK_' if bone else 'SM_')+name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 if bone:
  obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))),1,'REPLACE');mod=obj.modifiers.new('Rigid accessory','ARMATURE');mod.object=rig;obj.parent=rig
  rig.select_set(True)
 bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(out/(obj.name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'} if bone else {'MESH'},add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,axis_forward='-Y',axis_up='Z')
 assets.append(obj);obj.hide_render=True
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=712;sc.render.resolution_y=352;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.view_settings.view_transform='Standard'
for o in list(sc.objects):
 if o.type in {'LIGHT','CAMERA'}:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.camera_add();camera=bpy.context.object;camera.data.type='ORTHO';sc.camera=camera
for pos,power in [((100,120,240),700000),((-100,-80,190),500000)]:
 bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.size=150;l.rotation_euler=(Vector((0,0,90))-l.location).to_track_quat('-Z','Y').to_euler()
for obj in assets:
 obj.hide_render=False;center=sum((obj.matrix_world@Vector(c) for c in obj.bound_box),Vector())/8;camera.location=center+Vector((100,180,95));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=130 if 'Panniers' in obj.name else 100
 sc.render.filepath=str(out/('T_'+obj.name[3:]+'.png'));bpy.ops.render.render(write_still=True);obj.hide_render=True
hero.hide_render=False
for obj in assets:obj.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(out/'VoxelExplorer_CargoLoadout.blend'))
print('CARGO_MODELS_AUTHORED_ON_ORIGINAL_RIG')
