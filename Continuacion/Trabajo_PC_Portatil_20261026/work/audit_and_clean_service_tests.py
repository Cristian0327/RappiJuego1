import unreal,sys,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;root=Path(unreal.Paths.project_dir());docs=root/'Docs'
# Retain reproducible test assets outside the runnable project.
q=root/'Content/QA';backup=r/'Recuperacion_Migracion_Blueprints/2026-10-16_pruebas'
if q.exists():
 for asset in unreal.EditorAssetLibrary.list_assets('/Game/QA',recursive=True,include_folder=False):
  refs=unreal.EditorAssetLibrary.find_package_referencers_for_asset(asset,load_assets_to_confirm=True);assert all(str(x).startswith('/Game/QA') for x in refs),(asset,refs)
 if not backup.exists():shutil.copytree(q,backup)
 assert unreal.EditorAssetLibrary.delete_directory('/Game/QA')
reports=[]
for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game',recursive=True):
 if str(a.asset_class_path.asset_name) not in ['Blueprint','AnimBlueprint','WidgetBlueprint']:continue
 bp=a.get_asset();assert unreal.BlueprintEditorLibrary.compile_blueprint(bp),str(a.package_name);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['compiled'],audit['asset'];reports.append(audit)
native=[{'asset':a['asset'],'native_parent':a['parent']} for a in reports if a['parent'].startswith('/Script/BogotaVoxel.')];assert len(native)==7,native
(docs/'auditoria_bases_blueprints.json').write_text(json.dumps({'status':'PASS','compiled_blueprints':len(reports),'remaining_native_parents':native,'assets':reports},indent=2),encoding='utf-8');p=docs/'estado_migracion_total_blueprints.json';state=json.loads(p.read_text());state['remaining_inherited_blueprints']=native;state['runtime_blueprints_compiled']=len(reports);p.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');unreal.log('SERVICE_CLEANUP_AND_ALL_BLUEPRINT_AUDIT_PASS '+str(len(reports)))
