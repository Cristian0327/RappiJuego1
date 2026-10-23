import unreal,json
from pathlib import Path
rows=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/Delivery/Stores',recursive=False):
 mesh=unreal.load_asset(path)
 if not isinstance(mesh,unreal.StaticMesh):continue
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  if not slot.get_editor_property('material_interface'):rows.append(dict(asset=path,slot=i,name=str(slot.get_editor_property('material_slot_name')),imported=str(slot.get_editor_property('imported_material_slot_name'))))
root=Path(unreal.Paths.project_dir()).parents[1];(root/'work/commercial_missing_materials.json').write_text(json.dumps(rows,indent=2));unreal.log('MATERIAL_AUDIT '+str(len(rows)))
