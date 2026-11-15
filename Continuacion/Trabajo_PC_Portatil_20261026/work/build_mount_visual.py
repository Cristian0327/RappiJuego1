import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;G='/Script/Engine.GameplayStatics';K='/Script/Engine.KismetSystemLibrary';M=d.M;R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C'
T=unreal.AssetToolsHelpers.get_asset_tools();f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset('/Game/QA/BP_MountVisual') or T.create_asset('BP_MountVisual','/Game/QA',unreal.Blueprint,f);d.bp=bp
g=d.Graph();g.variables=[{'name':'Age','default':'0'},{'name':'Stage','default':'0'}];g.get('Age');g.get('Stage');g.call('Clock','Add_DoubleDouble',M);g.link('Age','Age','Clock','A');g.link('entry','DeltaSeconds','Clock','B');g.setter('Now','Age','Clock');g.exec('entry','Now');g.call('Player','GetPlayerPawn',G,PlayerIndex='0');g.node('Hero','cast',type=R);g.link('Player','ReturnValue','Hero','Object');last='Now';edge='then'
steps=[(3,'mount'),(3.10,'entry1'),(3.35,'entry2'),(3.60,'entry3'),(5,'mount'),(5.10,'exit1'),(5.35,'exit2'),(5.65,'exit3'),(6.1,'exitdone'),(8,'quit')]
for i,(t,action) in enumerate(steps):
 tag='S'+str(i);g.call(tag+'Due','Greater_DoubleDouble',M,B=str(t));g.link('Age','Age',tag+'Due','A');g.call(tag+'Stage','NearlyEqual_FloatFloat',M,B=str(i),ErrorTolerance='.01');g.link('Stage','Stage',tag+'Stage','A');g.call(tag+'Ready','BooleanAND',M);g.link(tag+'Due','ReturnValue',tag+'Ready','A');g.link(tag+'Stage','ReturnValue',tag+'Ready','B');g.branch(tag,tag+'Ready');g.exec(last,tag,edge)
 if action=='mount':
  g.call(tag+'Act','MountPressed',R);g.link('Hero','AsBP Blueprint Rider',tag+'Act','self')
 else:
  command='quit' if action=='quit' else 'HighResShot 1280x720 filename="'+str(r/'work'/('mount_visual_'+action+'.png')).replace('\\','/')+'"'
  g.call(tag+'Act','ExecuteConsoleCommand',K,Command=command)
 g.exec(tag,tag+'Act');g.setter(tag+'Next','Stage',value=str(i+1));g.exec(tag+'Act',tag+'Next');g.exec(tag+'Next','result');last=tag;edge='else'
g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/MountVisualCity');unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/MountVisualCity');unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('MOUNT_VISUAL_READY')
