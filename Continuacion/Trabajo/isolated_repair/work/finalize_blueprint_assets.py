import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
cleaned=0
for path in unreal.EditorAssetLibrary.list_assets('/Game',recursive=True,include_folder=False):
 data=unreal.EditorAssetLibrary.find_asset_data(path)
 if str(data.asset_class_path.asset_name) in ['Blueprint','WidgetBlueprint','AnimBlueprint']:
  b=unreal.load_asset(path);cleaned+=unreal.DeliveryEditorLibrary.clean_blueprint(b);unreal.BlueprintEditorLibrary.compile_blueprint(b);unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
city=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.BogotaCity))
assert city.get_class().get_name()=='BP_BogotaCity_C'
removed=unreal.DeliveryEditorLibrary.clean_city_duplicate_bikes()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(root/'work/final_asset_cleanup.json').write_text(json.dumps({'dead_parent_nodes_removed':cleaned,'duplicate_bike_actors_removed':removed,'canonical_city':city.get_class().get_path_name()},indent=2))
exec(compile((root/'work/validate_blueprint_migration.py').read_text(encoding='utf-8-sig'),str(root/'work/validate_blueprint_migration.py'),'exec'))
unreal.log('FINAL_ASSET_CLEANUP_PASS')
