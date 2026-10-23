exec(compile(__import__('pathlib').Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts, 'Inspect only the isolated copy'
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rows=[];stations=[a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaTransmiStation_C'];plan=json.loads((P.parent/'new_map_audit/integration_plan.json').read_text())
for a in stations:
 at=a.get_actor_location();t=a.get_actor_transform();parts=[]
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  mesh=c.get_editor_property('static_mesh')
  if mesh:parts.append(dict(name=c.get_name(),mesh=mesh.get_path_name(),bounds=str(mesh.get_bounds()),relative=str(c.get_editor_property('relative_location')),scale=str(c.get_editor_property('relative_scale3d'))))
 distances=[]
 for i,points in enumerate(plan['lanes']):
  close=[]
  for p in points:
   q=unreal.MathLibrary.inverse_transform_location(t,unreal.Vector(*p))
   if abs(q.x)<1800:close.append(abs(q.y))
  distances.append(min(close) if close else None)
 rows.append(dict(name=a.get_name(),position=str(at),rotation=str(a.get_actor_rotation()),lanes_nearest_side=distances,parts=parts))
(P/'station_lane_clearance.json').write_text(json.dumps(rows,indent=2));unreal.log('STATION_CLEARANCE_AUDIT_DONE')
