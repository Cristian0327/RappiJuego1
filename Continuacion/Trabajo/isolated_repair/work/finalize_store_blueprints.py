import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
for file in ['migrate_store_geometry_rules.py','migrate_recipient_interface.py','audit_superseded_interiors.py']:
 exec((root/'work'/file).read_text(encoding='utf-8-sig'))
report=[]
for row in json.loads((root/'work/commercial_catalog.json').read_text(encoding='utf-8')):
 for suffix in ['Front','Interior']:
  old='/Game/Delivery/Stores/SM_'+row['label']+suffix;new=old+'_Voxel'
  mesh=unreal.load_asset(new)
  assert isinstance(mesh,unreal.StaticMesh) and len(mesh.get_editor_property('static_materials'))<50,new
  if not unreal.EditorAssetLibrary.does_asset_exist(old):continue
  refs=list(unreal.EditorAssetLibrary.find_package_referencers_for_asset(old,load_assets_to_confirm=True))
  deleted=False
  if not refs:deleted=unreal.EditorAssetLibrary.delete_asset(old)
  report.append({'old':old,'replacement':new,'referencers':refs,'deleted':deleted})
(root/'work/superseded_store_assets_cleanup.json').write_text(json.dumps(report,indent=2))
