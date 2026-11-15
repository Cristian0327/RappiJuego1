import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;s=(r/'work/build_npc_facing_coordinator.py').read_text(encoding='utf-8-sig');prefix=s[:s.index("E.compile_blueprint(bp);d.bp=bp;")];exec(compile(prefix,'FacingSetup','exec'))
if 'Actors' not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,'Actors',E.get_array_type(E.get_object_reference_type(unreal.Actor)))
assert E.compile_blueprint(bp);d.bp=bp;g=d.Graph();g.get('Actors');g.call('Clear','Array_Clear','/Script/Engine.KismetArrayLibrary');g.link('Actors','Actors','Clear','TargetArray');g.exec('entry','Clear');last='Clear'
for tag,typ in [('Road','/Game/Traffic/Services/BP_VoxelRoadVehicle.BP_VoxelRoadVehicle_C'),('Owner','/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C')]:
 g.call(tag,'GetAllActorsOfClass',G,ActorClass=typ)
 if tag=='Road':g.exec(last,tag)
 else:g.link(last,'Completed',tag,'execute')
 g.node(tag+'Each','foreach');g.link(tag,'OutActors',tag+'Each','Array');g.link(tag,'then',tag+'Each','Exec');g.call(tag+'Add','Array_Add','/Script/Engine.KismetArrayLibrary');g.link('Actors','Actors',tag+'Add','TargetArray');g.link(tag+'Each','Array Element',tag+'Add','NewItem');g.link(tag+'Each','LoopBody',tag+'Add','execute');last=tag+'Each'
g.link('OwnerEach','Completed','result','execute');g.build('ReceiveBeginPlay')
start=s.index('def op');end=s.index("w=unreal.EditorLoadingAndSavingUtils.load_map",start);body='g=d.Graph()\n'+s[start:end];a=body.index("g.call('ValidCache','IsValid',S)");b=body.index("g.call('ActorValid'",a);body=body[:a]+"g.get('Actors');g.node('Each','foreach');g.link('Actors','Actors','Each','Array');g.link('entry','then','Each','Exec');"+body[b:];body=body.replace("g.exec('ValidActor','Legacy')","g.node('ActorHidden','getfield',owner=A,var='bHidden');g.link('Each','Array Element','ActorHidden','self');g.call('ActorVisible','Not_PreBool',M);g.link('ActorHidden','bHidden','ActorVisible','A');g.branch('DrawnActor','ActorVisible');g.exec('ValidActor','DrawnActor');g.exec('DrawnActor','Legacy')");exec(compile(body,'LiveFacingTick','exec'))
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for path in ['/Game/Maps/Bogota_Blueprint_Integration','/Game/QA/PureIntegratedWorld']:
 assert unreal.EditorLoadingAndSavingUtils.load_map(path)
 for a in actors.get_all_level_actors():
  if a.get_class().get_path_name()==bp.generated_class().get_path_name():actors.destroy_actor(a)
 actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('City_MountedFacingCorrection');w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,path)
unreal.log('LIVE_MOTO_FACING_CONNECTED')
