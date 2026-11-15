import unreal,json,sys,math
from pathlib import Path
P=Path(__file__).resolve().parent
root=Path(unreal.Paths.project_dir()).parent
sys.path.insert(0,str(root/'Herramientas'))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rows=[]
for a in aa.get_all_level_actors():
 if a.get_class().get_name() in ['BP_BogotaTransmiStation_C','BP_BogotaSignal_C'] or a.get_name() in ['StaticMeshActor_47','StaticMeshActor_7']:
  row=dict(name=a.get_name(),label=a.get_actor_label(),cls=a.get_class().get_name(),location=list(a.get_actor_location().to_tuple()),rotation=list(a.get_actor_rotation().to_tuple()),components=[])
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   mesh=c.get_editor_property('static_mesh')
   row['components'].append(dict(name=c.get_name(),mesh=mesh.get_path_name() if mesh else None,transform=str(c.get_world_transform()),bounds=str(mesh.get_bounds()) if mesh else None,collision=str(c.get_collision_profile_name()),trace_flag=str(mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')) if mesh else None))
  rows.append(row)
(root/'static_obstacle_inspection.json').write_text(json.dumps(rows,indent=2))
for r in rows:
 if r['cls']=='BP_BogotaTransmiStation_C' or r['name'] in ['StaticMeshActor_47','StaticMeshActor_7','BP_BogotaSignal_C_17']:unreal.log('RESUME_OBSTACLE '+json.dumps(r))
bp=unreal.load_asset('/Game/World/BogotaUrban/BP_BogotaTransmiStation')
(root/'station_blueprint_audit.txt').write_text(unreal.DeliveryEditorLibrary.audit_blueprint(bp))
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
unreal.log('RESUME_STATIC_INSPECTION_COMPLETE')