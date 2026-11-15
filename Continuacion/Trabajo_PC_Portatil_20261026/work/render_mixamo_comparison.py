import bpy,math,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/RigComparison'
for label,file in [('Mixamo',out/'Mixamo_AutoRig.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file));sc=bpy.context.scene
 for o in list(sc.objects):
  if o.type in {'LIGHT','CAMERA'}:bpy.data.objects.remove(o,do_unlink=True)
 sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=420;sc.render.resolution_y=600;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.view_settings.exposure=-.4
 sc.world=bpy.data.worlds.new('Review');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.16,.18,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 bpy.ops.object.camera_add(location=(2.4,-5,2.4));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=2.1;cam.rotation_euler=(Vector((0,0,.86))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
 for pos,power in [((1,-3,4),260),((-2,2,3),180)]:
  bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.size=3;l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.location.z=-.006;mat=bpy.data.materials.new('Ground');mat.diffuse_color=(.16,.18,.20,1);floor.data.materials.append(mat)
 for i in range(24):
  sc.frame_set(1+round(i*41/24));sc.render.filepath=str(out/f'{label}_{i:02}.png');bpy.ops.render.render(write_still=True)
print('COMPARISON_FRAMES_READY')
