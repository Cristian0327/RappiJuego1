import unreal,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
report=[]
for a in actors:
 n=a.get_class().get_name()
 if any(t in n for t in ['TrafficManager','ResidentialRouteAssembler','DeliveryStore','CivilMotorcycle','PoliceMotorcycle','TwoWheelerCitizen']):
  row=dict(name=a.get_name(),cls=n,at=list(a.get_actor_location().to_tuple()),props={})
  for prop in ['UrbanCrossingCenters','UrbanCrossingForwards','UrbanSignalGroups','UrbanRoadWidths','UrbanStopOffsets','BuildingCenters','BuildingExtents','Route','RouteIndex','RoadMode','Bicycle','PointID']:
   try:row['props'][prop]=str(a.get_editor_property(prop))
   except:pass
  report.append(row)
(P/'actors.json').write_text(json.dumps(report,indent=2))
for path in ['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager','/Game/Delivery/BlueprintGameplay/World/BP_ResidentialRouteAssembler','/Game/Traffic/Services/BP_TwoWheelerCitizen']:
 b=unreal.load_asset(path);(P/(b.get_name()+'_audit.json')).write_text(unreal.DeliveryEditorLibrary.audit_blueprint(b))
unreal.log('LIBRARY_METHODS '+str([n for n in dir(unreal.DeliveryEditorLibrary) if any(t in n for t in ['graph','blueprint','pin'])]))
