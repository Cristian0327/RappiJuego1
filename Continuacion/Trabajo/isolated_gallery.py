import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C'
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset('/Game/QA/BP_GalleryOnly') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_GalleryOnly','/Game/QA',unreal.Blueprint,f);d.bp=bp
g=d.Graph();g.variables=[{'name':'Age','default':'0'},{'name':'Stage','default':'0'}];g.get('Age');g.get('Stage');g.call('Elapsed','Add_DoubleDouble',M);g.link('Age','Age','Elapsed','A');g.link('entry','DeltaSeconds','Elapsed','B');g.setter('Now','Age','Elapsed');g.exec('entry','Now');last='Now';edge='then';stage=0
s=(r/'work/build_pure_rider_mount_runtime.py').read_text(encoding='utf-8-sig');exec(s[s.index('def phase('):s.index('def callcore(')])
p0=phase('Open',2);g.call('Cars','GetAllActorsOfClass',G,ActorClass=V);g.exec(p0,'Cars');g.node('Loop','foreach');g.link('Cars','OutActors','Loop','Array');g.link('Cars','then','Loop','Exec');g.node('Car','cast',type=V);g.link('Loop','Array Element','Car','Object');g.call('OpenDoors','RequestDoors',V,Left='1',Right='1');g.link('Car','AsBP Traffic Vehicle','OpenDoors','self');g.exec('Loop','OpenDoors','LoopBody');g.call('Pose','UpdateDoorPose',V,Dt='1');g.link('Car','AsBP Traffic Vehicle','Pose','self');g.exec('OpenDoors','Pose');g.setter('Opened','Stage',value=str(stage));g.link('Loop','Completed','Opened','execute');g.exec('Opened','result')
p0=phase('Shot',5);g.call('ShotCmd','ExecuteConsoleCommand',K,Command='HighResShot 1 filename=C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/work/SolidVehicleVisualQA/ISOLATED.png');g.exec(p0,'ShotCmd');advance('ShotCmd')
p0=phase('Exit',7);g.call('Quit','ExecuteConsoleCommand',K,Command='quit');g.exec(p0,'Quit');g.exec('Quit','result');g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).new_level('/Game/QA/SolidVehiclesGallery');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_solid_world_qa.py').read_text();part=s[s.index("rows=json.loads"):s.index('probe=actors.spawn_actor_from_class')];exec(part)
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(87300,82500,0)),False);camera.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.PLAYER0)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('ISOLATED_GALLERY_READY')


