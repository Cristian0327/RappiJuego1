import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_service_traffic_cache.py','place_two_wheeler_citizens.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),str(r/'work'/name),'exec'))
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert unreal.EditorAssetLibrary.duplicate_asset('/Game/Maps/Bogota','/Game/QA/CyclistCityVerified_20261016')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/CyclistCityVerified_20261016')
assert sum(o.get_actor_label().startswith('Motociclista_Propietario_') for o in a.get_all_level_actors())==4
a.spawn_actor_from_class(unreal.load_asset('/Game/QA/BP_TestTwoWheeler').generated_class(),unreal.Vector())
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('CITY_CYCLIST_TEST_READY_PASS')
