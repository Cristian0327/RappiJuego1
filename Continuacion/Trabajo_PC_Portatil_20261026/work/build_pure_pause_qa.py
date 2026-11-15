import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=d.M;A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C'
def asset(n,parent):
 b=unreal.load_asset('/Game/QA/'+n)
 if not b:f=unreal.BlueprintFactory();f.set_editor_property('parent_class',parent);b=T.create_asset(n,'/Game/QA',unreal.Blueprint,f)
 assert E.compile_blueprint(b);return b
bp=asset('BP_TestBlueprintPause',unreal.Actor);d.bp=bp
for n,t in [('StartReal',E.get_basic_type_by_name('real')),('Phase',E.get_basic_type_by_name('int'))]:
 if n not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,n,t)
E.compile_blueprint(bp)
g=d.Graph();g.call('Platform','GetAccurateRealTime',G);g.call('Now','Add_DoubleDouble',M);g.link('Platform','Seconds','Now','A');g.link('Platform','PartialSeconds','Now','B');g.setter('Start','StartReal','Now');g.call('KeepTicking','SetTickableWhenPaused',A,bTickableWhenPaused='true');g.exec('entry','KeepTicking');g.call('EveryFrame','SetActorTickInterval',A,TickInterval='0');g.exec('KeepTicking','EveryFrame');g.exec('EveryFrame','Start');g.exec('Start','result');g.build('ReceiveBeginPlay')
g=d.Graph();g.get('StartReal');g.get('Phase');g.call('Platform','GetAccurateRealTime',G);g.call('Now','Add_DoubleDouble',M);g.link('Platform','Seconds','Now','A');g.link('Platform','PartialSeconds','Now','B');g.call('Age','Subtract_DoubleDouble',M);g.link('Now','ReturnValue','Age','A');g.link('StartReal','StartReal','Age','B');g.call('Player','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Player','ReturnValue','Rider','Object');last='entry';edge='then'
for i,t in [(0,.5),(1,.9),(2,1.3)]:
 n='P'+str(i);g.call(n+'Phase','EqualEqual_IntInt',M,B=str(i));g.link('Phase','Phase',n+'Phase','A');g.call(n+'Time','Greater_DoubleDouble',M,B=str(t));g.link('Age','ReturnValue',n+'Time','A');g.call(n+'Due','BooleanAND',M);g.link(n+'Phase','ReturnValue',n+'Due','A');g.link(n+'Time','ReturnValue',n+'Due','B');g.branch(n,n+'Due');g.exec(last,n,edge);last=n;edge='else';tail=n
 if i==0:
  g.call('Pause','PausePressed',R);g.link('Rider','AsBP Blueprint Rider','Pause','self');g.exec(tail,'Pause');tail='Pause'
 else:
  g.call(n+'Paused','IsGamePaused',G);src=n+'Paused'
  if i==2:g.call('Unpaused','Not_PreBool',M);g.link(src,'ReturnValue','Unpaused','A');src='Unpaused'
  g.call(n+'Text','Conv_BoolToString','/Script/Engine.KismetStringLibrary');g.link(src,'ReturnValue',n+'Text','InBool');g.call(n+'Msg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='BLUEPRINT_PAUSE '+('PAUSED=' if i==1 else 'RESUMED='));g.link(n+'Text','ReturnValue',n+'Msg','B');g.call(n+'Print','PrintString',K,bPrintToScreen='false');g.link(n+'Msg','ReturnValue',n+'Print','InString');g.exec(tail,n+'Print');tail=n+'Print'
  if i==1:g.call('Resume','PausePressed',R);g.link('Rider','AsBP Blueprint Rider','Resume','self');g.exec(tail,'Resume');tail='Resume'
  else:g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true');g.exec(tail,'Quit');g.exec('Quit','result');continue
 g.setter(n+'Next','Phase',value=str(i+1));g.exec(tail,n+'Next');g.exec(n+'Next','result')
g.exec(last,'result','else');g.build('ReceiveTick');assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());tick=c.get_editor_property('primary_actor_tick');tick.set_editor_property('tick_even_when_paused',True);c.set_editor_property('primary_actor_tick',tick);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
gm=asset('BP_PauseGameMode',unreal.GameModeBase);c=unreal.get_default_object(gm.generated_class());c.set_editor_property('default_pawn_class',unreal.load_class(None,'/Game/QA/BP_RoadRiderFixture.BP_RoadRiderFixture_C'));c.set_editor_property('hud_class',unreal.load_class(None,'/Game/Delivery/BlueprintGameplay/UI/BP_BlueprintHUD.BP_BlueprintHUD_C'));assert unreal.EditorAssetLibrary.save_loaded_asset(gm,only_if_is_dirty=False)
path='/Game/QA/PureBlueprintPause';unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level(path);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-50));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(40,40,1));floor.static_mesh_component.set_collision_profile_name('BlockAll');actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(0,0,100));actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();w.get_world_settings().set_editor_property('default_game_mode',gm.generated_class());assert unreal.EditorLoadingAndSavingUtils.save_map(w,path);unreal.log('PURE_PAUSE_QA_READY')
