import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
r=json.loads(unreal.DeliveryEditorLibrary.validate_map_routes(60))
(root/'work/map_routes_initial.json').write_text(json.dumps(r,indent=2))
unreal.log('MAP_ROUTES_REPORT '+json.dumps(r))
