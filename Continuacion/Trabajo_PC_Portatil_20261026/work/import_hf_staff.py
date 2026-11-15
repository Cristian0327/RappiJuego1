import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
tasks=[]
for source in (root/'outputs/DeliveryArt/HighFidelity').glob('*.fbx'):
 t=unreal.AssetImportTask();t.filename=str(source);t.destination_path='/Game/Delivery/Stores';t.destination_name=source.stem;t.automated=True;t.replace_existing=True;t.save=True
 o=unreal.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=False;o.import_materials=True;o.import_textures=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;o.automated_import_should_detect_type=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;t.options=o;tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for t in tasks:
 if not t.imported_object_paths:raise RuntimeError(t.filename)
 for path in t.imported_object_paths:
  mesh=unreal.load_asset(path)
  if isinstance(mesh,unreal.StaticMesh):
   mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
   unreal.EditorAssetLibrary.save_loaded_asset(mesh)
unreal.log('STORES_IMPORTED '+str(len(tasks)))

exec((root/"work/fix_store_materials.py").read_text(encoding="utf-8-sig"))

