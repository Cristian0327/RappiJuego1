import bpy,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];folder=root/'outputs/DeliveryArt/People'
for file in folder.glob('A_CustomerStudent_Walk.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(file));sc=bpy.context.scene;sc.frame_set(25)
 sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=600;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.view_settings.exposure=-.35
 sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
 bpy.ops.object.camera_add(location=(2.4,-5,2.5));c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=2.15;c.rotation_euler=(Vector((0,0,.9))-c.location).to_track_quat('-Z','Y').to_euler();sc.camera=c
 for pos,power in [((1,-3,4),280),((-2,2,3),150)]:
  bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.size=3;l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
 sc.render.filepath=str(folder/(file.stem+'_Posed.png'));bpy.ops.render.render(write_still=True)
print('RIG_POSES_RENDERED')
