import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
dest='/Game/Delivery/People';report=[]
task=unreal.AssetImportTask();task.filename=str(root/'outputs/DeliveryArt/People/NPCPalette.png');task.destination_path=dest;task.automated=True;task.replace_existing=True;task.save=True;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
texture=unreal.load_asset(dest+'/NPCPalette');texture.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);unreal.EditorAssetLibrary.save_loaded_asset(texture)
mat=unreal.load_asset(dest+'/NPC_Atlas')
if not mat:mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('NPC_Atlas',dest,unreal.Material,unreal.MaterialFactoryNew())
unreal.MaterialEditingLibrary.delete_all_material_expressions(mat);node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-250,0);node.set_editor_property('texture',texture);unreal.MaterialEditingLibrary.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR);unreal.MaterialEditingLibrary.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
mult=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionMultiply,-50,160);mult.set_editor_property('const_b',.35);unreal.MaterialEditingLibrary.connect_material_expressions(node,'RGB',mult,'A');unreal.MaterialEditingLibrary.connect_material_property(mult,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);unreal.MaterialEditingLibrary.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
for f in (root/'outputs/DeliveryArt/People').glob('SK_*.fbx'):
 previous_skeleton=unreal.load_asset(dest+'/'+f.stem+'_Skeleton')
 if unreal.EditorAssetLibrary.does_asset_exist(dest+'/'+f.stem):unreal.EditorAssetLibrary.delete_asset(dest+'/'+f.stem)
 t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=dest;t.destination_name=f.stem;t.automated=True;t.replace_existing=True;t.save=True
 o=unreal.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=True;o.import_materials=False;o.import_textures=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;o.automated_import_should_detect_type=False;o.create_physics_asset=False;t.options=o
 if previous_skeleton:o.skeleton=previous_skeleton
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
 assert t.imported_object_paths,f
 for path in t.imported_object_paths:
  a=unreal.load_asset(path)
  if isinstance(a,unreal.SkeletalMesh):
   slots=a.get_editor_property('materials')
   for slot in slots:
    slot.set_editor_property('material_interface',unreal.load_asset(dest+'/NPC_Atlas'))
   a.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(a)
  if isinstance(a,unreal.AnimSequence):
   target=dest+'/A_'+f.stem[3:]+'_Work'
   if path.split('.')[0]!=target:
    if unreal.EditorAssetLibrary.does_asset_exist(target):unreal.EditorAssetLibrary.delete_asset(target)
    unreal.EditorAssetLibrary.rename_asset(path,target)
  report.append(path)
 mesh=unreal.load_asset(dest+'/'+f.stem);skeleton=mesh.get_editor_property('skeleton');assert skeleton
 unreal.EditorAssetLibrary.save_loaded_asset(skeleton)
 # Explicit animation import also handles existing skeletal-mesh reimports.
 at=unreal.AssetImportTask();at.filename=str(f);at.destination_path=dest;at.destination_name='A_'+f.stem[3:]+'_Work';at.automated=True;at.replace_existing=True;at.save=True
 ao=unreal.FbxImportUI();ao.import_mesh=False;ao.import_animations=True;ao.skeleton=skeleton;ao.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;ao.automated_import_should_detect_type=False;at.options=ao
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([at])
 clips=[unreal.load_asset(p) for p in at.imported_object_paths];assert any(isinstance(a,unreal.AnimSequence) for a in clips),f
 for clip in clips:
  if isinstance(clip,unreal.AnimSequence):
   target=dest+'/A_'+f.stem[3:]+'_Work'
   if clip.get_path_name().split('.')[0]!=target:unreal.EditorAssetLibrary.rename_asset(clip.get_path_name(),target)
   unreal.EditorAssetLibrary.save_loaded_asset(clip);report.append(target)
unreal.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False,recursive=True)
(root/'outputs/DeliveryArt/People/unreal_import.json').write_text(json.dumps(report,indent=2))
unreal.log('RIGGED_PEOPLE_IMPORTED')
