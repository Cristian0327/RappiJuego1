import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=d.M;A='/Script/Engine.Actor';K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C';NPC='/Game/World/BlueprintWorld/Traffic/BP_TaxiPassenger.BP_TaxiPassenger_C';LANE='/Game/World/BlueprintWorld/Traffic/BP_TrafficLane.BP_TrafficLane_C'
def asset(n,parent):
 b=unreal.load_asset('/Game/QA/'+n)
 if not b:f=unreal.BlueprintFactory();f.set_editor_property('parent_class',parent);b=T.create_asset(n,'/Game/QA',unreal.Blueprint,f)
 assert E.compile_blueprint(b);return b
lane=asset('BP_TaxiTestLane',unreal.load_class(None,LANE));sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
spline=next(lib.get_object_for_blueprint(lib.get_data(h),lane) for h in sub.k2_gather_subobject_data_for_blueprint(lane) if str(lib.get_variable_name(lib.get_data(h)))=='Route');spline.set_spline_points([unreal.Vector(x,y,2) for x,y in [(-10000,-1000),(10000,-1000),(10000,1000),(-10000,1000)]],unreal.SplineCoordinateSpace.LOCAL,False)
for i in range(4):spline.set_spline_point_type(i,unreal.SplinePointType.LINEAR,False)
spline.set_closed_loop(True,True);assert E.compile_blueprint(lane);assert unreal.EditorAssetLibrary.save_loaded_asset(lane,only_if_is_dirty=False)
bp=asset('BP_TestTaxiTrip',unreal.Actor);d.bp=bp
for n,c in [('Car',V),('Passenger',NPC),('Lane',LANE)]:
 if n not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,n,E.get_object_reference_type(unreal.load_class(None,c)))
 E.set_blueprint_variable_instance_editable(bp,n,True)
for n,t in [('Age','real'),('LastState','int'),('Reserved','bool'),('RearOpened','bool'),('Seated','bool'),('Travelled','bool'),('Alighted','bool')]:
 if n not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,n,E.get_basic_type_by_name(t))
assert E.compile_blueprint(bp)
g=d.Graph();g.get('Car');g.get('Lane');g.call('Rebuild','ExecuteConsoleCommand',K,Command='RebuildNavigation');g.exec('entry','Rebuild');g.call('Init','InitializeRoute',V,AtDistance='3500');g.link('Car','Car','Init','self');g.link('Lane','Lane','Init','Route');g.exec('Rebuild','Init')
for n,v in [('CruiseSpeed','975'),('Speed','975')]:g.node('Init'+n,'setfield',owner=V,var=n,defaults={n:v});g.link('Car','Car','Init'+n,'self')
g.exec('Init','InitCruiseSpeed');g.exec('InitCruiseSpeed','InitSpeed');g.exec('InitSpeed','result');g.build('ReceiveBeginPlay')
g=d.Graph()
for n in ['Car','Passenger','Age','LastState','Reserved','RearOpened','Seated','Travelled','Alighted']:g.get(n)
def field(n,owner,var,ref,pin):g.node(n,'getfield',owner=owner,var=var);g.link(ref,pin,n,'self')
def op(n,fn,a=None,b=None,**kw):
 g.call(n,fn,M,**kw)
 if a:g.link(*a,n,'A')
 if b:g.link(*b,n,'B')
