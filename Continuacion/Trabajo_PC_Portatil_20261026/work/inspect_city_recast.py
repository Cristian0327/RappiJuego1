import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PureCityCrowd');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);out={}
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.RecastNavMesh):
  for p in ['runtime_generation','tile_size_uu','cell_size','cell_height','agent_radius','agent_height','agent_max_height','agent_max_step_height','tile_pool_size','fixed_tile_pool_size','can_be_main_nav_data','force_rebuild_on_load','nav_mesh_resolution_params']:
   try:out[p]=str(a.get_editor_property(p))
   except Exception as e:out[p]=str(e)
(r/'work/city_recast_configuration.json').write_text(json.dumps(out,indent=2));unreal.log('RECAST_CONFIG_PASS')
