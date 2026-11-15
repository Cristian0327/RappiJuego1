import unreal,sys,json,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
orig_build=d.Graph.build
def diagnostic_build(self,name):
 try:return orig_build(self,name)
 except:
  (root/'work/failed_police_graph.json').write_text(unreal.DeliveryEditorLibrary.audit_blueprint(d.bp));raise
d.Graph.build=diagnostic_build
E=unreal.BlueprintEditorLibrary;M=d.M;A='/Script/Engine.Actor';SYS='/Script/Engine.KismetSystemLibrary';GAME='/Script/Engine.GameplayStatics';STR='/Script/Engine.KismetStringLibrary';folder='/Game/Traffic/Services';tools=unreal.AssetToolsHelpers.get_asset_tools();actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
police=unreal.load_asset(folder+'/BP_PoliceOfficer');assert police
cdo=unreal.get_default_object(police.generated_class());mesh=cdo.get_editor_property('mesh');assert mesh.get_skinned_asset() and mesh.get_skinned_asset().get_path_name().startswith(folder), 'Police mesh defaults did not persist'
# A parked patrol is an engine actor with collision construction in Blueprint.
path=folder+'/BP_PolicePatrol'
if unreal.EditorAssetLibrary.does_asset_exist(path):patrol=unreal.load_asset(path)
else:
 f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.SkeletalMeshActor);patrol=tools.create_asset('BP_PolicePatrol',folder,unreal.Blueprint,f)
pdo=unreal.get_default_object(patrol.generated_class());m=pdo.get_editor_property('skeletal_mesh_component');m.set_skeletal_mesh_asset(unreal.load_asset(folder+'/SK_PolicePatrol'));m.set_material(0,unreal.load_asset(folder+'/M_ServiceVoxel'));m.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);d.bp=patrol;g=d.Graph();g.call('At','MakeTransform',M,Location='(X=0,Y=0,Z=106)',Scale='(X=1,Y=1,Z=1)');g.call('Box','AddComponentByClass',A,Class='/Script/Engine.BoxComponent',bManualAttachment='false',bDeferredFinish='false');g.link('At','ReturnValue','Box','RelativeTransform');g.exec('entry','Box');g.node('AsBox','cast',type='/Script/Engine.BoxComponent');g.link('Box','ReturnValue','AsBox','Object');g.call('Extent','SetBoxExtent','/Script/Engine.BoxComponent',InBoxExtent='(X=232,Y=120,Z=106)',bUpdateOverlaps='true');g.link('AsBox','AsBox Collision','Extent','self');g.exec('Box','Extent');g.call('Profile','SetCollisionProfileName','/Script/Engine.PrimitiveComponent',InCollisionProfileName='BlockAll',bUpdateOverlaps='true');g.link('AsBox','AsBox Collision','Profile','self');g.exec('Extent','Profile');g.exec('Profile','result');g.build('ReceiveBeginPlay');assert E.compile_blueprint(patrol);unreal.EditorAssetLibrary.save_loaded_asset(patrol,only_if_is_dirty=False)
# Preserve the current map before placing the two functional Blueprint actors.
p=root/'RappiJuego1/Content/Maps/Bogota.umap';b=root/'Recuperacion_Migracion_Blueprints/2026-10-16_modelos/Bogota.umap';b.parent.mkdir(parents=True,exist_ok=True)
if not b.exists():shutil.copy2(p,b)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
for actor in actors.get_all_level_actors():
 if str(actor.get_actor_label()) in ['Policia_Voxel_BP','Patrulla_Voxel_BP']:actors.destroy_actor(actor)
officer=actors.spawn_actor_from_class(police.generated_class(),unreal.Vector(-8000,14000,155),unreal.Rotator(pitch=0,yaw=90,roll=0));officer.set_actor_label('Policia_Voxel_BP');car=actors.spawn_actor_from_class(patrol.generated_class(),unreal.Vector(-7000,14500,55),unreal.Rotator(0,0,0));car.set_actor_label('Patrulla_Voxel_BP');unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
# A reusable test map and a pure Blueprint harness validate actual movement.
unreal.EditorAssetLibrary.make_directory('/Game/QA');hpath='/Game/QA/BP_ValidatePolicePatrol'
if unreal.EditorAssetLibrary.does_asset_exist(hpath):h=unreal.load_asset(hpath)
else:
 f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);h=tools.create_asset('BP_ValidatePolicePatrol','/Game/QA',unreal.Blueprint,f)
