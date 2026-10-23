import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A='/Script/Engine.Actor';M=d.M;K='/Script/Engine.KismetSystemLibrary';AL='/Script/Engine.KismetArrayLibrary';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C';TM='/Game/World/BlueprintWorld/Traffic/BP_TrafficManager.BP_TrafficManager_C'
def asset(n,parent):
 b=unreal.load_asset('/Game/QA/'+n)
 if not b:f=unreal.BlueprintFactory();f.set_editor_property('parent_class',parent);b=T.create_asset(n,'/Game/QA',unreal.Blueprint,f)
 assert E.compile_blueprint(b);return b
fixture=asset('BP_FarTrafficManagerFixture',unreal.load_class(None,TM));d.bp=fixture
for fn in ['ReceiveBeginPlay','ReceiveTick']:
 g=d.Graph();g.exec('entry','result');g.build(fn)
assert E.compile_blueprint(fixture);unreal.EditorAssetLibrary.save_loaded_asset(fixture,only_if_is_dirty=False)
bp=asset('BP_TestFarTrafficCollision',unreal.Actor);d.bp=bp
for n in ['NearCar','FarCar','Manager']:
 if n not in [str(x) for x in E.list_member_variable_names(bp)]:E.add_member_variable(bp,n,E.get_object_reference_type(unreal.Actor))
 E.set_blueprint_variable_instance_editable(bp,n,True)
E.compile_blueprint(bp);g=d.Graph()
for n in ['NearCar','FarCar','Manager']:g.get(n)
g.node('NearType','cast',type=V);g.link('NearCar','NearCar','NearType','Object');g.node('FarType','cast',type=V);g.link('FarCar','FarCar','FarType','Object');g.node('ManagerType','cast',type=TM);g.link('Manager','Manager','ManagerType','Object');g.call('Age','GetGameTimeSinceCreation',A);g.call('Due','Greater_DoubleDouble',M,B='.5');g.link('Age','ReturnValue','Due','A');g.branch('Ready','Due');g.exec('entry','Ready');g.exec('Ready','result','else');last='Ready'
for tag,x in [('Near',1000),('Far',50000)]:
 for var in ['NextPosition','PreviousPosition']:
  n=tag+var;g.node(n,'setfield',owner=V,var=var,defaults={var:'(X='+str(x)+',Y=0,Z=2)'});g.link(tag+'Type','AsBP Traffic Vehicle',n,'self');g.exec(last,n);last=n
 g.node(tag+'Vehicles','getfield',owner=TM,var='Vehicles');g.link('ManagerType','AsBP Traffic Manager',tag+'Vehicles','self');g.call(tag+'Add','Array_Add',AL);g.link(tag+'Vehicles','Vehicles',tag+'Add','TargetArray');g.link(tag+'Type','AsBP Traffic Vehicle',tag+'Add','NewItem');g.exec(last,tag+'Add');last=tag+'Add'
g.call('Render','RenderTraffic',TM,Alpha='1');g.link('ManagerType','AsBP Traffic Manager','Render','self');g.exec(last,'Render')
for n,car,fn in [('NearCollision','NearCar','GetActorEnableCollision'),('FarCollision','FarCar','GetActorEnableCollision'),('FarTick','FarCar','IsActorTickEnabled')]:
 g.call(n,fn,A);g.link(car,car,n,'self')
for n,src in [('FarNoCollision','FarCollision'),('FarNoTick','FarTick')]:g.call(n,'Not_PreBool',M);g.link(src,'ReturnValue',n,'A')
g.call('CollisionCorrect','BooleanAND',M);g.link('NearCollision','ReturnValue','CollisionCorrect','A');g.link('FarNoCollision','ReturnValue','CollisionCorrect','B');g.call('Correct','BooleanAND',M);g.link('CollisionCorrect','ReturnValue','Correct','A');g.link('FarNoTick','ReturnValue','Correct','B');g.call('Text','Conv_BoolToString','/Script/Engine.KismetStringLibrary');g.link('Correct','ReturnValue','Text','InBool');g.call('Msg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='FAR_TRAFFIC_NO_GHOST_COLLISION=');g.link('Text','ReturnValue','Msg','B');g.call('Print','PrintString',K,bPrintToScreen='false');g.link('Msg','ReturnValue','Print','InString');g.exec('Render','Print');g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true');g.exec('Print','Quit');g.exec('Quit','result');g.build('ReceiveTick');assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
path='/Game/QA/PureFarTrafficCollision';unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level(path);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);cl=unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_Private.BP_Traffic_Private_C');near=actors.spawn_actor_from_class(cl,unreal.Vector(1000,0,2));far=actors.spawn_actor_from_class(cl,unreal.Vector(50000,0,2));manager=actors.spawn_actor_from_class(fixture.generated_class(),unreal.Vector());test=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());test.set_editor_property('NearCar',near);test.set_editor_property('FarCar',far);test.set_editor_property('Manager',manager);actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,0,100));w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();w.get_world_settings().set_editor_property('default_game_mode',unreal.load_asset('/Game/QA/BP_TerrainGameMode').generated_class());assert unreal.EditorLoadingAndSavingUtils.save_map(w,path);unreal.log('PURE_FAR_TRAFFIC_QA_READY')
