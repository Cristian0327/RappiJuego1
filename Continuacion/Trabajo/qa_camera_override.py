import unreal
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/SolidWorldRecovery')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
w.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,'/Script/Engine.GameModeBase'))
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
unreal.log('QA_CAMERA_OVERRIDE_PASS')
