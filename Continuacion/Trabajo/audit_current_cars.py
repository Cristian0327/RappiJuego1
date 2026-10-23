import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for n,p in [('road','/Game/Delivery/BlueprintGameplay/Player/BP_RoadInteraction'),('traffic','/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle')]:
 a=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset(p)));(r/('work/current_'+n+'_audit.json')).write_text(json.dumps(a,indent=2))
unreal.log('CAR_AUDIT_PASS')
