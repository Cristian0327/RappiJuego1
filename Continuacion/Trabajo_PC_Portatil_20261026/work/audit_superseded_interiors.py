import unreal,json
from pathlib import Path
project=Path(unreal.Paths.project_dir());root=project.parents[1]
rows=json.loads((root/'work/commercial_catalog.json').read_text(encoding='utf-8'))
report=[]
for row in rows:
 old='/Game/Delivery/Stores/SM_'+row['label']+'Interior'
 new=old+'_Voxel';mesh=unreal.load_asset(new)
 assert isinstance(mesh,unreal.StaticMesh),new
 slots=list(mesh.get_editor_property('static_materials'))
 assert len(slots)<50,(new,len(slots))
 assert all(s.material_interface for s in slots),new
 refs=unreal.EditorAssetLibrary.find_package_referencers_for_asset(old,load_assets_to_confirm=True) if unreal.EditorAssetLibrary.does_asset_exist(old) else []
 report.append({'old':old,'replacement':new,'materials':len(slots),'referencers':list(refs)})
(root/'work/superseded_interiors_audit.json').write_text(json.dumps(report,indent=2))
