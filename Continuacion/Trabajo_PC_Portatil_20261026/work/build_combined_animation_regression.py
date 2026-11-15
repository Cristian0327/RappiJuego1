import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;exec(compile((r/'work/build_player_interaction_runtime_test.py').read_text(encoding='utf-8-sig'),'HeroInteractionRegression','exec'),{});actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.load_asset('/Game/Delivery/Core/BP_DeliveryGameMode').generated_class())
for i,role in enumerate(['Cashier','Chef','TechClerk','Pharmacist','Florist','CustomerStudent','CustomerOffice','CustomerNeighbor']):
 cls=unreal.load_class(None,'/Game/QA/BP_TestMotion_'+role+'.BP_TestMotion_'+role+'_C');assert cls,role;actors.spawn_actor_from_class(cls,unreal.Vector(-6000,14000+i*160,60))
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/StandingIdleAndInteractionRegression');unreal.log('COMBINED_ANIMATION_REGRESSION_MAP_BUILT_PASS checks_expected=34')
