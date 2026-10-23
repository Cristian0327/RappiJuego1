import bpy,math,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd';cat=json.loads((out/'catalog.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
for i,c in enumerate(cat):
 with bpy.data.libraries.load(str(out/('SK_'+c['name']+'.blend')),link=False) as (a,b):b.objects=list(a.objects)
 objects=[o for o in b.objects if o]
 for o in objects:bpy.context.collection.objects.link(o);o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
 rig=next(o for o in objects if o.type=='ARMATURE');rig.scale=(c['scale'],)*3;rig.location=((i%10)*230,(i//10)*270,0)
 rig.animation_data.action=rig.animation_data.action
 for p in []:p.rotation_mode='QUATERNION';p.rotation_quaternion=(1,0,0,0)
 rig.rotation_euler.z=math.radians(-12)
bpy.ops.mesh.primitive_plane_add(size=5000,location=(800,350,-1));floor=bpy.context.object
m=bpy.data.materials.new('Warm grey ground');m.diffuse_color=(.20,.23,.26,1);floor.data.materials.append(m)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.world=bpy.data.worlds.new('World');scene.world.color=(.35,.35,.35);scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.6,.6,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
bpy.ops.object.light_add(type='AREA',location=(500,-800,1400));bpy.context.object.data.energy=2500000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=2000
bpy.ops.object.camera_add(location=(1150,-2100,1600));cam=bpy.context.object;target=Vector((1035,675,80));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.clip_end=10000;cam.data.type='ORTHO';cam.data.ortho_scale=2500;scene.camera=cam
scene.render.resolution_x=2000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.render.filepath=str(out/'Ciudadanos_Blender.png');scene.frame_set(1);bpy.ops.render.render(write_still=True)






