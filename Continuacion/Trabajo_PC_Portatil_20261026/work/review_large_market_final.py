import bpy,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/Shops';REVIEW=ROOT/'work/CommercialReview';REVIEW.mkdir(exist_ok=True)
for label,W,D in [('FreshMarket',20,18)]:
 bpy.ops.wm.open_mainfile(filepath=str(OUT/('SM_'+label+'Front.blend')))
 with bpy.data.libraries.load(str(OUT/('SM_'+label+'Interior.blend')),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith('SM_'+label+'Interior')]
 for obj in b.objects:
  if obj:bpy.context.collection.objects.link(obj);obj.location.y+=D/2
 for mat in bpy.data.materials:
  if mat.name.startswith('ENV_glass'):
   node=mat.node_tree.nodes['Principled BSDF'];node.inputs['Transmission Weight'].default_value=1;node.inputs['IOR'].default_value=1.05;node.inputs['Roughness'].default_value=.03;node.inputs['Alpha'].default_value=.12
 sc=bpy.context.scene;sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=-.8;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.world=bpy.data.worlds.new('Review');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.85,.89,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 bpy.ops.object.camera_add(location=(-23,-27,19));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=31;cam.rotation_euler=(Vector((0,D*.45,2.3))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
 for pos,energy,size in [((-10,-10,18),3500,14),((12,3,16),2500,12),((0,15,18),3000,12)]:
  bpy.ops.object.light_add(type='AREA',location=pos);obj=bpy.context.object;obj.data.energy=energy;obj.data.size=size;obj.rotation_euler=(Vector((0,D/2,1))-obj.location).to_track_quat('-Z','Y').to_euler()
 sc.render.filepath=str(REVIEW/(label+'_Exterior.png'));bpy.ops.render.render(write_still=True)
 for obj in [o for o in bpy.context.scene.objects if o.type=='MESH']:
  bm=bmesh.new();bm.from_mesh(obj.data);faces=[]
  for f in bm.faces:
   c=obj.matrix_world@f.calc_center_median()
   if c.z>4.65 or (c.x<-W/2+.3 and c.y>.3):faces.append(f)
  bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(obj.data);bm.free()
 sc.render.filepath=str(REVIEW/(label+'_Interior.png'));bpy.ops.render.render(write_still=True);print('LARGE_REVIEW_DONE',label,flush=True)
