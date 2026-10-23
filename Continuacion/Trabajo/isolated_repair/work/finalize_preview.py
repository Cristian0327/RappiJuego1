import bpy,math
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs/unreal_v2')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'VoxelExplorer_Unreal.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['Armature'];ob=bpy.data.objects['SK_VoxelExplorer']
rig.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1);bpy.context.view_layer.update()
# Keep the reference stance, but detach the current action so manual posing is immediate.
rig.animation_data.action=None
rig.pose.bones['pelvis'].select=True
ob.select_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'VoxelExplorer_Unreal.blend'),compress=True)
bpy.ops.object.mode_set(mode='OBJECT');rig.hide_set(True)
bpy.ops.mesh.primitive_plane_add(size=20000,location=(0,0,-.8));floor=bpy.context.object
fm=bpy.data.materials.new('Preview floor');fm.use_nodes=True
fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.025,.024,.024,1)
fm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
floor.data.materials.append(fm)
for name,loc,power,size,color in [('Key',(-300,-400,500),4500000,400,(1,.88,.77)),('Fill',(300,-200,250),2700000,300,(.78,.92,1)),('Rim',(100,300,400),5500000,300,(1,.93,.86))]:
 d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;d.color=color;o.rotation_euler=(Vector((0,0,95))-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Preview');cam=bpy.data.objects.new('Preview',cd);scene.collection.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=215;cd.clip_end=10000;scene.camera=cam
scene.render.resolution_x=720;scene.render.resolution_y=1080;scene.cycles.samples=32
for name,loc,act,frame in [('hero',(300,-600,235),'Idle',1),('side',(700,0,93),'Idle',1),('back',(0,700,93),'Idle',1),('articulations',(300,-600,235),'Rig_Test',31)]:
 rig.animation_data.action=bpy.data.actions[act];scene.frame_set(frame);cam.location=loc;cam.rotation_euler=(Vector((0,0,95))-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
