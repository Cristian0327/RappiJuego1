import bpy,math,json,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/Shops';REV=ROOT/'outputs/DeliveryArt/References/CommercialReview';REV.mkdir(exist_ok=True)
for r in json.loads((ROOT/'work/commercial_catalog.json').read_text()):
 label=r['label'];D=r['depth'];W=r['width'];bpy.ops.wm.open_mainfile(filepath=str(OUT/('SM_'+label+'Front.blend')))
 with bpy.data.libraries.load(str(OUT/('SM_'+label+'Interior.blend')),link=False) as (a,b):b.objects=[n for n in a.objects if n=='SM_'+label+'Interior']
 for o in b.objects:
  if o:bpy.context.collection.objects.link(o);o.location.y=D/2
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.resolution_x=1100;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX'
 sc.world=bpy.data.worlds.new('Daylight');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.85,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 bpy.ops.object.light_add(type='AREA',location=(-15,-5,30));bpy.context.object.data.energy=18000;bpy.context.object.data.size=20
 bpy.ops.object.light_add(type='SUN',location=(0,0,20));bpy.context.object.rotation_euler=(.4,-.5,-.3);bpy.context.object.data.energy=2
 bpy.ops.object.camera_add(location=(-35,-36,25));cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=max(D+12,42);cam.rotation_euler=(Vector((0,D*.40,2.5))-cam.location).to_track_quat('-Z','Y').to_euler()
 sc.render.filepath=str(REV/(label+'_Exterior.png'));bpy.ops.render.render(write_still=True)
 # Cutaway derived from the same exported meshes; no alternative presentation geometry.
 for o in [x for x in sc.objects if x.type=='MESH']:
  bm=bmesh.new();bm.from_mesh(o.data);faces=[]
  for f in bm.faces:
   c=o.matrix_world@f.calc_center_median()
   if c.z>5.3 or c.x<-W/2+.5 or c.y<.3:faces.append(f)
  bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
 cam.location=(-26,-23,29);cam.rotation_euler=(Vector((0,D*.48,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(D+8,38)
 sc.render.filepath=str(REV/(label+'_Interior.png'));bpy.ops.render.render(write_still=True);print('REVIEW_DONE',label,flush=True)
