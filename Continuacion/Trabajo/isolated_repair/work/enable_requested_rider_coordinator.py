import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRiderAnimationCoordinator');d.bp=bp;c=unreal.get_default_object(bp.generated_class());tick=c.get_editor_property('primary_actor_tick');report={}
for n in ['can_ever_tick','start_with_tick_enabled','tick_interval','tick_group']:
 try:report[n]=str(tick.get_editor_property(n))
 except Exception as ex:report[n]=str(ex)
for n,v in [('can_ever_tick',True),('start_with_tick_enabled',True),('tick_interval',0)]:tick.set_editor_property(n,v)
c.set_editor_property('primary_actor_tick',tick);g=d.Graph();g.call('Enabled','SetActorTickEnabled','/Script/Engine.Actor',bEnabled='true');g.exec('entry','Enabled');g.exec('Enabled','result');g.build('ReceiveBeginPlay');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_class()==bp.generated_class():
  t=a.get_editor_property('primary_actor_tick');t.set_editor_property('can_ever_tick',True);t.set_editor_property('start_with_tick_enabled',True);t.set_editor_property('tick_interval',0);a.set_editor_property('primary_actor_tick',t)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/Maps/Bogota_Blueprint_Integration');(r/'work/rider_coordinator_tick_inspection.json').write_text(json.dumps(report,indent=2));unreal.log('RIDER_COORDINATOR_TICK '+json.dumps(report))
exec(compile((r/'work/build_requested_fixes_qa.py').read_text(encoding='utf-8-sig'),'RequestedQA','exec'),{})
