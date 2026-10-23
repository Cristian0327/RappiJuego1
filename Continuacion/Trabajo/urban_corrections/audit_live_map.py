import unreal,json
from pathlib import Path
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');rows=[]
for a in A.get_all_level_actors():
 cs=[]
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  mesh=c.get_editor_property('static_mesh');n=c.get_name();ct=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
  if ct:cs.append(dict(name=n,mesh=mesh.get_path_name() if mesh else None,count=ct))
 rows.append(dict(name=a.get_name(),label=a.get_actor_label(),cls=a.get_class().get_path_name(),loc=list(a.get_actor_location().to_tuple()),components=cs))
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_corrections/live_actor_inventory.json').write_text(json.dumps(rows,indent=2));unreal.log('MAP_INVENTORY_READY')
