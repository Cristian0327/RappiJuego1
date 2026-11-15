import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
world=unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota');assert world
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label().startswith('Policia_Sector_'):
  m=a.get_editor_property('mesh');rows.append({'label':a.get_actor_label(),'mesh':m.get_skinned_asset().get_path_name(),'material':m.get_material(0).get_path_name()})
(r/'work/police_instance_materials.json').write_text(json.dumps(rows,indent=2))
unreal.log('POLICE_INSTANCE_MATERIAL_AUDIT_PASS')
