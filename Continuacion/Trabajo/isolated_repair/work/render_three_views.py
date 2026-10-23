import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Stores'
for n in ['SM_Cashier','SM_Chef','SM_TechClerk','SM_Pharmacist','SM_Florist']:
 bpy.ops.wm.open_mainfile(filepath=str(out/(n+'.blend')));scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32;scene.render.resolution_x=440;scene.render.resolution_y=560;scene.render.resolution_percentage=100
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.5;scene.camera=cam
 bpy.ops.object.light_add(type='AREA');light=bpy.context.object;light.data.energy=450;light.data.size=4
 for label,pos in [('Front',(0,-6,1)),('Side',(6,0,1)),('Back',(0,6,1))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();light.location=(pos[0]*.6,pos[1]*.6,4);light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/'Turnarounds'/(n+'_'+label+'.png'));bpy.ops.render.render(write_still=True)
print('THREE_VIEWS_RENDERED')
