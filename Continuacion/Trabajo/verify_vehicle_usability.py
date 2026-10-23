import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;K='/Script/Engine.KismetSystemLibrary';A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C'

for path,names in [('/Game/World/BlueprintWorld/Traffic/BP_TaxiPassenger',['State','Age','HailElapsed','CitizenId']),('/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider',['RoadActive'])]:
 b=unreal.load_asset(path)
 for name in names:E.set_blueprint_variable_instance_editable(b,name,True)
 assert E.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
# Focused Blueprint VM checks, using the actual game classes.
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);checks={};created=[]
def ck(n,v):checks[n]=bool(v);assert v,n
def spawn(path,at):
 a=actors.spawn_actor_from_class(unreal.load_class(None,path),unreal.Vector(*at));created.append(a);return a
try:
 bike=spawn('/Game/Delivery/BlueprintGameplay/Vehicles/BP_DeliveryTwoWheeler.BP_DeliveryTwoWheeler_C',(80000,80000,0));bike.call_method('SetRidden',(False,));box=bike.get_editor_property('ParkedTrafficBody');ck('parked_bike_query_collision',box.get_collision_enabled()==unreal.CollisionEnabled.QUERY_ONLY);ck('traffic_probe_sees_bike_object_channel',box.get_collision_object_type()==unreal.CollisionChannel.ECC_PAWN);bike.call_method('SetRidden',(True,));ck('ridden_bike_no_duplicate_blocker',box.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION)
 taxi=spawn('/Game/World/BlueprintWorld/Traffic/BP_TaxiPassenger.BP_TaxiPassenger_C',(90000,90000,90));taxi.call_method('ReceiveBeginPlay');taxi.set_editor_property('State',0);taxi.set_editor_property('Age',3.);taxi.set_editor_property('HailElapsed',21.);taxi.set_editor_property('CitizenId',0);taxi.call_method('ReceiveTick',(.25,));ck('taxi_hail_has_timeout',taxi.get_editor_property('State')==10);taxi.set_editor_property('Age',13.);taxi.call_method('ReceiveTick',(.25,));ck('taxi_cooldown_retries',taxi.get_editor_property('State')==0)
 rider=spawn(R,(85000,85000,100));mesh=rider.get_editor_property('mesh');ck('hero_full_frame_animation',not mesh.get_editor_property('enable_update_rate_optimizations'));ck('hero_pose_refresh_visible_or_hidden',mesh.get_editor_property('visibility_based_anim_tick_option')==unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
 rider.set_editor_property('RoadActive',True);rider.call_method('ApplyRoadCameraSpacing');boom=rider.get_editor_property('CameraBoom');ck('car_camera_distance',abs(boom.get_editor_property('target_arm_length')-650)<1);ck('car_camera_above_roof',boom.get_editor_property('socket_offset').z>=170);ck('camera_after_physics',boom.get_editor_property('primary_component_tick').get_editor_property('tick_group')==unreal.TickingGroup.TG_POST_PHYSICS)
 # Save a concise proof without claiming an FPS guarantee for all hardware.
 (r/'work/vehicle_usability_vm.json').write_text(json.dumps({'status':'PASS','checks':checks,'count':len(checks)},indent=2));unreal.log('VEHICLE_USABILITY_VM_PASS '+str(len(checks)))
finally:
 for a in reversed(created):actors.destroy_actor(a)
# End-to-end station queue test: four passengers use the same doorway sequentially.
s=(r/'work/build_pure_station_passenger_qa.py').read_text(encoding='utf-8-sig');s=s.replace("B='6'","B='18'").replace("B='7'","B='19'").replace("B='14'","B='55'").replace("'TransitDwell':10","'TransitDwell':18").replace("i*50","i*160").replace("/Game/QA/PureStationPassenger","/Game/QA/OrderedStationUsability");exec(compile(s,'OrderedStationEndToEnd','exec'),{});unreal.log('VEHICLE_USABILITY_FINAL_BUILD_PASS')
