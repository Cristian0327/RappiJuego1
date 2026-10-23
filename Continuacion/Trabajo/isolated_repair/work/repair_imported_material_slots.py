import unreal,json,re
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1];repaired=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/Delivery/Stores',recursive=False):
 mesh=unreal.load_asset(path)
 if not isinstance(mesh,unreal.StaticMesh):continue
 changed=False
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  name=str(slot.get_editor_property('material_slot_name'));canonical=re.sub(r'[_\.]\d+$','',name)
  if canonical.startswith('ENV_'):
   mat=unreal.load_asset('/Game/Delivery/Stores/'+canonical)
   if mat and slot.get_editor_property('material_interface')!=mat:mesh.set_material(i,mat);changed=True;repaired.append(dict(asset=path,slot=i,material=canonical))
 if changed:unreal.EditorAssetLibrary.save_loaded_asset(mesh)
(root/'work/material_slot_repairs.json').write_text(json.dumps(repaired,indent=2))
exec((root/'work/audit_commercial_materials.py').read_text())
