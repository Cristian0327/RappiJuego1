import unreal,sys,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;root=Path(unreal.Paths.project_dir());docs=root/'Docs'
# Retain reproducible test assets outside the runnable project.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
q=root/'Content/QA';backup=r/'Recuperacion_Migracion_Blueprints/2026-10-16_puertas_verificadas'
if q.exists():
 for asset in unreal.EditorAssetLibrary.list_assets('/Game/QA',recursive=True,include_folder=False):
  refs=unreal.EditorAssetLibrary.find_package_referencers_for_asset(asset,load_assets_to_confirm=True);assert all(str(x).startswith('/Game/QA') for x in refs),(asset,refs)
 if not backup.exists():shutil.copytree(q,backup)
 assert unreal.EditorAssetLibrary.delete_directory('/Game/QA')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
unused=[]
for asset in ['/Game/VoxelExplorer/AN_Rig_Test','/Game/Traffic/Services/BP_PolicePatrol']:
 if not unreal.EditorAssetLibrary.does_asset_exist(asset):continue
 refs=unreal.EditorAssetLibrary.find_package_referencers_for_asset(asset,load_assets_to_confirm=True)
 if refs:continue
 file=root/'Content'/(asset.removeprefix('/Game/')+'.uasset');dest=r/'Recuperacion_Migracion_Blueprints/2026-10-16_recursos_sustituidos';dest.mkdir(parents=True,exist_ok=True)
 if file.exists():shutil.copy2(file,dest/file.name)
 assert unreal.EditorAssetLibrary.delete_asset(asset);unused.append(asset)
controller=unreal.load_asset('/Game/Delivery/Developer/BP_DeveloperVehicleDoors');assert controller
cdo=unreal.get_default_object(controller.generated_class());assert 'POST_UPDATE_WORK' in str(cdo.get_editor_property('primary_actor_tick').get_editor_property('tick_group'))
(docs/'recursos_sustituidos_retirados.json').write_text(json.dumps(unused,indent=2))
reports=[]
for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game',recursive=True):
 if str(a.asset_class_path.asset_name) not in ['Blueprint','AnimBlueprint','WidgetBlueprint']:continue
 bp=a.get_asset();assert unreal.BlueprintEditorLibrary.compile_blueprint(bp),str(a.package_name);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['compiled'],audit['asset'];reports.append(audit)
native=[{'asset':a['asset'],'native_parent':a['parent']} for a in reports if a['parent'].startswith('/Script/BogotaVoxel.')];assert len(native)==7,native
(docs/'auditoria_bases_blueprints.json').write_text(json.dumps({'status':'PASS','compiled_blueprints':len(reports),'remaining_native_parents':native,'assets':reports},indent=2),encoding='utf-8');p=docs/'estado_migracion_total_blueprints.json';state=json.loads(p.read_text());state['remaining_inherited_blueprints']=native;state['runtime_blueprints_compiled']=len(reports);p.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');unreal.log('SERVICE_CLEANUP_AND_ALL_BLUEPRINT_AUDIT_PASS '+str(len(reports)))

exec(compile((r/"work/verify_playable_map_clean.py").read_text(),str(r/"work/verify_playable_map_clean.py"),"exec"))
