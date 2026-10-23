import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;out=[]
for folder in ['/Game/World/BlueprintWorld/Traffic','/Game/Traffic/Services']:
 for path in unreal.EditorAssetLibrary.list_assets(folder,True,False):
  data=unreal.EditorAssetLibrary.find_asset_data(path)
  if str(data.asset_class_path.asset_name)!='Blueprint':continue
  bp=data.get_asset();cls=bp.generated_class()
  if not cls:continue
  c=unreal.get_default_object(cls)
  try:body=c.get_editor_property('Body');mesh=body.get_editor_property('skeletal_mesh_asset')
  except:continue
  out.append({'blueprint':path,'mesh':mesh.get_path_name() if mesh else None,'materials':[m.get_path_name() if m else None for m in body.get_materials()],'mesh_materials':[m.material_interface.get_path_name() if m.material_interface else None for m in mesh.materials] if mesh else [],'slots':len(mesh.materials) if mesh else 0,'scale':str(body.get_relative_scale3d())})
(r/'work/new_map_vehicle_audit.json').write_text(json.dumps(out,indent=2));unreal.log('VEHICLE_AUDIT_READY '+str(len(out)))
