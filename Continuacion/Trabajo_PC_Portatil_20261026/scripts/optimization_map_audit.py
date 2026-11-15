import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
report={'actors':[],'navigation':[]}
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 row=dict(name=actor.get_name(),label=actor.get_actor_label(),cls=actor.get_class().get_path_name(),components=[])
 if isinstance(actor,unreal.RecastNavMesh):
  nav=dict(name=actor.get_name())
  for key in ['runtime_generation','force_rebuild_on_load','tile_size_uu','cell_size','cell_height','agent_radius','agent_height']:
   try:nav[key]=str(actor.get_editor_property(key))
   except Exception:pass
  report['navigation'].append(nav)
 for component in actor.get_components_by_class(unreal.PrimitiveComponent):
  c=dict(name=component.get_name(),cls=component.get_class().get_name())
  for key in ['can_ever_affect_navigation','ld_max_draw_distance','cached_max_draw_distance','cast_shadow']:
   try:c[key]=str(component.get_editor_property(key))
   except Exception:pass
  if isinstance(component,unreal.StaticMeshComponent):
   m=component.get_editor_property('static_mesh')
   if m:c['mesh']=m.get_path_name()
  if isinstance(component,unreal.InstancedStaticMeshComponent):c['instances']=component.get_instance_count()
  row['components'].append(c)
 report['actors'].append(row)
(R/'optimization_map_audit.json').write_text(json.dumps(report,indent=2))
unreal.log('OPTIMIZATION_MAP_AUDIT_READY')
