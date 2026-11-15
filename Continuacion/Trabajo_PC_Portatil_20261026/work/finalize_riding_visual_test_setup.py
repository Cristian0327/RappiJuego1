import unreal
bp=unreal.load_asset('/Game/Traffic/Services/BP_VoxelRoadVehicle');unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp,'RoadSpeed',True);assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
for name in ['BP_CivilMotorcycle','BP_PoliceMotorcycle','BP_PoliceRoadPatrol']:
 b=unreal.load_asset('/Game/Traffic/Services/'+name);assert unreal.BlueprintEditorLibrary.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PatrolWindowVerifiedTest');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_actor_label().startswith('Patrulla_Sector_'):a.set_editor_property('RoadSpeed',0.0)
 if isinstance(a,unreal.CameraActor):a.get_editor_property('camera_component').set_editor_property('field_of_view',40)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True);assert unreal.EditorAssetLibrary.does_asset_exist('/Game/QA/HeroRidingVisualVerifiedTest');unreal.log('BOTH_RIDING_VISUAL_TESTS_READY')
