import bpy, math, sys
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Progression'
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for name,color in {'Paint':(.04,.65,.88,1),'Rubber':(.018,.025,.038,1),'Steel':(.42,.48,.55,1),'Chrome':(.75,.85,.9,1),'Orange':(1,.28,.04,1),'Lamp':(1,.94,.65,1),'Red':(.9,.025,.07,1),'Shell':(.032,.044,.071,1),'Edge':(.10,.14,.21,1)}.items():
 m=bpy.data.materials.new('Voxel_'+name);m.diffuse_color=color;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.72;mats[name]=m
def box(name,p,s,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat]);return o
def beam(name,a,b,t,mat):
 a,b=Vector(a),Vector(b);steps=max(1,math.ceil((b-a).length/min(.04,t*.75)))
 for i in range(steps+1):o=box(name,a.lerp(b,i/steps),(t,t,t),mat)
 return o
def bike(stage):
 # Frame as short stepped rods, block forks, seat and cockpit. Front = +X.
 points=[(-.62,0,.33),(-.12,0,.72),(.38,0,.77),(.06,0,.33)]
 for a,b in [(0,1),(1,2),(2,3),(3,0),(1,3)]:beam('Frame',points[a],points[b],.055 if stage<2 else .075,'Paint')
 for y in [-.06,.06]:beam('Fork',(.38,y,.77),(.62,y,.33),.04,'Steel')
 box('Seat',(-.13,0,.84),(.26,.21,.08),'Rubber');beam('Seatpost',(-.12,0,.72),(-.13,0,.84),.04,'Steel')
 box('Handlebar',(.36,0,1.11),(.09,.50,.05),'Steel');beam('Stem',(.38,0,.77),(.36,0,1.11),.04,'Steel')
 for y in [-.24,.24]:box('Grip',(.36,y,1.11),(.13,.14,.075),'Rubber')
 if stage>=3:
  for x in [-.62,.62]:box('SpeedDisc',(x,.065,.33),(.23,.025,.23),'Chrome')
 if stage>=4:
  box('BikeEngine',(0,0,.46),(.34,.24,.23),'Steel');box('Battery',(.13,0,.6),(.16,.20,.19),'Orange');box('EngineLamp',(.04,-.13,.49),(.10,.015,.055),'Lamp')
def pedal():
 box('PedalPlatform',(0,0,0),(.23,.17,.055),'Orange')
 for x in [-.075,0,.075]:box('PedalGrip',(x,0,.035),(.025,.16,.025),'Rubber')
 box('Axle',(0,-.08,0),(.035,.13,.035),'Chrome')
def moto(stage):
 box('Engine',(0,0,.57),(.51,.35,.31),'Steel');box('Tank',(.24,0,.85),(.36,.38,.25),'Paint')
 box('Seat',(-.25,0,.80),(.49,.39,.11),'Rubber');box('Tail',(-.51,0,.79),(.22,.38,.22),'Paint');box('TailLamp',(-.63,0,.83),(.03,.23,.09),'Red')
 for y in [-.10,.10]:beam('FrontFork',(.5,y,.98),(.62,y,.33),.06,'Chrome')
 box('Cockpit',(.47,0,.99),(.18,.37,.22),'Paint');box('Headlamp',(.57,0,1.02),(.035,.25,.15),'Lamp')
 box('Handlebar',(.36,0,1.11),(.08,.50,.055),'Steel')
 for y in [-.24,.24]:box('Grip',(.36,y,1.11),(.13,.13,.085),'Rubber');box('Footpeg',(-.10,y,.33),(.24,.16,.07),'Steel')
 box('Exhaust',(-.30,-.27,.40),(.52,.12,.12),'Steel')
 if stage>=1:box('Turbo',(.03,-.23,.58),(.23,.13,.23),'Orange')
 if stage>=2:
  for y in [-.21,.21]:box('Fairing',(.24,y,.73),(.51,.065,.30),'Paint');box('SideStripe',(.24,y*1.18,.78),(.40,.03,.05),'Orange')
 if stage>=3:box('Cylinder',(0,0,.60),(.55,.42,.37),'Steel')
 if stage>=4:
  for x in [-.16,0,.16]:box('Injector',(x,-.23,.75),(.08,.07,.15),'Chrome')
 if stage>=5:box('SportExhaust',(-.35,-.30,.40),(.68,.16,.16),'Rubber');box('SportIntake',(.06,0,.66),(.36,.45,.12),'Orange')
