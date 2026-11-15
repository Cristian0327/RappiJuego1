import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrowdManager');c=unreal.get_default_object(bp.generated_class());out={}
for name in ['SpawnPositions','Headings','Models','StartIndices','Route0','Route1','Route2','Route3']:
 data=c.get_editor_property(name);out[name]={'count':len(data),'first':[str(v) for v in data[:3]]}
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());spawn=a.call_method('SpawnModel',(0,unreal.Vector(-34848,-20918,114),0.));out['actual_spawn']=str(spawn.get_actor_location());actors.destroy_actor(spawn);actors.destroy_actor(a);(r/'work/crowd_spawn_coordinate_inventory.json').write_text(json.dumps(out,indent=2));unreal.log('CROWD_SPAWN_COORDINATES_PASS')