d.bp=h;g=d.Graph();g.call('Player','GetPlayerPawn',GAME,PlayerIndex='0');g.call('BlockRoute','K2_SetActorLocation',A,NewLocation='(X=-8000,Y=14600,Z=155)',bSweep='false',bTeleport='true');g.link('Player','ReturnValue','BlockRoute','self');g.exec('entry','BlockRoute');g.exec('BlockRoute','result');g.build('ReceiveBeginPlay');g=d.Graph();g.variables=[{'name':'PlayerClearance','default':'50000'},{'name':'Elapsed','default':'0'},{'name':'Travel','default':'0'},{'name':'MaximumTurn','default':'0'},{'name':'Captured','type':'bool','default':'false'}]
for v in ['Elapsed','Travel','MaximumTurn','Captured','PlayerClearance']:g.get(v)
g.call('Find','GetActorOfClass',GAME,ActorClass=folder+'/BP_PoliceOfficer.BP_PoliceOfficer_C');g.exec('entry','Find');g.call('IsValid','IsValid',SYS);g.link('Find','ReturnValue','IsValid','Object');g.branch('Valid','IsValid');g.exec('Find','Valid');g.exec('Valid','result','else')
g.call('At','K2_GetActorLocation',A);g.link('Find','ReturnValue','At','self');g.call('Velocity','GetVelocity',A);g.link('Find','ReturnValue','Velocity','self');g.call('Speed','VSizeXY',M);g.link('Velocity','ReturnValue','Speed','A');g.call('Distance','Multiply_DoubleDouble',M);g.link('Speed','ReturnValue','Distance','A');g.link('entry','DeltaSeconds','Distance','B');g.call('Sum','Add_DoubleDouble',M);g.link('Travel','Travel','Sum','A');g.link('Distance','ReturnValue','Sum','B');g.setter('AddTravel','Travel','Sum');g.exec('Valid','AddTravel');g.call('Time','Add_DoubleDouble',M);g.link('Elapsed','Elapsed','Time','A');g.link('entry','DeltaSeconds','Time','B');g.setter('AddTime','Elapsed','Time');g.exec('AddTravel','AddTime');g.call('Rotation','K2_GetActorRotation',A);g.link('Find','ReturnValue','Rotation','self');g.call('DeltaYaw','NormalizedDeltaRotator',M,B='(Pitch=0,Yaw=90,Roll=0)');g.link('Rotation','ReturnValue','DeltaYaw','A');g.call('Yaw','BreakRotator',M);g.link('DeltaYaw','ReturnValue','Yaw','InRot');g.call('Abs','Abs',M);g.link('Yaw','Yaw','Abs','A');g.call('Max','FMax',M);g.link('MaximumTurn','MaximumTurn','Max','A');g.link('Abs','ReturnValue','Max','B');g.setter('SaveTurn','MaximumTurn','Max');g.exec('AddTime','SaveTurn')
g.call('Camera','GetActorOfClass',GAME,ActorClass='/Script/Engine.CameraActor');g.call('Player','GetPlayerPawn',GAME,PlayerIndex='0');g.call('PlayerAt','K2_GetActorLocation',A);g.link('Player','ReturnValue','PlayerAt','self');g.call('ToPlayer','Subtract_VectorVector',M);g.link('At','ReturnValue','ToPlayer','A');g.link('PlayerAt','ReturnValue','ToPlayer','B');g.call('PlayerDistance','VSizeXY',M);g.link('ToPlayer','ReturnValue','PlayerDistance','A');g.call('Closest','FMin',M);g.link('PlayerClearance','PlayerClearance','Closest','A');g.link('PlayerDistance','ReturnValue','Closest','B');g.setter('SaveClearance','PlayerClearance','Closest');g.exec('SaveTurn','SaveClearance');g.exec('SaveClearance','Camera');g.call('CameraOffset','Add_VectorVector',M,B='(X=-650,Y=-850,Z=340)');g.link('At','ReturnValue','CameraOffset','A');g.call('CameraAt','K2_SetActorLocation',A,bSweep='false',bTeleport='true');g.link('Camera','ReturnValue','CameraAt','self');g.link('CameraOffset','ReturnValue','CameraAt','NewLocation');g.exec('Camera','CameraAt');g.call('LookAt','FindLookAtRotation',M);g.link('CameraOffset','ReturnValue','LookAt','Start');g.link('At','ReturnValue','LookAt','Target');g.call('AimCamera','K2_SetActorRotation',A,bTeleportPhysics='true');g.link('Camera','ReturnValue','AimCamera','self');g.link('LookAt','ReturnValue','AimCamera','NewRotation');g.exec('CameraAt','AimCamera');g.call('PC','GetPlayerController',GAME,PlayerIndex='0');g.call('View','SetViewTargetWithBlend','/Script/Engine.PlayerController',BlendTime='0');g.link('PC','ReturnValue','View','self');g.link('Camera','ReturnValue','View','NewViewTarget');g.exec('AimCamera','View')
g.call('After5','Greater_DoubleDouble',M,B='5');g.link('Elapsed','Elapsed','After5','A');g.call('NotCaptured','Not_PreBool',M);g.link('Captured','Captured','NotCaptured','A');g.call('TakeShot','BooleanAND',M);g.link('After5','ReturnValue','TakeShot','A');g.link('NotCaptured','ReturnValue','TakeShot','B');g.branch('Shot','TakeShot');g.exec('View','Shot');g.call('Capture','ExecuteConsoleCommand',SYS,Command='HighResShot 1');g.exec('Shot','Capture');g.setter('MarkCaptured','Captured',value='true');g.exec('Capture','MarkCaptured');g.call('Finished','Greater_DoubleDouble',M,B='65');g.link('Elapsed','Elapsed','Finished','A');g.branch('Done','Finished');g.exec('Shot','Done','else');g.exec('MarkCaptured','Done');g.exec('Done','result','else')
g.call('XYZ','BreakVector',M);g.link('At','ReturnValue','XYZ','InVec')
previous=None
for i,(label,node,pin) in enumerate([('POLICE_BLUEPRINT_QA travel_cm=','Travel','Travel'),(' turn_degrees=','MaximumTurn','MaximumTurn'),(' z_cm=','XYZ','Z'),(' player_clearance_cm=','PlayerClearance','PlayerClearance')]):
 g.call('Text'+str(i),'Conv_DoubleToString',STR);g.link(node,pin,'Text'+str(i),'InDouble');g.call('Field'+str(i),'Concat_StrStr',STR,A=label);g.link('Text'+str(i),'ReturnValue','Field'+str(i),'B')
 if previous:g.call('Join'+str(i),'Concat_StrStr',STR);g.link(previous,'ReturnValue','Join'+str(i),'A');g.link('Field'+str(i),'ReturnValue','Join'+str(i),'B');previous='Join'+str(i)
 else:previous='Field'+str(i)
