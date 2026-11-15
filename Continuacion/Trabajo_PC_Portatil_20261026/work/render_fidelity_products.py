import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];out=r/'outputs/DeliveryArt/HighFidelity';bpy.ops.wm.read_factory_settings(use_empty=True)
names=['Milk','Rice','Apples','Burger','Headphones','Keyboard','PhoneBox','FirstAid','Medicine','Bouquet']
for i,name in enumerate(names):
 with bpy.data.libraries.load(str(out/('SM_'+name+'.blend')),link=False) as (a,b):b.objects=['SM_'+name]
 o=b.objects[0];bpy.context.collection.objects.link(o);o.location=((i%5-2)*.9,(i//5)*.95,0)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=-.5
sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.mesh.primitive_plane_add(size=200);plane=bpy.context.object;plane.location.z=-.012;mat=bpy.data.materials.new('Backdrop');mat.diffuse_color=(.8,.82,.86,1);plane.data.materials.append(mat)
bpy.ops.object.camera_add(location=(0,-5,4));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=4.9;cam.rotation_euler=(Vector((0,.5,.12))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
for pos,energy in [((-3,-3,5),650),((4,1,4),450)]:
 bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=energy;l.data.size=4;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(out/'Productos_Revision_Detallada.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'Productos_Revision.blend'));bpy.ops.render.render(write_still=True)
