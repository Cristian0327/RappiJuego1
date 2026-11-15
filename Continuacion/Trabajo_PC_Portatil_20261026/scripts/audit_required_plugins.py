"""Read real package dependencies before considering optional editor plugins."""
import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);seen=set();pending=['/Game/Maps/MapaCompleto_Integration','/Game/QA/PurePhoneRuntime','/Game/QA/CPUIsolation'];options=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)
while pending:
 p=pending.pop()
 if p in seen:continue
 seen.add(p)
 pending.extend(str(x) for x in (reg.get_dependencies(p,options) or []))
modules=sorted(p.split('/')[2] for p in seen if p.startswith('/Script/'));roots=sorted(set(p.split('/')[1] for p in seen if p.startswith('/') and len(p.split('/'))>2 and not p.startswith(('/Game/','/Engine/','/Script/'))))
(R/'AdversarialQA_20261026/required_packages.json').write_text(json.dumps(dict(package_count=len(seen),script_modules=modules,external_roots=roots,packages=sorted(seen)),indent=2));unreal.log('REQUIRED_PLUGIN_DEPENDENCIES_AUDITED')