g.call('Print','PrintString',SYS,bPrintToScreen='false',bPrintToLog='true');g.link(previous,'ReturnValue','Print','InString');g.exec('Done','Print');g.call('Quit','ExecuteConsoleCommand',SYS,Command='quit');g.exec('Print','Quit');g.exec('Quit','result');g.build('ReceiveTick');assert E.compile_blueprint(h);unreal.EditorAssetLibrary.save_loaded_asset(h,only_if_is_dirty=False)
if not unreal.EditorAssetLibrary.does_asset_exist('/Game/QA/PolicePatrolTest'):assert unreal.EditorAssetLibrary.duplicate_asset('/Game/Maps/Bogota','/Game/QA/PolicePatrolTest')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PolicePatrolTest')
for actor in actors.get_all_level_actors():
 if actor.get_class() in [h.generated_class(),police.generated_class(),patrol.generated_class()]:actors.destroy_actor(actor)
actors.spawn_actor_from_class(police.generated_class(),unreal.Vector(-8000,14000,155),unreal.Rotator(pitch=0,yaw=90,roll=0));actors.spawn_actor_from_class(patrol.generated_class(),unreal.Vector(-7000,14500,55));actors.spawn_actor_from_class(h.generated_class(),unreal.Vector(0,0,0));actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(-8600,13150,480));unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(root/'work/police_integration_setup.json').write_text(json.dumps({'status':'READY_FOR_RUNTIME_TEST','officer':folder+'/BP_PoliceOfficer','patrol':folder+'/BP_PolicePatrol','test_map':'/Game/QA/PolicePatrolTest'},indent=2));unreal.log('POLICE_BLUEPRINT_INTEGRATION_SETUP_PASS')