def out(n):return(n,'ReturnValue')
op('NextAge','Add_DoubleDouble',('Age','Age'),('entry','DeltaSeconds'));g.setter('Clock','Age','NextAge');g.exec('entry','Clock');field('Cruise',V,'CruiseSpeed','Car','Car');g.call('Advance','SimulateMovement',V,Clearance='100000');g.link('Car','Car','Advance','self');g.link('entry','DeltaSeconds','Advance','Dt');g.link('Cruise','CruiseSpeed','Advance','DesiredSpeed');g.exec('Clock','Advance');g.call('Render','RenderMovement',V,Alpha='1');g.link('Car','Car','Render','self');g.exec('Advance','Render');g.call('Doors','UpdateDoorPose',V);g.link('Car','Car','Doors','self');g.link('entry','DeltaSeconds','Doors','Dt');g.exec('Render','Doors');field('State',NPC,'State','Passenger','Passenger');op('Changed','NotEqual_IntInt',('State','State'),('LastState','LastState'));g.branch('NewState','Changed');g.exec('Doors','NewState');g.call('StateText','Conv_IntToString','/Script/Engine.KismetStringLibrary');g.link('State','State','StateText','InInt');g.call('StateMsg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='TAXI_TRIP_STATE=');g.link('StateText','ReturnValue','StateMsg','B');g.call('StatePrint','PrintString',K,bPrintToScreen='false');g.link('StateMsg','ReturnValue','StatePrint','InString');g.exec('NewState','StatePrint');g.setter('RememberState','LastState','State','State');tail='StatePrint'
for tag in ['PassengerAt','CarPoint','GoalAt']:
 if tag=='PassengerAt':g.call(tag,'K2_GetActorLocation',A);g.link('Passenger','Passenger',tag,'self');pin='ReturnValue'
 elif tag=='CarPoint':field(tag,V,'NextPosition','Car','Car');pin='NextPosition'
 else:field(tag,NPC,'Goal','Passenger','Passenger');pin='Goal'
 g.call(tag+'Text','Conv_VectorToString','/Script/Engine.KismetStringLibrary');g.link(tag,pin,tag+'Text','InVec');g.call(tag+'Msg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='TAXI_DIAGNOSTIC '+tag+'=');g.link(tag+'Text','ReturnValue',tag+'Msg','B');g.call(tag+'Print','PrintString',K,bPrintToScreen='false');g.link(tag+'Msg','ReturnValue',tag+'Print','InString');g.exec(tail,tag+'Print');tail=tag+'Print'
g.exec(tail,'RememberState');field('RearAlpha',V,'DoorAlphaRearRight','Car','Car');field('Distance',NPC,'TripTravel','Passenger','Passenger');op('HasReserved','Greater_IntInt',('State','State'),B='0');op('RearIsOpen','Greater_DoubleDouble',('RearAlpha','DoorAlphaRearRight'),B='.7');op('IsSeated','EqualEqual_IntInt',('State','State'),B='4');op('DidTravel','Greater_DoubleDouble',('Distance','TripTravel'),B='1000');op('IsAlighted','EqualEqual_IntInt',('State','State'),B='8');last='RememberState';edge='then'
for n,condition in [('Reserved','HasReserved'),('RearOpened','RearIsOpen'),('Seated','IsSeated'),('Travelled','DidTravel'),('Alighted','IsAlighted')]:
 op(n+'Or','BooleanOR',(n,n),out(condition));g.setter('Keep'+n,n,n+'Or');g.exec(last,'Keep'+n,edge)
 if n=='Reserved':g.exec('NewState','Keep'+n,'else')
 last='Keep'+n;edge='then'
op('IdleAgain','EqualEqual_IntInt',('State','State'),B='0');op('Completed','BooleanAND',out('IdleAgain'),('Alighted','Alighted'));op('TimedOut','Greater_DoubleDouble',('Age','Age'),B='80');op('Assess','BooleanOR',out('Completed'),out('TimedOut'));g.branch('Done','Assess');g.exec(last,'Done');g.exec('Done','result','else');last='Done'
for n in ['Reserved','RearOpened','Seated','Travelled','Alighted']:
 g.call(n+'Text','Conv_BoolToString','/Script/Engine.KismetStringLibrary');g.link(n,n,n+'Text','InBool');g.call(n+'Msg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='TAXI_TRIP '+n+'=');g.link(n+'Text','ReturnValue',n+'Msg','B');g.call(n+'Print','PrintString',K,bPrintToScreen='false');g.link(n+'Msg','ReturnValue',n+'Print','InString');g.exec(last,n+'Print');last=n+'Print'
g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true');g.exec(last,'Quit');g.exec('Quit','result');g.build('ReceiveTick');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
path='/Game/QA/PureTaxiTrip';unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level(path);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-50));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(240,60,1));floor.static_mesh_component.set_collision_profile_name('BlockAll');floor.static_mesh_component.set_editor_property('can_ever_affect_navigation',True);bounds=actors.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,100));builder=bounds.get_editor_property('brush_builder')
for n,value in [('x',24000.),('y',6000.),('z',350.)]:builder.set_editor_property(n,value)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.NavigationSystemV1.get_navigation_system(w).on_navigation_bounds_updated(bounds);route=actors.spawn_actor_from_class(lane.generated_class(),unreal.Vector());car=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_TaxiSedan.BP_Traffic_TaxiSedan_C'),unreal.Vector(-6500,-1000,2));passenger=actors.spawn_actor_from_class(unreal.load_class(None,NPC),unreal.Vector(-5000,0,90));model=unreal.get_default_object(unreal.load_asset('/Game/World/BlueprintWorld/Crowd/Models/BP_Citizen00').generated_class()).get_editor_property('mesh');passenger.mesh.set_skeletal_mesh_asset(model.get_skeletal_mesh_asset());passenger.mesh.set_material(0,model.get_material(0));test=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());test.set_editor_property('Car',car);test.set_editor_property('Passenger',passenger);test.set_editor_property('Lane',route);actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,2000,100));w.get_world_settings().set_editor_property('default_game_mode',unreal.load_asset('/Game/QA/BP_TerrainGameMode').generated_class());assert unreal.EditorLoadingAndSavingUtils.save_map(w,path);unreal.log('PURE_TAXI_TRIP_QA_READY')
