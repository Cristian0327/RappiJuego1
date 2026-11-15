import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PurePhoneRuntime')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not any(a.get_class().get_name()=='BP_MapNavigation_C' for a in actors.get_all_level_actors()):actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BogotaUrban/BP_MapNavigation.BP_MapNavigation_C'),unreal.Vector())
b=unreal.load_asset('/Game/QA/BP_TestPurePhoneRuntime');c=unreal.get_default_object(b.generated_class());c.set_editor_property('Age',-15.);c.set_editor_property('Stage',0.);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
for a in actors.get_all_level_actors():
 if a.get_class().get_name()=='BP_TestPurePhoneRuntime_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(b.generated_class(),unreal.Vector())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/PurePhoneRuntime')
(R/'AdversarialQA_20261026/final_visual_setup.json').write_text(json.dumps(dict(map=world.get_path_name(),navigation_overlay_actor_present=True,shader_warmup_before_ui_seconds=15,per_page_render_wait_seconds=4)))
unreal.log('FINAL_VISUAL_MAP_SAVED')
