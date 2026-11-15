from pathlib import Path
source=(Path(__file__).parent/'import_commercial_district.py').read_text(encoding='utf-8')
exec(source.split('unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)')[0])
tasks=[t for t in tasks if 'Interior' in t.filename]
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for t in tasks:
 assert t.imported_object_paths,t.filename
 for path in t.imported_object_paths:
  mesh=unreal.load_asset(path)
  if isinstance(mesh,unreal.StaticMesh):
   mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
exec((root/'work/fix_store_materials.py').read_text(encoding='utf-8-sig'))
unreal.log('DENSE_INTERIORS_IMPORTED')
