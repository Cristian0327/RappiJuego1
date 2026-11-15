import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
report=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game',recursive=True,include_folder=False):
 data=unreal.EditorAssetLibrary.find_asset_data(path)
 if str(data.asset_class_path.asset_name) not in ['Blueprint','WidgetBlueprint','AnimBlueprint']:continue
 bp=unreal.load_asset(path)
 report.append(json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp)))
p=root/'work/blueprint_audit.json';p.write_text(json.dumps(report,indent=2));unreal.log('BLUEPRINT_AUDIT '+str(len(report)))
