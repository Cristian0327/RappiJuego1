import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True);bases=[];deps=[];calls=[]
for a in reg.get_assets_by_path('/Game',recursive=True):
 if str(a.package_name).startswith('/Game/QA/'):continue
 native=[str(p) for p in (reg.get_dependencies(a.package_name,opts) or []) if str(p).startswith('/Script/BogotaVoxel')]
 if native:deps.append({'asset':str(a.package_name),'dependencies':native})
 if str(a.asset_class_path.asset_name) not in ['Blueprint','WidgetBlueprint','AnimBlueprint']:continue
 b=a.get_asset();audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b))
 if audit['parent'].startswith('/Script/BogotaVoxel'):bases.append({'asset':audit['asset'],'parent':audit['parent']})
 for g in audit['graphs']:
  if g['native_calls']:calls.append({'asset':audit['asset'],'graph':g['name'],'calls':g['native_calls']})
result={'status':'IN_PROGRESS','native_bases_remaining':bases,'direct_native_dependencies':deps,'custom_native_calls':calls};(r/'work/current_native_dependencies_20261017.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');unreal.log('NATIVE_DEPENDENCY_AUDIT_FINISHED bases='+str(len(bases))+' assets='+str(len(deps))+' graphs='+str(len(calls)))
