import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
out={}
for p in ['/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle']:
 out[p]=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset(p)))
(r/'work/drive_door_audit.json').write_text(json.dumps(out,indent=2));unreal.log('DRIVE_DOOR_AUDIT_READY')
