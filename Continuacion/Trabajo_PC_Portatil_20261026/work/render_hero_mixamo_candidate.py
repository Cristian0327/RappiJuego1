import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
folder=root/'outputs/DeliveryArt/Mixamo'
bpy.ops.wm.open_mainfile(filepath=str(folder/'Hero_Mixamo_Walk.blend'))
sc=bpy.context.scene;sc.frame_set(12);bpy.context.view_layer.update()
points=[o.matrix_world@Vector(p) for o in sc.objects if o.type=='MESH' for p in o.bound_box]
low=Vector(tuple(min(p[i] for p in points) for i in range(3)));high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
center=(low+high)/2;height=high.z-low.z
sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=720;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('ReviewWorld');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.18,.22,1)
bpy.ops.object.camera_add(location=center+Vector((height*.8,-height*2,height*.3)))
camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=height*1.25;sc.camera=camera
for offset in [(1,-2,2),(-2,-1,1)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*height)
 lamp=bpy.context.object;lamp.data.energy=700*height*height;lamp.data.shape='DISK';lamp.data.size=height*2;lamp.rotation_euler=(center-lamp.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(folder/'Hero_Mixamo_Review.png');bpy.ops.render.render(write_still=True)
