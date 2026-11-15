import unreal,sys,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/QA';name='BP_TestDeveloperDoors';path=folder+'/'+name
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else tools.create_asset(name,folder,unreal.Blueprint,f)
X=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform'));known=[str(x).split(':')[-1] for x in E.list_member_variable_names(bp)]
for n,t in {'Body':E.get_object_reference_type(unreal.PoseableMeshComponent),'RestCar':X,'RestBus':X}.items():
 if n not in known:E.add_member_variable(bp,n,t)
E.compile_blueprint(bp);d.bp=bp;M=d.M;S='/Script/Engine.KismetSystemLibrary';A='/Script/Engine.Actor';G='/Script/Engine.GameplayStatics';P='/Script/Engine.PoseableMeshComponent';SK='/Script/Engine.SkinnedMeshComponent';R='/Script/BogotaVoxel.BogotaPlayer';D='/Script/BogotaVoxel.DeliveryComponent';C='/Game/Delivery/Developer/BP_DeveloperVehicleDoors.BP_DeveloperVehicleDoors_C';STR='/Script/Engine.KismetStringLibrary'
g=d.Graph();g.get('Body');g.call('Transform','MakeTransform',M,Scale='(X=1,Y=1,Z=1)');g.call('Add','AddComponentByClass',A,Class=P,bManualAttachment='false',bDeferredFinish='false');g.link('Transform','ReturnValue','Add','RelativeTransform');g.exec('entry','Add');g.node('Cast','cast',type=P);g.link('Add','ReturnValue','Cast','Object');g.setter('SaveBody','Body','Cast','AsPoseable Mesh Component');g.exec('Add','SaveBody');g.call('Mesh','SetSkinnedAssetAndUpdate',SK,NewMesh='/Game/Traffic/Detailed/SK_PrivateSUV.SK_PrivateSUV',bReinitPose='true');g.link('Body','Body','Mesh','self');g.exec('SaveBody','Mesh');g.call('Read','GetBoneTransformByName',P,BoneName='door_L',BoneSpace='ComponentSpace');g.link('Body','Body','Read','self');g.exec('Mesh','Read');g.setter('Store','RestCar','Read');g.exec('Read','Store');g.exec('Store','result');g.build('ReceiveBeginPlay')
g=d.Graph();g.variables=[{'name':'Age','default':'0'},{'name':'Stage','default':'0'}]
for n in ['Age','Stage','Body','RestCar','RestBus']:g.get(n)
g.call('Time','Add_DoubleDouble',M);g.link('Age','Age','Time','A');g.link('entry','DeltaSeconds','Time','B');g.setter('AgeNow','Age','Time');g.exec('entry','AgeNow');g.call('Player','GetPlayerPawn',G,PlayerIndex='0');g.node('Rider','cast',type=R);g.link('Player','ReturnValue','Rider','Object');g.node('Delivery','getfield',owner=R,var='Delivery');g.link('Rider','AsBogota Player','Delivery','self');g.call('Manager','GetActorOfClass',G,ActorClass=C);g.node('ManagerCast','cast',type=C);g.link('Manager','ReturnValue','ManagerCast','Object');g.call('SelfAt','K2_GetActorLocation',A);g.call('PlayerAt','Add_VectorVector',M,B='(X=0,Y=400,Z=100)');g.link('SelfAt','ReturnValue','PlayerAt','A')
last='AgeNow';lastpin='then'
def phase(id,time,stage):
 global last,lastpin
 g.call(id+'Time','Greater_DoubleDouble',M,B=str(time));g.link('Age','Age',id+'Time','A');g.call(id+'Stage','NearlyEqual_FloatFloat',M,B=str(stage),ErrorTolerance='.01');g.link('Stage','Stage',id+'Stage','A');g.call(id+'Allowed','BooleanAND',M);g.link(id+'Time','ReturnValue',id+'Allowed','A');g.link(id+'Stage','ReturnValue',id+'Allowed','B');g.branch(id,id+'Allowed');g.exec(last,id,lastpin);last=id;lastpin='else';return id

def end(lastnode,stage):
 g.setter('Stage'+str(stage),'Stage',value=str(stage));g.exec(lastnode,'Stage'+str(stage));g.exec('Stage'+str(stage),'result')
def code(id,start):
 last=start
 for i,c in enumerate('PUERTAS'):
  n=id+str(i);g.call(n,'DeveloperKey',D,Key=c);g.link('Delivery','Delivery',n,'self');g.exec(last,n);last=n
 return last

def dev(id,start,value):
 g.node(id,'setfield',owner=D,var='DeveloperMode',defaults={'DeveloperMode':str(value).lower()});g.link('Delivery','Delivery',id,'self');g.exec(start,id);return id

