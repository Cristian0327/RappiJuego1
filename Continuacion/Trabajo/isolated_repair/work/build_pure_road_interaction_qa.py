import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A='/Script/Engine.Actor';K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics';M=d.M;R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C';ROAD='/Game/Delivery/BlueprintGameplay/Player/BP_RoadInteraction.BP_RoadInteraction_C';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C'
def asset(n,parent):
 p='/Game/QA/'+n;b=unreal.load_asset(p)
 if not b:f=unreal.BlueprintFactory();f.set_editor_property('parent_class',parent);b=T.create_asset(n,'/Game/QA',unreal.Blueprint,f)
 assert E.compile_blueprint(b);return b
pawn=asset('BP_RoadRiderFixture',unreal.load_class(None,R));c=unreal.get_default_object(pawn.generated_class());c.set_editor_property('BlueprintReady',True);assert unreal.EditorAssetLibrary.save_loaded_asset(pawn,only_if_is_dirty=False);gm=asset('BP_RoadRiderGameMode',unreal.GameModeBase);unreal.get_default_object(gm.generated_class()).set_editor_property('default_pawn_class',pawn.generated_class());assert unreal.EditorAssetLibrary.save_loaded_asset(gm,only_if_is_dirty=False);bp=asset('BP_TestRoadInteraction',unreal.Actor);d.bp=bp
for n in ['Road','Car']:
 if n not in [str(x) for x in E.list_member_variable_names(bp)]:E.add_member_variable(bp,n,E.get_object_reference_type(unreal.Actor))
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);g=d.Graph();g.variables=[{'name':'Age','default':'0'},{'name':'Phase','type':'int','default':'0'}];g.get('Age');g.get('Phase');g.get('Road');g.get('Car');g.node('RoadType','cast',type=ROAD);g.link('Road','Road','RoadType','Object');g.node('CarType','cast',type=V);g.link('Car','Car','CarType','Object');g.call('Player','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Player','ReturnValue','Rider','Object');g.node('Delivery','getfield',owner=R,var='Delivery');g.link('Rider','AsBP Blueprint Rider','Delivery','self');g.call('Clock','Add_DoubleDouble',M);g.link('Age','Age','Clock','A');g.link('entry','DeltaSeconds','Clock','B');g.setter('AgeNow','Age','Clock');g.exec('entry','AgeNow')
def compare(n,fn,a,b=None,**kw):
 g.call(n,fn,M,**kw);g.link(*a,n,'A')
 if b:g.link(*b,n,'B')
