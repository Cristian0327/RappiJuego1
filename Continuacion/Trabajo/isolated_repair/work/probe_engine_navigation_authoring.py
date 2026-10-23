import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;assert unreal.EditorLoadingAndSavingUtils.new_blank_map(False);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);volume=actors.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,150));initial=volume.get_actor_bounds(False);builder=volume.get_editor_property('brush_builder');report={'initial_bounds':str(initial),'initial_builder':str(builder),'nav_system_api':[n for n in dir(unreal.NavigationSystemV1) if any(x in n for x in ['build','nav','project','path'])],'ai_controller':str(unreal.load_class(None,'/Script/AIModule.DetourCrowdAIController'))}
if builder:
 report['builder_api']=[n for n in dir(builder) if 'build' in n]
 for name,value in [('x',90000.),('y',60000.),('z',500.)]:
  try:builder.set_editor_property(name,value)
  except Exception as e:report[name+'_error']=str(e)
 report['after_builder_properties']=str(volume.get_actor_bounds(False))
_,extent=volume.get_actor_bounds(False);volume.set_actor_scale3d(unreal.Vector(45000/max(1,extent.x),30000/max(1,extent.y),250/max(1,extent.z)));report['after_scale']=str(volume.get_actor_bounds(False));world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();report['navigation_system']=str(unreal.NavigationSystemV1.get_navigation_system(world));(r/'work/engine_navigation_authoring_probe.json').write_text(json.dumps(report,indent=2));actors.destroy_actor(volume);unreal.log('ENGINE_NAVIGATION_AUTHORING_PROBE_COMPLETE')