def check(id,start,kind,baseline,bone):
 g.call(id+'Read','GetBoneTransformByName',P,BoneName=bone,BoneSpace='ComponentSpace');g.link('Body','Body',id+'Read','self');g.exec(start,id+'Read');g.call(id+'Parts','BreakTransform',M);g.link(id+'Read','ReturnValue',id+'Parts','InTransform');g.call(id+'Rest','BreakTransform',M);g.link(baseline,baseline,id+'Rest','InTransform');g.call(id+'Delta','Subtract_VectorVector',M);g.link(id+'Parts','Location',id+'Delta','A');g.link(id+'Rest','Location',id+'Delta','B');g.call(id+'Distance','VSize',M);g.link(id+'Delta','ReturnValue',id+'Distance','A');g.call(id+'Rot','NormalizedDeltaRotator',M);g.link(id+'Parts','Rotation',id+'Rot','A');g.link(id+'Rest','Rotation',id+'Rot','B');g.call(id+'Angles','BreakRotator',M);g.link(id+'Rot','ReturnValue',id+'Angles','InRot');g.call(id+'Yaw','Abs',M);g.link(id+'Angles','Yaw',id+'Yaw','A')
 if kind=='caropen':g.call(id+'Pass','Greater_DoubleDouble',M,B='60');g.link(id+'Yaw','ReturnValue',id+'Pass','A')
 elif kind=='busopen':g.call(id+'Pass','Greater_DoubleDouble',M,B='45');g.link(id+'Distance','ReturnValue',id+'Pass','A')
 else:
  g.call(id+'LocPass','Less_DoubleDouble',M,B='.1');g.link(id+'Distance','ReturnValue',id+'LocPass','A');g.call(id+'RotPass','Less_DoubleDouble',M,B='.1');g.link(id+'Yaw','ReturnValue',id+'RotPass','A');g.call(id+'Pass','BooleanAND',M);g.link(id+'LocPass','ReturnValue',id+'Pass','A');g.link(id+'RotPass','ReturnValue',id+'Pass','B')
 g.call(id+'ScaleDelta','Subtract_VectorVector',M);g.link(id+'Parts','Scale',id+'ScaleDelta','A');g.link(id+'Rest','Scale',id+'ScaleDelta','B');g.call(id+'ScaleSize','VSize',M);g.link(id+'ScaleDelta','ReturnValue',id+'ScaleSize','A');g.call(id+'ScaleOK','Less_DoubleDouble',M,B='.001');g.link(id+'ScaleSize','ReturnValue',id+'ScaleOK','A');g.call(id+'AllOK','BooleanAND',M);g.link(id+'ScaleOK','ReturnValue',id+'AllOK','A');g.link(id+'Pass','ReturnValue',id+'AllOK','B');g.call(id+'Text','Conv_BoolToString',STR);g.link(id+'AllOK','ReturnValue',id+'Text','InBool');g.call(id+'Message','Concat_StrStr',STR,A='DEV_DOORS_QA '+id+'=');g.link(id+'Text','ReturnValue',id+'Message','B');g.call(id+'Print','PrintString',S,bPrintToScreen='false',bPrintToLog='true');g.link(id+'Message','ReturnValue',id+'Print','InString');g.exec(id+'Read',id+'Print');return id+'Print'
def absent(id,start):
 g.call(id+'Find','GetActorOfClass',G,ActorClass=C);g.exec(start,id+'Find');g.call(id+'Valid','IsValid',S);g.link(id+'Find','ReturnValue',id+'Valid','Object');g.call(id+'Not','Not_PreBool',M);g.link(id+'Valid','ReturnValue',id+'Not','A');g.call(id+'Text','Conv_BoolToString',STR);g.link(id+'Not','ReturnValue',id+'Text','InBool');g.call(id+'Message','Concat_StrStr',STR,A='DEV_DOORS_QA '+id+'=');g.link(id+'Text','ReturnValue',id+'Message','B');g.call(id+'Print','PrintString',S,bPrintToScreen='false',bPrintToLog='true');g.link(id+'Message','ReturnValue',id+'Print','InString');g.exec(id+'Find',id+'Print');return id+'Print'
