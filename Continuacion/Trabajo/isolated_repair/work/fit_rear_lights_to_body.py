import bpy,json,shutil,sys,math
from pathlib import Path
from mathutils import Vector
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');folder=r/'outputs/DeliveryArt/TrafficDetailed';sys.path.insert(0,str(r/'work'));from fleet20_catalog import FLEET20
specs={'SK_'+x['name']:x for x in FLEET20};original=r/'Recuperacion_Migracion_Blueprints/2026-10-16_posturas_controles/Modelos';recovery=r/'Recuperacion_Migracion_Blueprints/2026-10-18_rear_lamp_fit';recovery.mkdir(exist_ok=True);report=[]
names=['SK_PrivateSUV','SK_PrivatePickup','SK_PrivatePrado','SK_PrivateVitara','SK_PrivateSingleCab','SK_PrivateVan','SK_PrivateWagon']
for name in names:
 for source in [folder/(name+'.blend'),folder/(name+'.fbx'),r/'RappiJuego1/Content/Traffic/Detailed'/(name+'.uasset')]:
  target=recovery/source.name
  if source.exists() and not target.exists():shutil.copy2(source,target)
 bpy.ops.wm.open_mainfile(filepath=str(folder/(name+'.blend')));current=bpy.data.objects[name].find_armature();bind={b.name:tuple(v for row in b.matrix_local for v in row) for b in current.data.bones}
 bpy.ops.wm.open_mainfile(filepath=str(original/(name+'.blend')));mesh=bpy.data.objects[name];rig=mesh.find_armature();other={b.name:tuple(v for row in b.matrix_local for v in row) for b in rig.data.bones};assert bind.keys()==other.keys() and all(abs(x-y)<1e-6 for k in bind for x,y in zip(bind[k],other[k])),(name,'bind changed')
 colors=mesh.data.color_attributes['TrafficColor'];palette=json.loads((folder/'materials.json').read_text());uvs={}
 for key in ['TailLight','Amber','Lamp','Black']:
  col=palette[key];poly=min(mesh.data.polygons,key=lambda p:sum((colors.data[p.loop_start].color[i]-col[i])**2 for i in range(3)));uvs[key]=mesh.data.uv_layers[0].data[poly.loop_start].uv.copy()
 spec=specs[name];length=spec['length'];width=spec['width'];rear_top=spec['profile'][0][1] if spec['profile'] else 1.04 if spec['kind']=='suv' else 1.23 if spec['kind']=='pickup' else .87
 top=min(rear_top-.02,1.18);centre=round((top-.20)/.02)*.02;rear=round((-length/2-.01)/.02)*.02;side=round((width/2-.24)/.02)*.02;added=[]
 for sign in [-1,1]:
  for key,z,height,span,depth in [('Black',centre,.40,.26,.08),('TailLight',centre+.01,.24,.20,.10),('Amber',centre+.14,.08,.20,.12),('Lamp',centre-.14,.08,.20,.12)]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(rear,sign*side,z));o=bpy.context.object;o.name=name+'_RearFit_'+key;o.dimensions=(depth,span,height);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
   for v in o.data.vertices:v.co=Vector(tuple(round(float(c)/.02)*.02 for c in v.co))
   attr=o.data.color_attributes.new(name='TrafficColor',type='BYTE_COLOR',domain='CORNER')
   for item in attr.data:item.color=palette[key]
   for layer in mesh.data.uv_layers:
    uv=o.data.uv_layers.new(name=layer.name)
    for item in uv.data:item.uv=uvs[key] if layer==mesh.data.uv_layers[0] else (0,1)
   group=o.vertex_groups.new(name='root');group.add(list(range(len(o.data.vertices))),1,'REPLACE');added.append(o)
 # Verify every backing cluster overlaps the actual original body mesh in 3D.
 body_vertices=[v.co.copy() for v in mesh.data.vertices]
 for sign in [-1,1]:
  near=[v for v in body_vertices if abs(v.y-sign*side)<.15 and abs(v.z-centre)<.19 and abs(v.x+length/2)<.10]
  assert near,(name,'rear cluster lacks body backing',sign,rear,side,centre)
 bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True)
 for o in added:o.select_set(True)
 bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.context.scene['rear_lights_fitted_to_body']=True;bpy.ops.wm.save_as_mainfile(filepath=str(folder/(name+'.blend')));bpy.ops.export_scene.fbx(filepath=str(folder/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE');report.append({'model':name,'rear_plane_m':rear,'cluster_y_m':side,'cluster_z_m':centre,'has_original_body_backing':True,'bind_pose_unchanged':True,'voxel_grid_cm':2});print('REAR_LAMP_BODY_FIT '+name,flush=True)
(folder/'rear_lights_fitted.json').write_text(json.dumps(report,indent=2));print('REAR_LAMP_BODY_FIT_BLENDER_PASS models='+str(len(report)),flush=True)
