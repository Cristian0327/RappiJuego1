import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
candidates=[]
for directory in ['/Game/Delivery/Review/Pizzeria','/Game/Delivery/Animation/MixamoCandidate']:
 candidates.extend(unreal.EditorAssetLibrary.list_assets(directory,recursive=True,include_folder=False))
packages={p.split('.')[0] for p in candidates};report=[]
for path in candidates:
 refs=unreal.EditorAssetLibrary.find_package_referencers_for_asset(path,load_assets_to_confirm=True)
 external=[r for r in refs if r.split('.')[0] not in packages]
 assert not external,(path,external)
 report.append({'asset':path,'referencers':list(refs)})
for item in report:
 assert unreal.EditorAssetLibrary.delete_asset(item['asset']),item['asset']
 item['deleted']=True
(root/'work/rejected_review_cleanup.json').write_text(json.dumps(report,indent=2))
