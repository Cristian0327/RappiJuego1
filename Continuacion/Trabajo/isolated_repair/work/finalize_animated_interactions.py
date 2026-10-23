import unreal,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;root=Path(unreal.Paths.project_dir());a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota');actors=a.get_all_level_actors();labels=[o.get_actor_label() for o in actors];assert sum(x.startswith('Ciclista_Propietario_') for x in labels)==8;assert sum(x.startswith('Motociclista_Propietario_') for x in labels)==4;assert 'City_AnimatedVehicleInteractions' in labels;assert not any(x.startswith(('BP_Test','BP_CyclistVisualObserver')) for x in labels)
reg=unreal.AssetRegistryHelpers.get_asset_registry();backup=r/'Recuperacion_Migracion_Blueprints/2026-10-16_interacciones_animadas';qa=root/'Content/QA'
if qa.exists():
 assets=unreal.EditorAssetLibrary.list_assets('/Game/QA',recursive=True,include_folder=False)
 for asset in assets:
  package=asset.split('.')[0];refs=[str(x) for x in reg.get_referencers(package,unreal.AssetRegistryDependencyOptions())];assert not any(not x.startswith('/Game/QA/') for x in refs),(package,refs)
 shutil.copytree(qa,backup/'QA_final',dirs_exist_ok=True);assert unreal.EditorAssetLibrary.delete_directory('/Game/QA')
for color in ['Blue','Red','Yellow']:
 asset='/Game/Traffic/Services/SK_BicycleCivil'+color
 if unreal.EditorAssetLibrary.does_asset_exist(asset):
  refs=[str(x) for x in reg.get_referencers(asset,unreal.AssetRegistryDependencyOptions())]
  if not refs:
   src=root/'Content/Traffic/Services'/('SK_BicycleCivil'+color+'.uasset');dst=backup/'Importaciones_sustituidas'/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);unreal.EditorAssetLibrary.delete_asset(asset)
report={'city_cyclists':8,'city_motorcycle_owners':4,'input_manager':True,'qa_actors_in_main':False,'cpp_migration_complete':False};(root/'Docs/validacion_mapa_interacciones_animadas.json').write_text(json.dumps(report,indent=2));unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True);unreal.log('ANIMATED_INTERACTIONS_MAIN_MAP_CLEAN_PASS')

docs=root/"Docs"
reports=[]
for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game',recursive=True):
 if str(a.asset_class_path.asset_name) not in ['Blueprint','AnimBlueprint','WidgetBlueprint']:continue
 bp=a.get_asset();assert unreal.BlueprintEditorLibrary.compile_blueprint(bp),str(a.package_name);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['compiled'],audit['asset'];reports.append(audit)
native=[{'asset':a['asset'],'native_parent':a['parent']} for a in reports if a['parent'].startswith('/Script/BogotaVoxel.')];assert len(native)==7,native
(docs/'auditoria_bases_blueprints.json').write_text(json.dumps({'status':'PASS','compiled_blueprints':len(reports),'remaining_native_parents':native,'assets':reports},indent=2),encoding='utf-8');p=docs/'estado_migracion_total_blueprints.json';state=json.loads(p.read_text());state['remaining_inherited_blueprints']=native;state['runtime_blueprints_compiled']=len(reports);p.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');unreal.log('SERVICE_CLEANUP_AND_ALL_BLUEPRINT_AUDIT_PASS '+str(len(reports)))

unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
