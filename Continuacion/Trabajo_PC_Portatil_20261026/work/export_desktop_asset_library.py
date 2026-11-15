import bpy,json,csv,sys,traceback,re
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
desktop=root.parent
out=desktop/'BogotaVoxel_Modelos_SinRig_y_Locaciones'
out.mkdir(exist_ok=True)
catalog=json.loads((root/'outputs/DeliveryArt/Crowd/catalog.json').read_text(encoding='utf-8-sig'))
themes=json.loads((root/'outputs/BogotaVoxel/DeliveryData/StoreThemes.json').read_text(encoding='utf-8-sig'))
jobs=[{'source':root/'outputs/unreal_v2/VoxelExplorer_GameRig.blend','target':out/'Personajes/Principal/Personaje_Principal','type':'principal','label':'Repartidor principal'}]
for row in catalog:
 idx=int(row['name'].removeprefix('Citizen'))
 jobs.append({'source':root/f'outputs/DeliveryArt/Crowd/SK_Citizen{idx:02}.blend','target':out/f'Personajes/Ciudadanos/{idx:02}_{row["label"]}','type':'npc_ciudad','label':row['label']})
for p in sorted((root/'outputs/DeliveryArt/People').glob('SK_*.blend')):
 jobs.append({'source':p,'target':out/'Personajes/Personal_y_Clientes'/p.stem.removeprefix('SK_'),'type':'npc_local','label':p.stem.removeprefix('SK_')})
for row in themes:
 for part,key in [('Fachada','FrontMesh'),('Interior','InteriorMesh')]:
  stem=row[key].split('/')[-1].split('.')[0].removesuffix('_Voxel')
  source=root/'outputs/DeliveryArt/Shops'/(stem+'.blend')
  assert source.is_file(),source
  jobs.append({'source':source,'target':out/'Locaciones_Pedidos'/row['Name']/part,'type':'locacion_'+part.lower(),'label':row['Title'],'theme':row['Name']})

report=[]
for i,job in enumerate(jobs):
 p=job['source'];dest=job['target'];dest.parent.mkdir(parents=True,exist_ok=True)
 try:
  bpy.ops.wm.open_mainfile(filepath=str(p))
  for o in bpy.data.objects:
   if o.type=='ARMATURE':o.data.pose_position='REST';o.animation_data_clear()
  bpy.context.view_layer.update()
  meshes=[o for o in bpy.data.objects if o.type=='MESH']
  assert meshes,p
  for o in meshes:
   world=o.matrix_world.copy();o.animation_data_clear()
   for m in list(o.modifiers):
    if m.type=='ARMATURE':o.modifiers.remove(m)
   o.parent=None;o.matrix_world=world;o.vertex_groups.clear()
  for o in list(bpy.data.objects):
   if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
  for a in list(bpy.data.armatures):bpy.data.armatures.remove(a)
  for a in list(bpy.data.actions):bpy.data.actions.remove(a)
  bpy.context.view_layer.update()
  points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
  low=Vector(tuple(min(p[a] for p in points) for a in range(3)));high=Vector(tuple(max(p[a] for p in points) for a in range(3)))
  dims=high-low
  scale=.01 if job['type'] in ['principal','npc_ciudad'] and dims.z>10 else 1
  # Consistent meters, center on XY, feet on the ground. No posing or skeleton remains.
  origin=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
  for o in meshes:
   o.location=(o.location-origin)*scale;o.scale*=scale
  bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
  bpy.ops.object.select_all(action='DESELECT')
  for o in meshes:o.select_set(True)
  bpy.context.view_layer.objects.active=meshes[0]
  bpy.context.view_layer.update()
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  # Packed .blend and embedded GLB are portable even after moving the source project.
  bpy.ops.file.pack_all()
  bpy.context.scene.render.engine='CYCLES'
  bpy.ops.wm.save_as_mainfile(filepath=str(dest.with_suffix('.blend')),compress=True)
  bpy.ops.export_scene.gltf(filepath=str(dest.with_suffix('.glb')),export_format='GLB',use_selection=True,export_animations=False,export_skins=False,export_cameras=False,export_lights=False)
  bpy.ops.export_scene.fbx(filepath=str(dest.with_suffix('.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,path_mode='COPY',embed_textures=True,axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True)
  assert not any(o.type=='ARMATURE' for o in bpy.data.objects)
  assert not any(o.vertex_groups for o in meshes)
  assert not any(m.type=='ARMATURE' for o in meshes for m in o.modifiers)
  report.append({'label':job['label'],'category':job['type'],'theme':job.get('theme'),'source':str(p.relative_to(root)),'blend':str(dest.with_suffix('.blend').relative_to(out)),'glb':str(dest.with_suffix('.glb').relative_to(out)),'fbx':str(dest.with_suffix('.fbx').relative_to(out)),'meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'armatures':0,'armature_modifiers':0,'vertex_groups':0,'dimensions_m':[round(x*scale,4) for x in dims],'status':'PASS'})
  print(f'ASSET_EXPORT {i+1}/{len(jobs)} {job["label"]} PASS',flush=True)
 except Exception:
  traceback.print_exc();report.append({'label':job['label'],'category':job['type'],'status':'FAIL','source':str(p)})
 (out/'catalogo_modelos.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

with (out/'catalogo_modelos.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Modelo','Tipo','Blender','GLB','FBX','Huesos','Estado'])
 for row in report:w.writerow([row['label'],row['category'],row.get('blend'),row.get('glb'),row.get('fbx'),row.get('armatures'),row['status']])
(out/'catalogo_locaciones.json').write_text(json.dumps(themes,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'status':'PASS' if all(x['status']=='PASS' for x in report) else 'FAIL','principal':sum(x['category']=='principal' for x in report),'ciudadanos':sum(x['category']=='npc_ciudad' for x in report),'personal_y_clientes':sum(x['category']=='npc_local' for x in report),'locaciones':len(themes),'modelos_locaciones':sum(x['category'].startswith('locacion_') for x in report),'total':len(report),'failed':[x['label'] for x in report if x['status']=='FAIL']}
(out/'validacion_exportacion.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'LEEME.md').write_text('# Biblioteca de modelos de Bogotá Voxel\n\nIncluye al personaje principal, 60 ciudadanos, el personal y los clientes de los locales, y todas las fachadas e interiores que aparecen en el catálogo actual de pedidos.\n\nCada modelo está disponible como .blend, .glb y .fbx. Los personajes están en reposo, sin armaduras, huesos, pesos ni animaciones. Materiales y texturas se conservan; el archivo Blender y el GLB llevan sus recursos incluidos. Unidades en metros y base apoyada en Z=0.\n\nLos originales riggeados se conservan en BogotaVoxel_JuegoCompleto. Estos son duplicados editables sin rig.\n\nConsulta catalogo_modelos.csv para encontrar cada archivo y catalogo_locaciones.json para ver los nombres de los locales.\n',encoding='utf-8')
print('DESKTOP_ASSET_EXPORT_RESULT '+json.dumps(summary),flush=True)
if summary['status']!='PASS':raise RuntimeError('One or more asset exports failed')
