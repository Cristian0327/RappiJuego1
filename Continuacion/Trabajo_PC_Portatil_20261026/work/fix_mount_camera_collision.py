import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;A='/Script/Engine.Actor';P='/Script/Engine.PrimitiveComponent';bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/Vehicles/BP_DeliveryTwoWheeler');d.bp=bp
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_mount_camera';backup.mkdir(exist_ok=True,parents=True);src=r/'RappiJuego1/Content/Delivery/BlueprintGameplay/Vehicles/BP_DeliveryTwoWheeler.uasset'
if not (backup/src.name).exists():shutil.copy2(src,backup/src.name)
g=d.Graph();g.get('ParkedTrafficBody');g.call('Hide','SetActorHiddenInGame',A);g.link('entry','Ridden','Hide','bNewHidden');g.exec('entry','Hide');g.branch('Riding','entry','Ridden');g.exec('Hide','Riding')
for tag,edge,mode in [('DisableBox','then','NoCollision'),('EnableBox','else','QueryOnly')]:
 g.call(tag,'SetCollisionEnabled',P,NewType=mode);g.link('ParkedTrafficBody','ParkedTrafficBody',tag,'self');g.exec('Riding',tag,edge);g.exec(tag,'CameraIgnore')
g.call('CameraIgnore','SetCollisionResponseToChannel',P,Channel='ECC_Camera',NewResponse='ECR_Ignore');g.link('ParkedTrafficBody','ParkedTrafficBody','CameraIgnore','self');g.exec('CameraIgnore','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'SetRidden',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'Ridden','category':'bool'}]}))
g=d.Graph();g.call('Parked','SetRidden',bp.generated_class().get_path_name(),Ridden='false');g.exec('entry','Parked');g.exec('Parked','result');g.build('ReceiveBeginPlay');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
# Verify the channel set by the actual function, without disabling traffic sensing.
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(bp.generated_class(),unreal.Vector(80000,80000,0));a.call_method('SetRidden',(False,));box=a.get_editor_property('ParkedTrafficBody');unreal.log('PARKED_CAMERA_RESPONSE '+str(box.get_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA)));assert box.get_collision_enabled()==unreal.CollisionEnabled.QUERY_ONLY
unreal.log('MOUNT_CAMERA_COLLISION_PATCH_PASS')
