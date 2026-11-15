import unreal,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;backup=Path((R/'optimization_backup_path.txt').read_text());map_path='/Game/Maps/MapaCompleto_Integration'
source=Path(unreal.Paths.project_content_dir())/'Maps/MapaCompleto_Integration.umap';dest=backup/'Content/Maps/MapaCompleto_Integration.umap';dest.parent.mkdir(parents=True,exist_ok=True)
if not dest.exists():shutil.copy2(source,dest)
assert unreal.EditorLoadingAndSavingUtils.load_map(map_path)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);report={'cull_distances':[],'navigation':[],'skeletal_components':0,'lights':0}
for actor in actors.get_all_level_actors():
 if isinstance(actor,unreal.RecastNavMesh):
  actor.set_editor_property('force_rebuild_on_load',False)
  actor.set_editor_property('runtime_generation',unreal.RuntimeGenerationType.DYNAMIC)
  # Keep the existing navigation generation mode until baked data is validated.
  report['navigation'].append(dict(name=actor.get_name(),runtime=str(actor.get_editor_property('runtime_generation')),force_rebuild=False))
 for component in actor.get_components_by_class(unreal.StaticMeshComponent):
  mesh=component.get_editor_property('static_mesh')
  if not mesh:continue
  path=mesh.get_path_name();distance=0
  if '/Delivery/Stores/' in path and 'Interior' in path:distance=12000
  elif '/StreetFrontages/' in path:distance=65000
  # Ground, road lanes, station ramps and landmarks retain their full visibility range.
  if distance:
   component.set_editor_property('ld_max_draw_distance',distance);component.set_cull_distance(distance)
   if isinstance(component,unreal.InstancedStaticMeshComponent):component.set_cull_distances(int(distance*.85),distance)
   report['cull_distances'].append(dict(actor=actor.get_name(),component=component.get_name(),mesh=path,distance=distance))
 for component in actor.get_components_by_class(unreal.SkeletalMeshComponent):
  component.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ONLY_TICK_POSE_WHEN_RENDERED)
  report['skeletal_components']+=1
 for component in actor.get_components_by_class(unreal.PointLightComponent):
  component.set_editor_property('max_draw_distance',8000);component.set_editor_property('max_distance_fade_range',1500);report['lights']+=1
graphics=unreal.load_asset('/Game/World/BlueprintWorld/Optimization/BP_GraphicsSettings');assert graphics
if not any(actor.get_class()==graphics.generated_class() for actor in actors.get_all_level_actors()):actors.spawn_actor_from_class(graphics.generated_class(),unreal.Vector())
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
# Benchmark duplicate only; the real map has no automated exit or profiling actor.
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/OptimizationBenchmark');assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/OptimizationBenchmark');probe=unreal.load_asset('/Game/QA/BP_OptimizationFrameProbe');actors.spawn_actor_from_class(probe.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level()
(R/'optimization_map_changes.json').write_text(json.dumps(report,indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('OPTIMIZATION_MAP_READY')