def report(n,start,node,pin='ReturnValue'):
 g.call(n+'Text','Conv_BoolToString','/Script/Engine.KismetStringLibrary');g.link(node,pin,n+'Text','InBool');g.call(n+'Msg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='ROAD_PLAYER '+n+'=');g.link(n+'Text','ReturnValue',n+'Msg','B');g.call(n+'Print','PrintString',K,bPrintToScreen='false');g.link(n+'Msg','ReturnValue',n+'Print','InString');g.exec(start,n+'Print');return n+'Print'
def field(n,owner,var,target,pin):g.node(n,'getfield',owner=owner,var=var);g.link(target,pin,n,'self')
def setR(n,var,val):g.node(n,'setfield',owner=R,var=var,defaults={var:val});g.link('Rider','AsBP Blueprint Rider',n,'self')
last='AgeNow';edge='then'
for i,seconds in [(0,.7),(1,1.25),(2,2.7),(3,4.1),(4,6.2),(5,8.3)]:
 tag='P'+str(i);compare(tag+'Phase','EqualEqual_IntInt',('Phase','Phase'),B=str(i));compare(tag+'Time','Greater_DoubleDouble',('Age','Age'),B=str(seconds));compare(tag+'Due','BooleanAND',(tag+'Phase','ReturnValue'),(tag+'Time','ReturnValue'));g.branch(tag,tag+'Due');g.exec(last,tag,edge);last=tag;edge='else';g.setter(tag+'Next','Phase',value=str(i+1))
 if i==0:
  g.node('Developer','setfield',owner=CORE,var='DeveloperMode',defaults={'DeveloperMode':'true'});g.link('Delivery','Delivery','Developer','self');g.call('PC','GetPlayerController',G,PlayerIndex='0');g.call('IgnoreRealKeys','DisableInput',A);g.link('Rider','AsBP Blueprint Rider','IgnoreRealKeys','self');g.link('PC','ReturnValue','IgnoreRealKeys','PlayerController');g.exec(tag,'IgnoreRealKeys');g.exec('IgnoreRealKeys','Developer');g.call('Enter','MountPressed',R);g.link('Rider','AsBP Blueprint Rider','Enter','self');g.call('UnlockCars','SetRoadCarsEnabled',ROAD,Enabled='true');g.link('RoadType','AsBP Road Interaction','UnlockCars','self');g.exec('Developer','UnlockCars');g.exec('UnlockCars','Enter');field('EntryMode',ROAD,'Mode','RoadType','AsBP Road Interaction');compare('Entered','EqualEqual_IntInt',('EntryMode','Mode'),B='1');tail=report('ENTER_REQUEST','Enter','Entered')
 elif i==1:
  field('DoorOpening',V,'DoorAlphaLeft','CarType','AsBP Traffic Vehicle');compare('DoorOpened','Greater_DoubleDouble',('DoorOpening','DoorAlphaLeft'),B='.7');tail=report('DOOR_ACTUALLY_OPEN',tag,'DoorOpened')
 elif i==2:
  field('ModeAtSeat',ROAD,'Mode','RoadType','AsBP Road Interaction');compare('Seated','EqualEqual_IntInt',('ModeAtSeat','Mode'),B='2');tail=report('SEATED',tag,'Seated');setR('Throttle','ForwardInput','1');g.exec(tail,'Throttle');setR('Steer','SideInput','.3');g.exec('Throttle','Steer');tail='Steer'
 elif i==3:
  setR('Brake','ForwardInput','0');g.exec(tag,'Brake');setR('Straight','SideInput','0');g.exec('Brake','Straight');tail='Straight'
 elif i==4:
  g.call('Exit','MountPressed',R);g.link('Rider','AsBP Blueprint Rider','Exit','self');g.exec(tag,'Exit');field('ExitMode',ROAD,'Mode','RoadType','AsBP Road Interaction');compare('Exiting','EqualEqual_IntInt',('ExitMode','Mode'),B='3');tail=report('EXIT_REQUEST','Exit','Exiting')
 else:
  field('FinalMode',ROAD,'Mode','RoadType','AsBP Road Interaction');compare('WalkingAgain','EqualEqual_IntInt',('FinalMode','Mode'),B='0');tail=report('WALKING_RESTORED',tag,'WalkingAgain');g.call('CarAt','K2_GetActorLocation',A);g.link('Car','Car','CarAt','self');g.call('CarAxes','BreakVector',M);g.link('CarAt','ReturnValue','CarAxes','InVec');compare('Moved','Greater_DoubleDouble',('CarAxes','X'),B='150100');tail=report('CAR_MOVED',tail,'Moved');g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true');g.exec(tail,'Quit');g.exec('Quit','result');continue
 g.exec(tail,tag+'Next');g.exec(tag+'Next','result')
g.exec(last,'result','else');g.build('ReceiveTick');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
path='/Game/QA/PureRoadInteraction';unreal.EditorLoadingAndSavingUtils.load_map(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level(path);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():actors.destroy_actor(a)
floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(150000,150000,-50));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(400,400,1));floor.static_mesh_component.set_collision_profile_name('BlockAll');actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(150000,149803,100));car=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_Private.BP_Traffic_Private_C'),unreal.Vector(150000,150000,2));road=actors.spawn_actor_from_class(unreal.load_class(None,ROAD),unreal.Vector());test=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());test.set_editor_property('Road',road);test.set_editor_property('Car',car);w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();w.get_world_settings().set_editor_property('default_game_mode',gm.generated_class());assert unreal.EditorLoadingAndSavingUtils.save_map(w,path);unreal.log('PURE_ROAD_PLAYER_QA_READY')