p=phase('RequireDeveloper',.5,0);end(code('ForbiddenDoors',p),-1)
p=phase('CheckRequireDeveloper',1,-1);end(absent('REQUIRES_DEVELOPER',p),-2)
p=phase('Setup',2,-2);g.call('MovePlayer','K2_SetActorLocation',A,bSweep='false',bTeleport='true');g.link('Player','ReturnValue','MovePlayer','self');g.link('PlayerAt','ReturnValue','MovePlayer','NewLocation');g.exec(p,'MovePlayer');g.node('Movement','getfield',owner='/Script/Engine.Character',var='CharacterMovement');g.link('Rider','AsBogota Player','Movement','self');g.call('Freeze','DisableMovement','/Script/Engine.CharacterMovementComponent');g.link('Movement','CharacterMovement','Freeze','self');g.exec('MovePlayer','Freeze');end(code('OpenCar',dev('Enable','Freeze',True)),1)
p=phase('CheckCarOpen',3.5,1);end(check('CAR_OPEN',p,'caropen','RestCar','door_L'),2)
p=phase('CloseCar',4,2);end(code('CloseCarKey',p),3)
p=phase('CheckCarClosed',5.5,3);end(check('CAR_CLOSED',p,'closed','RestCar','door_L'),4)
p=phase('Disable',6,4);end(dev('DisableMode',p,False),5)
p=phase('CheckDisabled',6.5,5);g.exec(p,'Manager');g.call('Exists','IsValid',S);g.link('Manager','ReturnValue','Exists','Object');g.call('Absent','Not_PreBool',M);g.link('Exists','ReturnValue','Absent','A');g.call('AbsentText','Conv_BoolToString',STR);g.link('Absent','ReturnValue','AbsentText','InBool');g.call('AbsentMessage','Concat_StrStr',STR,A='DEV_DOORS_QA DISABLE_CLEANS_UP=');g.link('AbsentText','ReturnValue','AbsentMessage','B');g.call('PrintAbsent','PrintString',S,bPrintToScreen='false',bPrintToLog='true');g.link('AbsentMessage','ReturnValue','PrintAbsent','InString');g.exec('Manager','PrintAbsent');end('PrintAbsent',6)
p=phase('SetupBus',7,6);g.call('BusMesh','SetSkinnedAssetAndUpdate',SK,NewMesh='/Game/Traffic/Detailed/SK_TransMilenioG66.SK_TransMilenioG66',bReinitPose='true');g.link('Body','Body','BusMesh','self');g.exec(p,'BusMesh');g.call('ReadBus','GetBoneTransformByName',P,BoneName='bus_door_a',BoneSpace='ComponentSpace');g.link('Body','Body','ReadBus','self');g.exec('BusMesh','ReadBus');g.setter('StoreBus','RestBus','ReadBus');g.exec('ReadBus','StoreBus');end(code('OpenBus',dev('EnableBus','StoreBus',True)),7)
p=phase('CheckBusOpen',8.5,7);end(check('BUS_OPEN',p,'busopen','RestBus','bus_door_a'),8)
p=phase('CloseBus',9,8);end(code('CloseBusKey',p),9)
p=phase('CheckBusClosed',10.5,9);end(check('BUS_CLOSED',p,'closed','RestBus','bus_door_a'),10)
p=phase('ReopenBus',11,10);end(code('ReopenBusKey',p),11)
p=phase('MoveBus',12,11);g.call('NextAt','Add_VectorVector',M,B='(X=20,Y=0,Z=0)');g.link('SelfAt','ReturnValue','NextAt','A');g.call('MoveSelf','K2_SetActorLocation',A,bSweep='false',bTeleport='true');g.link('NextAt','ReturnValue','MoveSelf','NewLocation');g.exec(p,'MoveSelf');end('MoveSelf',12)
p=phase('CheckSafety',13,12);end(absent('MOVEMENT_RELEASES_CONTROL',check('MOVEMENT_CLOSES',p,'closed','RestBus','bus_door_a')),13)
p=phase('NoNearby',14,13);g.call('ClearMesh','SetSkinnedAssetAndUpdate',SK,bReinitPose='true');g.link('Body','Body','ClearMesh','self');g.exec(p,'ClearMesh');end(code('NoNearbyKey','ClearMesh'),14)
p=phase('CheckNoNearby',15,14);end(absent('NO_VEHICLE_NO_CONTROLLER',p),15)
p=phase('Done',16,15);g.call('Quit','ExecuteConsoleCommand',S,Command='quit');g.exec(p,'Quit');g.exec('Quit','result');g.exec(last,'result',lastpin);g.build('ReceiveTick');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
world=unreal.EditorLoadingAndSavingUtils.new_blank_map(False);assert world;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.WorldSettings):a.set_editor_property('default_game_mode',unreal.load_asset('/Game/Delivery/Core/BP_DeliveryGameMode').generated_class())
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(-6500,14000,5000));actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-6500,14400,5100));assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/DeveloperDoorsRuntimeTest');unreal.log('DEVELOPER_DOORS_RUNTIME_SETUP_PASS')
