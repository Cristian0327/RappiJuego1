import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C'
carbp=unreal.load_asset(V.rsplit('.',1)[0])
if 'TransitDoorUser' not in [str(x) for x in E.list_member_variable_names(carbp)]:assert E.add_member_variable(carbp,'TransitDoorUser',E.get_object_reference_type(unreal.Actor))
assert E.compile_blueprint(carbp);assert unreal.EditorAssetLibrary.save_loaded_asset(carbp,only_if_is_dirty=False)
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/fix_solid_vehicles_npc_recovery.py').read_text();part=s[s.index("s=(r/'work/build_pure_station_passenger.py')"):s.index("exec(compile(s,'StationConsistentBasis'")];ns={'r':r};exec(part,ns);s=ns['s'].replace("B='80'","B='160'")
# One actor owns the doorway while approaching, boarding or alighting.
s=s.replace("g.branch('Boardable','Candidate')","field(g,'DoorUser',V,'TransitDoorUser','BusType','AsBP Traffic Vehicle');g.call('DoorOccupied','IsValid',K);g.link('DoorUser','TransitDoorUser','DoorOccupied','Object');op(g,'DoorFree','Not_PreBool',out('DoorOccupied'));op(g,'BoardWithFreeDoor','BooleanAND',out('Candidate'),out('DoorFree'));g.branch('Boardable','BoardWithFreeDoor')")
s=s.replace("g.exec('Boardable','KeepBus')","g.call('QueueRoot','K2_GetRootComponent',A);g.call('QueueSelf','GetOwner','/Script/Engine.ActorComponent');g.link('QueueRoot','ReturnValue','QueueSelf','self');g.node('ReserveBoardDoor','setfield',owner=V,var='TransitDoorUser');g.link('BusType','AsBP Traffic Vehicle','ReserveBoardDoor','self');g.link('QueueSelf','ReturnValue','ReserveBoardDoor','TransitDoorUser');g.exec('Boardable','ReserveBoardDoor');g.exec('ReserveBoardDoor','KeepBus')")
s=s.replace("g.exec('Hide','BudgetRide')","g.node('ReleaseBoardDoor','setfield',owner=V,var='TransitDoorUser',defaults={'TransitDoorUser':'None'});g.link('SavedBus','AsBP Traffic Vehicle','ReleaseBoardDoor','self');g.exec('Hide','ReleaseBoardDoor');g.exec('ReleaseBoardDoor','BudgetRide')")
s=s.replace("g.branch('Alight','ExitReady')","field(g,'ExitDoorUser',V,'TransitDoorUser','SavedBus','AsBP Traffic Vehicle');g.call('ExitDoorBusy','IsValid',K);g.link('ExitDoorUser','TransitDoorUser','ExitDoorBusy','Object');op(g,'ExitDoorFree','Not_PreBool',out('ExitDoorBusy'));op(g,'OrderedExitReady','BooleanAND',out('ExitReady'),out('ExitDoorFree'));g.branch('Alight','OrderedExitReady')")
s=s.replace("g.exec('Alight','NewStation')","g.node('ReserveExitDoor','setfield',owner=V,var='TransitDoorUser');g.link('SavedBus','AsBP Traffic Vehicle','ReserveExitDoor','self');g.link('QueueSelf','ReturnValue','ReserveExitDoor','TransitDoorUser');g.exec('Alight','ReserveExitDoor');g.exec('ReserveExitDoor','NewStation')")
s=s.replace("g.exec('StillAlighting','ShowMesh','else')","g.node('ReleaseExitDoor','setfield',owner=V,var='TransitDoorUser',defaults={'TransitDoorUser':'None'});g.link('SavedBus','AsBP Traffic Vehicle','ReleaseExitDoor','self');g.exec('StillAlighting','ReleaseExitDoor','else');g.exec('ReleaseExitDoor','ShowMesh')")
s=s.replace("g.exec('Hide','ReleaseBoardDoor')","g.call('HideCollision','SetActorEnableCollision',A,bNewActorEnableCollision='false');g.exec('Hide','HideCollision');g.exec('HideCollision','ReleaseBoardDoor')")
s=s.replace("g.exec('ReleaseExitDoor','ShowMesh')","g.call('RestorePlatformCollision','SetActorEnableCollision',A,bNewActorEnableCollision='true');g.exec('ReleaseExitDoor','RestorePlatformCollision');g.exec('RestorePlatformCollision','ShowMesh')")
s=s.replace("op(g,'BoardWithFreeDoor','BooleanAND',out('Candidate'),out('DoorFree'))","op(g,'NotSameBus','NotEqual_ObjectObject',('BusType','AsBP Traffic Vehicle'),('BusActor','BusActor'));op(g,'NextBusCandidate','BooleanAND',out('Candidate'),out('NotSameBus'));op(g,'BoardWithFreeDoor','BooleanAND',out('NextBusCandidate'),out('DoorFree'))");exec(compile(s,'OrderedTransitDoorQueue','exec'),{})
# Spread authored waiting positions; retain station identity, appearance and boarding state.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);counts={'station_passengers':0,'road_motorcycles':0};xs=[-27000,-7000,17000,32000]
for a in actors.get_all_level_actors():
 name=a.get_class().get_name()
 if name=='BP_StationPassenger_C':
  station=a.get_editor_property('Station');slot=a.get_editor_property('PassengerId')%4;a.set_actor_location(unreal.Vector(xs[station]+380+slot*160,0,198),False,True);counts['station_passengers']+=1
 if name=='BP_TwoWheelerCitizen_C' and not a.get_editor_property('Bicycle'):
  a.set_editor_property('RoadMode',True);move=a.get_editor_property('character_movement');move.set_editor_property('max_step_height',0.);move.set_editor_property('use_rvo_avoidance',False);move.set_movement_mode(unreal.MovementMode.MOVE_WALKING);counts['road_motorcycles']+=1
assert unreal.EditorLoadingAndSavingUtils.save_current_level();(r/'work/vehicle_usability_world_placement.json').write_text(json.dumps(counts,indent=2));unreal.log('ORDERED_STATIONS_ROAD_MOTORCYCLES_PASS '+json.dumps(counts))
