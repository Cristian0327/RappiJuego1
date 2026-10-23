import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
dest='/Game/Delivery/Animation/MixamoCandidate'
options=unreal.FbxImportUI()
options.import_mesh=True
options.import_as_skeletal=True
options.import_animations=True
options.import_materials=False
options.import_textures=False
options.create_physics_asset=False
options.automated_import_should_detect_type=False
options.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
options.skeletal_mesh_import_data.convert_scene=True
options.skeletal_mesh_import_data.convert_scene_unit=True
task=unreal.AssetImportTask()
task.filename=str(root/'outputs/DeliveryArt/Mixamo/Hero_Mixamo_Walk.fbx')
task.destination_path=dest
task.destination_name='SK_HeroMixamo'
task.automated=True
task.save=True
task.replace_existing=True
task.options=options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
assert task.imported_object_paths,'Mixamo candidate import failed'
for path in task.imported_object_paths:
 asset=unreal.load_asset(path)
 if isinstance(asset,unreal.SkeletalMesh):
  materials=asset.get_editor_property('materials')
  for slot in materials:slot.set_editor_property('material_interface',unreal.load_asset('/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB'))
  asset.set_editor_property('materials',materials)
 unreal.EditorAssetLibrary.save_loaded_asset(asset)
Path(unreal.Paths.project_saved_dir(),'mixamo_candidate.json').write_text(json.dumps(list(task.imported_object_paths),indent=2))
unreal.log('HERO_MIXAMO_CANDIDATE_IMPORTED')
