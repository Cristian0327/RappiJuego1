import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
for name in ['CustomerStudent','CustomerOffice','CustomerNeighbor']:
 t=unreal.AssetImportTask();t.filename=str(root/'outputs/DeliveryArt/People'/('A_'+name+'_Walk.fbx'));t.destination_path='/Game/Delivery/People';t.destination_name='A_'+name+'_Walk';t.automated=True;t.replace_existing=True;t.save=True
 o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=unreal.load_asset('/Game/Delivery/People/SK_'+name+'_Skeleton');o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert t.imported_object_paths
 for p in t.imported_object_paths:
  a=unreal.load_asset(p);target='/Game/Delivery/People/A_'+name+'_Walk'
  if p.split('.')[0]!=target:unreal.EditorAssetLibrary.rename_asset(p,target)
  unreal.EditorAssetLibrary.save_loaded_asset(a)
unreal.log('CUSTOMER_WALKS_IMPORTED')
