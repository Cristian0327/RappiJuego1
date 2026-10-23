import bpy,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/TrafficDetailed'
bpy.ops.wm.read_factory_settings(use_empty=True)
expanded='--fleet20' in sys.argv
if expanded:
 catalog=json.loads((OUT/'fleet20_catalog.json').read_text(encoding='utf-8'))
 placements=[(s['name'],((i%5-2)*6.4,(i//5)*4.6-7,0)) for i,s in enumerate(catalog)]+[('TaxiCompact',(-4,12,0)),('TaxiSedan',(4,12,0)),('TransMilenio',(0,18,0))]
else:placements=[('TaxiCompact',(5.5,-5,0)),('TaxiSedan',(-.3,-5,0)),('Private',(-6.5,-5,0)),('PrivateHatch',(5.5,0,0)),('PrivateSUV',(-.3,0,0)),('PrivatePickup',(-6.5,0,0)),('TransMilenio',(0,6.0,0))]
for name,at in placements:
 with bpy.data.libraries.load(str(OUT/('SK_'+name+'.blend')),link=False) as (src,dst):dst.objects=[n for n in src.objects if n in ['SK_'+name,'Rig_'+name]]
 for obj in dst.objects:
  if obj:bpy.context.collection.objects.link(obj)
 rig=bpy.data.objects['Rig_'+name];rig.location=at
sc=bpy.context.scene;sc.frame_set(1);sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1800;sc.render.resolution_y=1300;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.view_settings.exposure=-.7
if expanded:sc.render.resolution_x=2400;sc.render.resolution_y=2200
sc.world=bpy.data.worlds.new('FleetStudio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.59,.64,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.38
floor=bpy.data.materials.new('Floor');floor.use_nodes=True;floor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.20,.21,.22,1);floor.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03));bpy.context.object.data.materials.append(floor)
aim=Vector((0,1.0,.8));bpy.ops.object.camera_add(location=(22,-31,22));cam=bpy.context.object;cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=25.5;sc.camera=cam
if expanded:
 aim=Vector((0,5,.8));cam.location=(36,-50,40);cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=45
bpy.ops.object.light_add(type='SUN',location=(6,-5,15));sun=bpy.context.object;sun.rotation_euler=(Vector((0,0,0))-sun.location).to_track_quat('-Z','Y').to_euler();sun.data.energy=1.3;sun.data.angle=.18
for pos,energy,size in [((5,-8,14),1800,12),((-8,-3,12),1400,10),((0,10,12),1700,10)]:
 bpy.ops.object.light_add(type='AREA',location=pos);light=bpy.context.object;light.data.energy=energy;light.data.size=size;light.rotation_euler=(aim-light.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(OUT/('Flota20_Colombia_SinTexto.png' if expanded else 'Flota_Colombia_Detallada_SinTexto.png'));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('Flota20_Colombia_Revision.blend' if expanded else 'Flota_Colombia_Revision.blend')));bpy.ops.render.render(write_still=True)
