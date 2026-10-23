import bpy,math
from pathlib import Path
from mathutils import Vector
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');folder=r/'outputs/DeliveryArt/AnimationRebuild/Upright';bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;snaps=[]
for group,role in enumerate(['Hero','Crowd','Cashier']):
 for version,subfolder in enumerate([folder,folder/'Standing']):
  file=subfolder/('AN_'+role+'Idle_Rebuilt.blend')
  with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.objects=src.objects
  loaded=[o for o in dst.objects if o]
  for o in loaded:scene.collection.objects.link(o)
  rig=next(o for o in loaded if o.type=='ARMATURE');scene.frame_set(1);bpy.context.view_layer.update();meshes=[o for o in loaded if o.type=='MESH' and o.find_armature()==rig];height=max(v.co.z for o in meshes for v in o.data.vertices)-min(v.co.z for o in meshes for v in o.data.vertices);factor=1.8/height
  for mesh in meshes:
   data=bpy.data.meshes.new_from_object(mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()));o=bpy.data.objects.new(role+str(version),data);scene.collection.objects.link(o);o.scale=(factor,)*3;o.location=(group*3.2+version*1.4,0,0);snaps.append(o)
  for o in loaded:bpy.data.objects.remove(o,do_unlink=True)
  bpy.ops.object.text_add(location=(group*3.2+version*1.4-.3,-.5,-.17),rotation=(math.pi/2,0,0));bpy.context.object.data.body='ANTES' if version==0 else 'AHORA';bpy.context.object.data.size=.14
bpy.ops.mesh.primitive_plane_add(size=200,location=(3.8,0,-.02));floor=bpy.context.object;mat=bpy.data.materials.new('ReviewFloor');mat.diffuse_color=(.08,.12,.14,1);floor.data.materials.append(mat);aim=Vector((3.9,0,.8));bpy.ops.object.camera_add(location=aim+Vector((3,-9,2)));cam=bpy.context.object;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=10.5;scene.camera=cam
for pos,energy in [((2,-4,7),1800),((5,4,5),1400)]:bpy.ops.object.light_add(type='AREA',location=pos);bpy.context.object.data.energy=energy;bpy.context.object.data.size=6
scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.color=(.15,.15,.15);scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1800;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.render.filepath=str(folder/'Standing/Idle_Comparison.png');bpy.ops.render.render(write_still=True);print('STANDING_IDLE_VISUAL_REVIEW_RENDERED',flush=True)
