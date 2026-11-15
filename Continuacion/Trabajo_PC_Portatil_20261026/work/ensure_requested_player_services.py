import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
items=[{'label':a.get_actor_label(),'class':a.get_class().get_path_name()} for a in actors.get_all_level_actors() if any(x in (a.get_class().get_path_name()+a.get_actor_label()) for x in ['Coordinator','RoadInteraction','Developer','CameraObstacle'])]
(r/'work/requested_map_services.json').write_text(json.dumps(items,indent=2));unreal.log('MAP_SERVICES '+json.dumps(items))
for name in ['BP_BlueprintRiderAnimationCoordinator','BP_RoadInteraction','BP_CameraObstacleSetup']:
 cls=unreal.load_class(None,'/Game/Delivery/BlueprintGameplay/Player/'+name+'.'+name+'_C')
 if not any(a.get_class()==cls for a in actors.get_all_level_actors()):actors.spawn_actor_from_class(cls,unreal.Vector()).set_actor_label(name)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/Maps/Bogota_Blueprint_Integration');unreal.log('ENSURED_PLAYER_SERVICES_PASS')
exec(compile((r/'work/build_requested_fixes_qa.py').read_text(encoding='utf-8-sig'),'RebuildRequestedQA','exec'),{})
