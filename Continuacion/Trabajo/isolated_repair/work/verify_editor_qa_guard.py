import unreal,json
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);before=len(a.get_all_level_actors())
r=json.loads(unreal.DeliveryEditorLibrary.validate_map_routes(1));assert 'error' in r,r
assert len(a.get_all_level_actors())==before
unreal.log('EDITOR_QA_GUARD_PASS')
