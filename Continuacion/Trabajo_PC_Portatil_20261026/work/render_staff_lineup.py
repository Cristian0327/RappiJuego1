import bpy
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Stores'
bpy.ops.wm.read_factory_settings(use_empty=True)
for i,n in enumerate(['SM_Cashier','SM_Chef','SM_TechClerk','SM_Pharmacist','SM_Florist']):
 with bpy.data.libraries.load(str(out/(n+'.blend'))) as (src,dst):dst.objects=[n]
 for ob in dst.objects:bpy.context.collection.objects.link(ob);ob.location.x=i*1.4
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1200;scene.render.resolution_y=460;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Dark blue');scene.world.color=(.04,.06,.08);scene.view_settings.view_transform='Standard'
bpy.ops.object.camera_add(location=(4,-12,5));cam=bpy.context.object;cam.rotation_euler=(Vector((2.8,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.4;scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(1,-4,6));bpy.context.object.data.energy=1100;bpy.context.object.data.size=7
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Encargados.blend'));scene.render.filepath=str(out/'Encargados.png');bpy.ops.render.render(write_still=True)
