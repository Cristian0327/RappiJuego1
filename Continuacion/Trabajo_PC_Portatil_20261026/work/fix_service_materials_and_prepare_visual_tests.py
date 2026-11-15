from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['import_service_voxel_models.py','diagnose_patrol_windows.py','build_hero_riding_visual_test.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
path='/Game/QA/PatrolWindowVerifiedTest';assert not unreal.EditorAssetLibrary.does_asset_exist(path);assert unreal.EditorAssetLibrary.duplicate_asset('/Game/QA/PatrolVisibleFinalVerifiedTest',path);unreal.EditorLoadingAndSavingUtils.load_map(path);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_actor_label().startswith('Patrulla_Sector_'):a.set_editor_property('RoadSpeed',0.0)
 if isinstance(a,unreal.CameraActor):a.get_editor_property('camera_component').set_editor_property('field_of_view',40)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True);unreal.log('WINDOW_MATERIAL_AND_VISUAL_TESTS_READY')
