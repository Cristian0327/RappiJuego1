import unreal,json,sys
from pathlib import Path
R=Path(unreal.Paths.project_dir()).parent
src=unreal.load_asset('/Game/World/BogotaUrban/Geometry/SM_Bogota_EstacionTransmi_Compacta')
asset='/Game/World/BogotaUrban/Geometry/SM_Bogota_EstacionTransmi_Compacta_PhysicsFixed'
mesh=unreal.load_asset(asset) or unreal.EditorAssetLibrary.duplicate_asset(src.get_path_name().split('.')[0],asset)
dm=unreal.DynamicMesh()
unreal.log('RESUME_COMPACT_BUILD_SCALE '+str((unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem) or unreal.new_object(unreal.StaticMeshEditorSubsystem)).get_lod_build_settings(src,0).build_scale3d))
result=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(src,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL))
unreal.log('RESUME_COPY_COMPACT '+str(result))
_,positions,gaps=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dm,False)
verts=unreal.GeometryScript_List.convert_vector_list_to_array(positions)
limits=dict(min=[min(getattr(v,k) for v in verts) for k in ['x','y','z']],max=[max(getattr(v,k) for v in verts) for k in ['x','y','z']])
assert 1100<limits['max'][0]<1300 and -1300<limits['min'][0]<-1100,limits
options=unreal.GeometryScriptCopyMeshToAssetOptions();options.set_editor_property('use_build_scale',False)
outcome=unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm,mesh,options,unreal.GeometryScriptMeshWriteLOD())
unreal.log('RESUME_WRITE_COMPACT '+str(outcome))
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
mesh.get_editor_property('body_setup').set_editor_property('double_sided_geometry',True)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
assert 1100<mesh.get_bounds().box_extent.x<1300
# Read-only source/render size comparison for frontages implicated by the corridor audit.
measurements=[]
SS=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem) or unreal.new_object(unreal.StaticMeshEditorSubsystem)
for idx in [7,18,22,23,41,43,44,47,50,128]:
 item=unreal.load_asset('/Game/World/BogotaUrban/StreetFrontages/SM_StreetFrontage_%03d'%idx)
 row=dict(asset=item.get_path_name(),bounds=str(item.get_bounds()),build_scale=str(SS.get_lod_build_settings(item,0).build_scale3d))
 for tag,typ in [('source',unreal.GeometryScriptLODType.SOURCE_MODEL),('render',unreal.GeometryScriptLODType.RENDER_DATA)]:
  tmp=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(item,tmp,unreal.GeometryScriptCopyMeshFromAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshReadLOD(lod_type=typ))
  _,ls,_=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(tmp,False);vs=unreal.GeometryScript_List.convert_vector_list_to_array(ls)
  row[tag]=dict(min=[min(getattr(v,k) for v in vs) for k in ['x','y','z']],max=[max(getattr(v,k) for v in vs) for k in ['x','y','z']]) if vs else None
 measurements.append(row)
(R/'frontage_geometry_sizes.json').write_text(json.dumps(measurements,indent=2))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaTransmiStation_C' and a.get_editor_property('StationId')==2)
shell=next(c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='StationShell');shell.set_editor_property('static_mesh',mesh)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
probe_bp=unreal.load_asset('/Game/QA/BP_AdaptationTrafficProbe')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/QA/AdaptationTraffic')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic');probe=aa.spawn_actor_from_class(probe_bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level()
source=R.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2';lanes=json.loads((source/'actual_lanes.json').read_text());hits=[]
for li in [0,1,2,3,6]:
 points=lanes[li]
 for i,q in enumerate(points):
  e=points[(i+1)%len(points)];start=unreal.Vector(q[0],q[1],q[2]+120);end=unreal.Vector(e[0],e[1],e[2]+120)
  blocked,actor,component,impact=probe.call_method('QueryRoadStatic',(start,end))
  if blocked:hits.append(dict(lane=li,segment=i,actor=actor.get_name() if actor else None,label=actor.get_actor_label() if actor else None,component=component,start=list(start.to_tuple()),end=list(end.to_tuple()),impact=list(impact.to_tuple())))
(R/'lane_static_obstacles_rebuilt.json').write_text(json.dumps(hits,indent=2));(R/'compact_collision_rebuild.json').write_text(json.dumps(dict(asset=asset,limits=limits,bounds=str(mesh.get_bounds()),hits=len(hits)),indent=2))
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('RESUME_COMPACT_COLLISION_REBUILT '+str(len(hits)))