import unreal,json,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True);deps={str(a.package_name):[str(p) for p in reg.get_dependencies(a.package_name,opts) or []] for a in reg.get_assets_by_path('/Game',recursive=True)};bad={p for p,ds in deps.items() if any(d.startswith('/Script/BogotaVoxel') for d in ds)}
while True:
 more={p for p,ds in deps.items() if any(d in bad for d in ds)}-bad
 if not more:break
 bad.update(more)
seen=set();todo=['/Game/Maps/Bogota_Blueprint_Integration']
while todo:
 p=todo.pop()
 if p in seen:continue
 seen.add(p);todo.extend(d for d in deps.get(p,[]) if d.startswith('/Game/'))
assert not seen.intersection(bad),sorted(seen.intersection(bad))
(r/'work/native_retirement_plan.json').write_text(json.dumps({'status':'PLAN_ONLY','reachable_packages':len(seen),'native_dependent_packages':sorted(bad),'safe_shipping_root':'/Game/Maps/Bogota_Blueprint_Integration'},indent=2));unreal.log('NATIVE_RETIREMENT_PLAN_SAFE packages='+str(len(bad)))
