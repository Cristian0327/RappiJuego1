import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;out={}
for p in ['/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/Delivery/BlueprintGameplay/Player/BP_RoadInteraction','/Game/Traffic/Transit/BP_StationPassenger','/Game/World/BlueprintWorld/Traffic/BP_TaxiPassenger']:
 out[p]=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset(p)))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[]
for a in actors.get_all_level_actors():
 c=a.get_class().get_name()
 if 'TwoWheelerCitizen' in c or 'StationPassenger' in c:
  row={'name':a.get_name(),'class':c,'at':str(a.get_actor_location())}
  for prop in ['Bicycle','RoadMode','Route','PassengerId','Station']:
   try:row[prop]=str(a.get_editor_property(prop))
   except:pass
  rows.append(row)
out['map_actors']=rows;(r/'work/usability_vehicle_audit.json').write_text(json.dumps(out,indent=2));unreal.log('USABILITY_VEHICLE_AUDIT_READY')