def wheels():
 for x in [-.62,.62]:
  for i in range(24):
   a=2*math.pi*i/24;box('Tire',(x+.30*math.sin(a),0,.33+.30*math.cos(a)),(.09,.14,.09),'Rubber')
  for a in [0,math.pi/2]:beam('Spoke',(x-.26*math.sin(a),0,.33-.26*math.cos(a)),(x+.26*math.sin(a),0,.33+.26*math.cos(a)),.035,'Steel')
def setup_render():
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=384;scene.render.resolution_y=256;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.world.color=(.30,.30,.30)
 bpy.ops.object.camera_add(location=(2.5,-3.5,2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.1;scene.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(1,-2,4));bpy.context.object.data.energy=350;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
 scene.view_settings.view_transform='Standard'
def export(name,render=True,addwheels=False):
 if '--no-render' in sys.argv:render=False
 mesh=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in mesh:o.select_set(True)
 bpy.context.view_layer.objects.active=mesh[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 # FBX origin must remain the rider's floor, rather than one component's center.
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 bpy.ops.export_scene.fbx(filepath=str(out/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z')
 if render:
  if addwheels:wheels()
  bpy.context.scene.render.filepath=str(out/('T_'+name+'.png'));bpy.ops.render.render(write_still=True)
 for ob in list(bpy.context.scene.objects):
  if ob.type=='MESH':bpy.data.objects.remove(ob,do_unlink=True)
setup_render()
for i in range(5):bike(i);export('SM_BikeStage'+str(i),addwheels=True)
pedal();export('SM_LuxuryPedal',render=False)
for i in range(6):moto(i);export('SM_MotoStage'+str(i),addwheels=True)
# Real stepped phone shell. Screen is an aperture in the HUD render, not a flat UMG rectangle.
for side in [-1,1]:
 box('Rail',(side*.036,0,.080),(.010,.016,.138),'Shell');box('Lip',(side*.032,-.009,.080),(.004,.003,.132),'Edge')
box('Top',(0,0,.151),(.062,.016,.014),'Shell');box('Bottom',(0,0,.009),(.062,.016,.014),'Shell')
for x in [-.030,.030]:
 for z in [.009,.151]:box('Corner',(x,0,z),(.014,.016,.014),'Shell')
for x in [-.032,.032]:
 for z in [.022,.138]:box('Step',(x,0,z),(.009,.016,.012),'Shell')
for x in [-.009,0,.009]:box('Speaker',(x,-.009,.152),(.004,.002,.003),'Chrome')
box('SideKey',(.043,0,.105),(.004,.014,.026),'Orange');box('Power',(-.043,0,.12),(.004,.014,.012),'Paint');box('Home',(0,-.009,.008),(.015,.002,.004),'Orange')
back=box('Back',(0,.006,.080),(.071,.004,.144),'Shell')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=back;bpy.ops.object.join();o=bpy.context.object;o.name='SM_UrbanPhoneVoxel';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SM_UrbanPhoneVoxel.blend'));bpy.ops.export_scene.fbx(filepath=str(out/'SM_UrbanPhoneVoxel.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z')
# Hide the rear plate polygons only for the transparent front image.
for poly in o.data.polygons:
 if poly.center.y>.003:poly.material_index=0
# Easier: render the front shell before the rear plate is visible by camera clipping.
cam=bpy.context.scene.camera;cam.location=(0,-1,.08);cam.rotation_euler=(Vector((0,0,.08))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.174
# Remove rear plate geometry in a temporary bmesh after saving the complete editable asset.
import bmesh
bm=bmesh.new();bm.from_mesh(o.data);verts=[v for v in bm.verts if v.co.y>=.0039 and abs(v.co.x)<.0356 and .0079<v.co.z<.1521];bmesh.ops.delete(bm,geom=verts,context='VERTS');bm.to_mesh(o.data);bm.free()
scene=bpy.context.scene;scene.render.resolution_x=420;scene.render.resolution_y=680;scene.render.filepath=str(out/'T_PhoneShell.png');bpy.ops.render.render(write_still=True)
print('PROGRESSION_ART_READY',flush=True)

