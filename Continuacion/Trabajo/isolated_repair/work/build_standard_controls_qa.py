import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;s=(r/'work/build_pure_rider_mount_runtime.py').read_text(encoding='utf-8-sig');prefix=s[:s.index('FIX=')].replace('BP_TestPureRiderMount','BP_TestStandardControls').replace('PURE_RIDER_MOUNT ','STANDARD_CONTROL ');exec(compile(prefix,'StandardControlsFixture','exec'));a=s.index('g.variables +=');b=s.index('def ridercall',a);exec(compile(s[a:b],'OrderedStandardInputs','exec'))
A='/Script/Engine.Actor';SC='/Script/Engine.SceneComponent';SK='/Script/Engine.SkeletalMeshComponent';RUN='/Game/Delivery/Animation/ABP_DeliveryRiderRun.ABP_DeliveryRiderRun_C';g.variables += [{'name':'StandingYaw','default':'0'}];g.get('StandingYaw')
def callhero(tag,fn,start,**kw):
 g.call(tag,fn,R,**kw);g.link('Rider','AsBP Blueprint Rider',tag,'self');g.exec(start,tag);return tag
def inputs(tag,start,forward,side):
 g.setter(tag+'F','ForcedForward',value=str(forward));g.exec(start,tag+'F');g.setter(tag+'S','ForcedSide',value=str(side));g.exec(tag+'F',tag+'S');return tag+'S'
def view(tag,start,yaw,pitch=-12):
 g.call(tag+'Rot','MakeRotator',M,Yaw=str(yaw),Pitch=str(pitch));g.call(tag,'SetControlRotation','/Script/Engine.Controller');g.link('Controller','ReturnValue',tag,'self');g.link(tag+'Rot','ReturnValue',tag,'NewRotation');g.exec(start,tag);return tag
# Pure velocity measurements re-evaluate at every phase.
g.call('Velocity','GetVelocity',A);g.link('Pawn','ReturnValue','Velocity','self');g.call('Speed','VSizeXY',M);g.link('Velocity','ReturnValue','Speed','A');g.call('UnitVelocity','Normal2D',M);g.link('Velocity','ReturnValue','UnitVelocity','A');g.call('VelocityAxes','BreakVector',M);g.link('UnitVelocity','ReturnValue','VelocityAxes','InVec');g.call('Forward','GetActorForwardVector',A);g.link('Pawn','ReturnValue','Forward','self');g.call('FacingDot','Dot_VectorVector',M);g.link('Forward','ReturnValue','FacingDot','A');g.link('UnitVelocity','ReturnValue','FacingDot','B')
def direction_check(tag,time,axis,positive):
 p0=phase(tag,time);g.call(tag+'Good','Greater_DoubleDouble' if positive else 'Less_DoubleDouble',M,B='.95' if positive else '-.95');g.link('VelocityAxes',axis,tag+'Good','A');report(tag,p0,tag+'Good')
