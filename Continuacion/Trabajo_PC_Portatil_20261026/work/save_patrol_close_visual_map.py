import unreal
path='/Game/QA/PatrolWindowFinalChecked';world=unreal.EditorLoadingAndSavingUtils.load_map(path);assert world and world.get_path_name().startswith(path+'.');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_actor_label().startswith('Patrulla_Sector_'):a.set_editor_property('RoadSpeed',0.0)
 if isinstance(a,unreal.CameraActor):a.get_editor_property('camera_component').set_editor_property('field_of_view',40)
assert unreal.EditorLoadingAndSavingUtils.save_map(world,path);unreal.log('PATROL_CLOSE_VISUAL_MAP_SAVED')
