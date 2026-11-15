import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');folder=r/'outputs/DeliveryArt/TrafficDetailed';backup=r/'Recuperacion_Migracion_Blueprints/2026-10-16_posturas_controles/Modelos';backup.mkdir(exist_ok=True);report=[]
for name in ['SK_PrivateSUV','SK_PrivatePickup','SK_PrivatePrado','SK_PrivateVitara','SK_PrivateSingleCab','SK_PrivateVan','SK_PrivateWagon']:
 file=folder/(name+'.blend');dest=backup/file.name
 if not dest.exists():shutil.copy2(file,dest)
 bpy.ops.wm.open_mainfile(filepath=str(dest));mesh=bpy.data.objects[name];rig=mesh.find_armature();colors=mesh.data.color_attributes['TrafficColor'];palette=json.loads((folder/'materials.json').read_text());uvs={}
 for key in ['TailLight','Amber','Lamp','Black']:
  col=palette[key];poly=min(mesh.data.polygons,key=lambda p:sum((colors.data[p.loop_start].color[i]-col[i])**2 for i in range(3)));uvs[key]=mesh.data.uv_layers[0].data[poly.loop_start].uv.copy()
 low=min(v.co.x for v in mesh.data.vertices);width=max(abs(v.co.y) for v in mesh.data.vertices);added=[]
 for sign in [-1,1]:
  for key,z,height,span,depth in [('Black',.85,.44,.26,.08),('TailLight',.87,.26,.20,.10),('Amber',1.04,.08,.20,.11),('Lamp',.69,.08,.20,.11)]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(round((low-depth*.35)/.02)*.02,round(sign*width*.82/.02)*.02,z));o=bpy.context.object;o.name=name+'_Rear_'+key;o.dimensions=(depth,span,height);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
   for v in o.data.vertices:v.co=Vector(tuple(round(float(c)/.02)*.02 for c in v.co))
   attr=o.data.color_attributes.new(name='TrafficColor',type='BYTE_COLOR',domain='CORNER')
   for item in attr.data:item.color=palette[key]
   for layer in mesh.data.uv_layers:
    uv=o.data.uv_layers.new(name=layer.name)
    for item in uv.data:item.uv=uvs[key] if layer==mesh.data.uv_layers[0] else (0,1)
   group=o.vertex_groups.new(name='root');group.add(list(range(len(o.data.vertices))),1,'REPLACE');added.append(o)
 bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True)
 for o in added:o.select_set(True)
 bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.context.scene['rear_lights_repaired']=True;bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.export_scene.fbx(filepath=str(folder/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE');report.append({'model':name,'rear_clusters':2,'voxel_grid_cm':2,'paint_mask':0,'door_rig_preserved':True});print('REAR_LIGHTS_FIXED '+name,flush=True)
(folder/'rear_lights_repaired.json').write_text(json.dumps(report,indent=2));print('REAR_LIGHTS_BLENDER_PASS',flush=True)
