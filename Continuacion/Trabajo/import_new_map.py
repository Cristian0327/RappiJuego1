import unreal,json,sys,shutil,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');D=r/'outputs/MapRebuild';D.mkdir(parents=True,exist_ok=True)
for name in ['manifest.json','Mapa_Completo_Andenes.blend']:shutil.copy2(W/name,D/name)
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Maps/MapaCompleto/Geometry';E.make_directory(folder)
mat=unreal.load_asset('/Game/Maps/MapaCompleto/M_MapaVoxel')
if not mat:
 mat=T.create_asset('M_MapaVoxel','/Game/Maps/MapaCompleto',unreal.Material,unreal.MaterialFactoryNew());v=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionVertexColor);unreal.MaterialEditingLibrary.connect_material_property(v,'RGB',unreal.MaterialProperty.MP_BASE_COLOR);rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant);rough.set_editor_property('r',.9);unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
mat.set_editor_property('two_sided',True);mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_OPAQUE);unreal.MaterialEditingLibrary.recompile_material(mat);E.save_loaded_asset(mat)
manifest=json.loads((W/'manifest.json').read_text());report=[]
for spec in manifest['meshes']:
 name=spec['name'];path=folder+'/'+name;mesh=unreal.load_asset(path)
 if not mesh:
  opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.import_animations=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;opt.static_mesh_import_data.force_front_x_axis=False
  task=unreal.AssetImportTask();task.filename=str(W/'export'/(name+'.fbx'));task.destination_path=folder;task.destination_name=name;task.options=opt;task.automated=True;task.save=True;T.import_asset_tasks([task]);assert task.imported_object_paths,name;mesh=unreal.load_asset(path)
 mesh.set_material(0,mat);body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);E.save_loaded_asset(mesh,only_if_is_dirty=False);b=mesh.get_bounding_box();report.append({'name':name,'min':list(b.min.to_tuple()),'max':list(b.max.to_tuple())});unreal.log('NEW_MAP_IMPORTED '+name)
(D/'import_report.json').write_text(json.dumps(report,indent=2))
# Inventory current functional actors so only the old scenery is removed during replacement.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in actors.get_all_level_actors():
 p=a.get_actor_location();rows.append({'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_path_name(),'position':[p.x,p.y,p.z]})
(D/'old_actor_inventory.json').write_text(json.dumps(rows,indent=2));unreal.log('NEW_MAP_ASSETS_READY '+str(len(report)))
