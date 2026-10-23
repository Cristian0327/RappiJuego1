import unreal,json,sys
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');P.mkdir(exist_ok=True)
assert 'isolated_repair' in Path(unreal.Paths.project_dir()).parts
E=unreal.BlueprintEditorLibrary
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
paths=['/Game/World/BlueprintWorld/Traffic/BP_TrafficManager','/Game/World/BlueprintWorld/Traffic/BP_TrafficJunction','/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle','/Game/Traffic/Services/BP_VoxelRoadVehicle','/Game/Traffic/Services/BP_TwoWheelerCitizen','/Game/World/BogotaUrban/BP_BogotaServiceSignals','/Game/World/BogotaUrban/BP_BogotaSignal','/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore','/Game/Delivery/BlueprintGameplay/World/BP_ResidentialRouteAssembler','/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore','/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone','/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry']
out={}
def conv(v):
 if isinstance(v,(int,float,str,bool)) or v is None:return v
 if isinstance(v,unreal.Vector):return list(v.to_tuple())
 if isinstance(v,unreal.Vector2D):return [v.x,v.y]
 if isinstance(v,unreal.Rotator):return [v.pitch,v.yaw,v.roll]
 if isinstance(v,unreal.Transform):return dict(location=conv(v.translation),rotation=conv(v.rotation.rotator()),scale=conv(v.scale3d))
 if isinstance(v,unreal.Array):return [conv(q) for q in v]
 return str(v)
for path in paths:
 b=unreal.load_asset(path)
 if not b:continue
 (P/(b.get_name()+'_audit.json')).write_text(unreal.DeliveryEditorLibrary.audit_blueprint(b))
 c=unreal.get_default_object(b.generated_class());out[path]={}
 for n in E.list_member_variable_names(b):
  try:out[path][str(n)]=conv(c.get_editor_property(str(n)))
  except Exception:pass
(P/'defaults.json').write_text(json.dumps(out))
actors=[]
for a in aa.get_all_level_actors():
 row=dict(name=a.get_name(),cls=a.get_class().get_name(),position=conv(a.get_actor_location()),rotation=conv(a.get_actor_rotation()),scale=conv(a.get_actor_scale3d()),properties={})
 for n in ['StoreId','Theme','ResidentialRoutes','Homes','Stores','BuildingCenters','BuildingExtents','Route','RouteIndex','RoadActors','RoadSpeeds','JunctionCentres','UrbanCrossingCenters','UrbanCrossingForwards','UrbanSignalGroups','UrbanRoadWidths','UrbanStopOffsets']:
  try:row['properties'][n]=conv(a.get_editor_property(n))
  except:pass
 actors.append(row)
(P/'actors.json').write_text(json.dumps(actors))
ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;lanes=[]
for i in range(7):
 b=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i));curve=next(lib.get_object_for_blueprint(lib.get_data(h),b) for h in ss.k2_gather_subobject_data_for_blueprint(b) if str(lib.get_variable_name(lib.get_data(h)))=='Route')
 lanes.append([conv(curve.get_location_at_spline_point(j,unreal.SplineCoordinateSpace.LOCAL)) for j in range(curve.get_number_of_spline_points())])
(P/'actual_lanes.json').write_text(json.dumps(lanes))
unreal.log('ADAPTATION_V2_AUDIT_READY')
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
