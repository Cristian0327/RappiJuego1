import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';PHONE='/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.WBP_BlueprintPhone_C';M=d.M;G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';U='/Script/UMG.UserWidget';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset('/Game/QA/BP_TestPurePhoneRuntime') or T.create_asset('BP_TestPurePhoneRuntime','/Game/QA',unreal.Blueprint,f);d.bp=bp;g=d.Graph();g.variables=[{'name':'Age','default':'0'},{'name':'Stage','default':'0'}];g.get('Age');g.get('Stage');g.call('Elapsed','Add_DoubleDouble',M);g.link('Age','Age','Elapsed','A');g.link('entry','DeltaSeconds','Elapsed','B');g.setter('Now','Age','Elapsed');g.exec('entry','Now');g.call('Pawn','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Pawn','ReturnValue','Rider','Object');g.node('Core','getfield',owner=R,var='Delivery');g.link('Rider','AsBP Blueprint Rider','Core','self');g.call('Valid','IsValid',K);g.link('Core','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('Now','Ready');g.exec('Ready','result','else');g.node('Widget','getfield',owner=CORE,var='PhoneWidget');g.link('Core','Delivery','Widget','self');g.node('Phone','cast',type=PHONE);g.link('Widget','PhoneWidget','Phone','Object');p='AsWBP Blueprint Phone';last='Ready';edge='then';stage=0;checks=[]
def phase(id,t):
 global last,edge,stage
 g.call(id+'Time','Greater_DoubleDouble',M,B=str(t));g.link('Age','Age',id+'Time','A');g.call(id+'Stage','NearlyEqual_FloatFloat',M,B=str(stage),ErrorTolerance='.01');g.link('Stage','Stage',id+'Stage','A');g.call(id+'OK','BooleanAND',M);g.link(id+'Time','ReturnValue',id+'OK','A');g.link(id+'Stage','ReturnValue',id+'OK','B');g.branch(id,id+'OK');g.exec(last,id,edge);last=id;edge='else';stage+=1;return id

def advance(start):
 tag='Step'+str(stage);g.setter(tag,'Stage',value=str(stage));g.exec(start,tag);g.exec(tag,'result')
def report(label,start,node,pin='ReturnValue'):
 tag='Report'+str(len(checks));g.call(tag+'Text','Conv_BoolToString','/Script/Engine.KismetStringLibrary');g.link(node,pin,tag+'Text','InBool');g.call(tag+'Msg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='PURE_PHONE_RUNTIME '+label+'=');g.link(tag+'Text','ReturnValue',tag+'Msg','B');g.call(tag,'PrintString',K,bPrintToScreen='false',bPrintToLog='true');g.link(tag+'Msg','ReturnValue',tag,'InString');g.exec(start,tag);advance(tag);checks.append(label)

def callcore(id,fn,start):g.call(id,fn,CORE);g.link('Core','Delivery',id,'self');g.exec(start,id);return id
p0=phase('Create',1.);n=callcore('Ensure','EnsurePhoneWidget',p0);report('CREATED',n,n)
p0=phase('Open',1.3);n=callcore('Toggle','TogglePhone',p0);advance(n)
p0=phase('Opened',1.5);g.node('OpenState','getfield',owner=CORE,var='PhoneOpen');g.link('Core','Delivery','OpenState','self');report('OPEN_STATE',p0,'OpenState','PhoneOpen')
p0=phase('Viewport',1.6);g.call('InViewport','IsInViewport',U);g.link('Phone',p,'InViewport','self');report('PRESENT_IN_VIEWPORT',p0,'InViewport')
for i,(name,page,fn) in enumerate([('HOME',0,'OpenHome'),('MAP',1,'OpenMap'),('ORDERS',2,'OpenOrders'),('UPGRADES',3,'OpenShop'),('GARAGE',4,'OpenCatalog'),('ACTIVE',5,'OpenActiveOrders'),('CARGO',6,'OpenCargo')]):
 p0=phase('Show'+name,1.8+i*.75);g.call('Page'+name,fn,PHONE);g.link('Phone',p,'Page'+name,'self');g.exec(p0,'Page'+name);g.node('State'+name,'getfield',owner=PHONE,var='Page');g.link('Phone',p,'State'+name,'self');g.call('Correct'+name,'EqualEqual_IntInt',M,B=str(page));g.link('State'+name,'Page','Correct'+name,'A');report(name,'Page'+name,'Correct'+name)
 p0=phase('Screenshot'+name,2.+i*.75);g.call('Shot'+name,'ExecuteConsoleCommand',K,Command='Shot showui filename="'+str(r/('work/PurePhoneVisualQA/'+name+'.png')).replace('\\','/')+'"');g.exec(p0,'Shot'+name);advance('Shot'+name)
p0=phase('Close',7.3);n=callcore('ClosePhone','ClosePhoneForWorld',p0);advance(n)
p0=phase('ClosedState',7.5);g.call('Closed','Not_PreBool',M);g.link('OpenState','PhoneOpen','Closed','A');report('CLOSED_STATE',p0,'Closed')
p0=phase('PersistentHUD',7.6);g.call('HUDInViewport','IsInViewport',U);g.link('Phone',p,'HUDInViewport','self');report('HUD_PERSISTS_ON_CLOSE',p0,'HUDInViewport')
p0=phase('Finish',8.);g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true');g.exec(p0,'Quit');g.exec('Quit','result');g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PureCityRoutes');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_class().get_name().startswith('BP_TestPureCityRoutes'):actors.destroy_actor(a)
actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-6000,14000,180));actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/BP_WorldPresentation.BP_WorldPresentation_C'),unreal.Vector());world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,'/Game/QA/BP_PureRiderGameMode.BP_PureRiderGameMode_C'));assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/PurePhoneRuntime');(r/'work/PurePhoneVisualQA').mkdir(exist_ok=True);unreal.log('PURE_PHONE_RUNTIME_MAP_BUILT_PASS checks='+str(len(checks)))

