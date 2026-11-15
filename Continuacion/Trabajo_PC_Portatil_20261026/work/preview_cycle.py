import bpy,math
from mathutils import Vector
from pathlib import Path
O=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs/unreal_v2')
bpy.ops.wm.open_mainfile(filepath=str(O/'VoxelExplorer_GameRig.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.animation_data.action=bpy.data.actions['BikePedal'];bpy.context.scene.frame_set(9)
with bpy.data.libraries.load(str(O/'VoxelBicycle.blend'),link=False) as (a,b):b.objects=[n for n in a.objects if n=='SM_Bicycle']
for o in b.objects:bpy.context.scene.collection.objects.link(o);o.rotation_euler.z=-math.pi/2
rig.hide_set(True);s=bpy.context.scene
bpy.ops.mesh.primitive_plane_add(size=20000,location=(0,0,-1));m=bpy.data.materials.new('Floor');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.06,.065,.07,1);bpy.context.object.data.materials.append(m)
for p,e,size in [((-300,-300,500),5000000,400),((300,-100,300),3500000,400),((0,300,350),4500000,300)]:
 d=bpy.data.lights.new('Softbox','AREA');o=bpy.data.objects.new('Softbox',d);s.collection.objects.link(o);o.location=p;d.energy=e;d.shape='DISK';d.size=size;o.rotation_euler=(Vector((0,0,95))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Review');o=bpy.data.objects.new('Review',d);s.collection.objects.link(o);o.location=(350,-450,230);o.rotation_euler=(Vector((0,-5,100))-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=255;s.camera=o
s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=900;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(O/'cycle_review.png');bpy.ops.render.render(write_still=True)
