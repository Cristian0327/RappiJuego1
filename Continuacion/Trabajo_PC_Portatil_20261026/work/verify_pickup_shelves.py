import unreal,json,re
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
rows=[]
for item in json.loads((root/'work/pickup_shelves_manifest.json').read_text()):
 mesh=unreal.load_asset('/Game/Delivery/Stores/'+item['asset'])
 assert mesh,item['asset']
 for slot in mesh.get_editor_property('static_materials'):
  name=re.sub(r'_\d+$','',str(slot.material_slot_name))
  expected=unreal.load_asset('/Game/Delivery/Stores/'+name)
  assert expected and slot.material_interface==expected,(item['asset'],name,str(slot.material_interface))
 rows.append({'asset':item['asset'],'materials_verified':len(mesh.get_editor_property('static_materials'))})
(root/'work/pickup_shelves_verified.json').write_text(json.dumps(rows,indent=2))