p0=phase('OpenSpace',1);g.call('Teleport','K2_SetActorLocationAndRotation',A,NewLocation='(X=80000,Y=78000,Z=95)',bSweep='false',bTeleport='true');g.link('Pawn','ReturnValue','Teleport','self');g.exec(p0,'Teleport');advance('Teleport')
p0=phase('StartW',1.2);end=view('InitialView',p0,0);advance(inputs('W',end,1,0))
direction_check('W_FOLLOWS_CAMERA_ZERO',2,'X',True)
p0=phase('BodyFacesMotion',2.05);g.call('FacingGood','Greater_DoubleDouble',M,B='.98');g.link('FacingDot','ReturnValue','FacingGood','A');report('BODY_FACES_MOVEMENT',p0,'FacingGood')
p0=phase('RotateWhileHoldingW',2.1);advance(view('NinetyView',p0,90))
direction_check('HELD_W_FOLLOWS_NEW_CAMERA_YAW',2.65,'Y',True)
p0=phase('ReleaseKeys',2.7);advance(inputs('Stop',p0,0,0))
p0=phase('StandingOrbit',3.2);g.call('ActorRotation','K2_GetActorRotation',A);g.link('Pawn','ReturnValue','ActorRotation','self');g.call('ActorAngles','BreakRotator',M);g.link('ActorRotation','ReturnValue','ActorAngles','InRot');g.setter('RememberStanding','StandingYaw','ActorAngles','Yaw');g.exec(p0,'RememberStanding');advance(view('StandingView','RememberStanding',180))
p0=phase('StandingStable',3.6);g.call('StandingDelta','Subtract_DoubleDouble',M);g.link('ActorAngles','Yaw','StandingDelta','A');g.link('StandingYaw','StandingYaw','StandingDelta','B');g.call('StandingWrap','NormalizeAxis',M);g.link('StandingDelta','ReturnValue','StandingWrap','Angle');g.call('StandingAbs','Abs',M);g.link('StandingWrap','ReturnValue','StandingAbs','A');g.call('NoBodyTurn','Less_DoubleDouble',M,B='1');g.link('StandingAbs','ReturnValue','NoBodyTurn','A');report('LOOK_ALONE_DOES_NOT_TURN_BODY',p0,'NoBodyTurn')
p0=phase('StartSHighPitch',3.7);end=view('HighPitchView',p0,90,70);advance(inputs('S',end,-1,0))
direction_check('S_BACKWARD_IGNORES_CAMERA_PITCH',4.3,'Y',False)
p0=phase('StartA',4.4);end=view('LevelView',p0,90);advance(inputs('A',end,0,-1))
direction_check('A_IS_CAMERA_LEFT',5,'X',True)
p0=phase('StartD',5.1);advance(inputs('D',p0,0,1))
direction_check('D_IS_CAMERA_RIGHT',5.7,'X',False)
p0=phase('StartDiagonal',5.8);advance(inputs('Diagonal',p0,1,1))
p0=phase('DiagonalSpeed',6.5);g.call('Speed140','NearlyEqual_FloatFloat',M,B='140',ErrorTolerance='3');g.link('Speed','ReturnValue','Speed140','A');report('DIAGONAL_HAS_SAME_WALK_SPEED',p0,'Speed140')
p0=phase('SprintStart',6.6);end=inputs('Run',p0,1,0);advance(callhero('ShiftDown','StartSprint',end))
p0=phase('SprintWorks',7.8);g.call('Fast','Greater_DoubleDouble',M,B='620');g.link('Speed','ReturnValue','Fast','A');g.call('Animation','GetAnimInstance',SK);g.link('Mesh','Mesh','Animation','self');g.node('RunClass','cast',type=RUN);g.link('Animation','ReturnValue','RunClass','Object');g.call('RunValid','IsValid',K);g.link('RunClass','AsABP Delivery Rider Run','RunValid','Object');g.call('RunGood','BooleanAND',M);g.link('Fast','ReturnValue','RunGood','A');g.link('RunValid','ReturnValue','RunGood','B');report('SPRINT_650_MIXAMO_PRESERVED',p0,'RunGood')
p0=phase('StopSprint',7.9);end=inputs('StopRun',p0,0,0);advance(callhero('ShiftUp','EndSprint',end))
p0=phase('ReturnToBike',8.5);g.call('BikeAt','K2_GetActorLocation',A);g.link('Parked','ParkedVehicle','BikeAt','self');g.call('NearBike','Add_VectorVector',M,B='(X=0,Y=-100,Z=90)');g.link('BikeAt','ReturnValue','NearBike','A');g.call('BikeRotation','K2_GetActorRotation',A);g.link('Parked','ParkedVehicle','BikeRotation','self');g.call('PlaceNearBike','K2_SetActorLocationAndRotation',A,bSweep='false',bTeleport='true');g.link('Pawn','ReturnValue','PlaceNearBike','self');g.link('NearBike','ReturnValue','PlaceNearBike','NewLocation');g.link('BikeRotation','ReturnValue','PlaceNearBike','NewRotation');g.exec(p0,'PlaceNearBike');advance('PlaceNearBike')
p0=phase('MountBike',8.8);advance(callhero('PressF','MountPressed',p0))
p0=phase('MountReady',9.7);g.call('NotTransition','EqualEqual_IntInt',M,B='0');g.link('Transition','TransitionState','NotTransition','A');g.call('StableMounted','BooleanAND',M);g.link('Mounted','Riding','StableMounted','A');g.link('NotTransition','ReturnValue','StableMounted','B');report('MOUNTING_PRESERVED',p0,'StableMounted')
p0=phase('VehicleOrbit',9.8);g.call('OrbitYaw','Add_DoubleDouble',M,B='80');g.link('ActorAngles','Yaw','OrbitYaw','A');g.call('VehicleOrbitRotation','MakeRotator',M,Pitch='-12');g.link('OrbitYaw','ReturnValue','VehicleOrbitRotation','Yaw');g.call('SetVehicleView','SetControlRotation','/Script/Engine.Controller');g.link('Controller','ReturnValue','SetVehicleView','self');g.link('VehicleOrbitRotation','ReturnValue','SetVehicleView','NewRotation');g.exec(p0,'SetVehicleView');end=inputs('VehicleGas','SetVehicleView',1,0);advance(callhero('MouseActivity','Turn',end,V='.02'))
g.call('ControlView','GetControlRotation','/Script/Engine.Controller');g.link('Controller','ReturnValue','ControlView','self');g.call('ViewError','NormalizedDeltaRotator',M);g.link('ControlView','ReturnValue','ViewError','A');g.link('ActorRotation','ReturnValue','ViewError','B');g.call('ViewErrorAngles','BreakRotator',M);g.link('ViewError','ReturnValue','ViewErrorAngles','InRot');g.call('YawError','Abs',M);g.link('ViewErrorAngles','Yaw','YawError','A')
p0=phase('MouseNoSteering',10.3);g.call('SteerAngle','SteeringAngle',R,Dt='.1');g.link('Rider','AsBP Blueprint Rider','SteerAngle','self');g.call('ZeroSteer','NearlyEqual_FloatFloat',M,B='0',ErrorTolerance='.001');g.link('SteerAngle','ReturnValue','ZeroSteer','A');report('VEHICLE_MOUSE_LOOK_DOES_NOT_STEER',p0,'ZeroSteer')
p0=phase('FreeLookHeld',10.4);g.call('OrbitStillFree','Greater_DoubleDouble',M,B='60');g.link('YawError','ReturnValue','OrbitStillFree','A');report('VEHICLE_FREE_LOOK_HAS_DELAY',p0,'OrbitStillFree')
p0=phase('KeyboardTurn',10.5);advance(inputs('RightTurn',p0,1,1))
p0=phase('KeyboardSteer',11.2);g.call('PositiveSteer','Greater_DoubleDouble',M,B='.1');g.link('SteerAngle','ReturnValue','PositiveSteer','A');report('KEYBOARD_STEERS_VEHICLE',p0,'PositiveSteer')
p0=phase('StopSteering',11.3);advance(inputs('Straight',p0,1,0))
p0=phase('VehicleFollow',13.5);g.call('CameraBehind','Less_DoubleDouble',M,B='6');g.link('YawError','ReturnValue','CameraBehind','A');report('VEHICLE_CAMERA_SOFT_RECENTERS',p0,'CameraBehind')
p0=phase('Finish',13.8);g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true');g.exec(p0,'Quit');g.exec('Quit','result');g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(80000,80000,-50));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(200,200,1));world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/StandardControls');unreal.log('STANDARD_CONTROLS_QA_READY')
