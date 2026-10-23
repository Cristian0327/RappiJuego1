import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1];obsolete={'SM_'+n for n in ['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']};report=[]
for folder in ['/Game/Delivery/Stores','/Game/Delivery/Art']:
 for path in unreal.EditorAssetLibrary.list_assets(folder,recursive=True):
  asset=unreal.load_asset(path)
  if asset and asset.get_name() in obsolete and isinstance(asset,unreal.StaticMesh):
   refs=unreal.EditorAssetLibrary.find_package_referencers_for_asset(path,True);deleted=False
   if not refs:deleted=unreal.EditorAssetLibrary.delete_asset(path)
   report.append({'asset':path,'referencers':list(refs),'deleted':deleted})
(root/'work/unused_npc_asset_cleanup.json').write_text(json.dumps(report,indent=2));unreal.log('UNUSED_STATIC_NPC_ASSETS_CHECKED '+str(len(report)))
