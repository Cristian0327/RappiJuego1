import unreal,json
from pathlib import Path
mat=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficVoxelVertex');assert mat
r={}
for a in unreal.EditorAssetLibrary.list_assets('/Game/Traffic/Detailed',recursive=False):
 if a.split('/')[-1].startswith('SK_'):
  m=unreal.load_asset(a)
  if not isinstance(m,unreal.SkeletalMesh):continue
  m.modify();slots=m.get_editor_property('materials')
  for i in range(len(slots)):
   s=slots[i];s.material_interface=mat;slots[i]=s
  m.set_editor_property('materials',slots)
  assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
  r[m.get_name()]=len(slots)
Path(__file__).resolve().parent.joinpath('traffic_material_assignment.json').write_text(json.dumps(r))
