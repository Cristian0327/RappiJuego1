import unreal,json,sys,math
from pathlib import Path
R=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(R/'python_deps'))
from shapely.geometry import LineString,Point,MultiPoint
from shapely.ops import unary_union,nearest_points
from shapely import wkt
S=R.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
lanes=json.loads((S/'actual_lanes.json').read_text());corridor=unary_union([LineString(p+[p[0]]).buffer(225) for i,p in enumerate(lanes) if i not in [4,5]])
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
names={x['actor'] for x in json.loads((R/'lane_static_obstacles_rebuilt.json').read_text()) if x['actor'].startswith('StaticMeshActor_')};report=[]
for a in aa.get_all_level_actors():
 if a.get_name() not in names:continue
 c=a.get_components_by_class(unreal.StaticMeshComponent)[0];src=c.static_mesh;path=src.get_path_name().split('.')[0].removesuffix('_TrafficClearance');src=unreal.load_asset(path)
 dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(src,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL))
 _,vl,_=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dm,False);verts=unreal.GeometryScript_List.convert_vector_list_to_array(vl)
 tr=c.get_world_transform();world=[unreal.MathLibrary.transform_location(tr,v) for v in verts]
 _,tl,_=unreal.GeometryScript_MeshQueries.get_all_triangle_indices(dm,False);triangles=unreal.GeometryScript_List.convert_triangle_list_to_array(tl)
 remove=[];high_in_corridor=0
 for i,t in enumerate(triangles):
  if min(t.x,t.y,t.z)<0:continue
  q=[world[t.x],world[t.y],world[t.z]];lo=min(v.z for v in q);hi=max(v.z for v in q)
  if lo>240 or hi<-120:continue
  footprint=MultiPoint([(v.x,v.y) for v in q]).convex_hull
  if not corridor.intersects(footprint):continue
  if hi<240 and lo>-120:remove.append(i)
  else:high_in_corridor+=1
 row=dict(actor=a.get_name(),source=path,triangles=len(triangles),removed_low_triangles=len(remove),preserved_tall_intersections=high_in_corridor)
 if remove:
  ids=unreal.GeometryScript_List.convert_array_to_index_list(remove)
  unreal.GeometryScript_MeshEdits.delete_triangles_from_mesh(dm,ids)
  dest=path+'_TrafficClearance';mesh=unreal.load_asset(dest) or unreal.EditorAssetLibrary.duplicate_asset(path,dest)
  opts=unreal.GeometryScriptCopyMeshToAssetOptions(use_build_scale=False)
  unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm,mesh,opts,unreal.GeometryScriptMeshWriteLOD())
  mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
  c.set_editor_property('static_mesh',mesh);row['asset']=dest
 report.append(row);unreal.log('RESUME_LOW_CLEARANCE '+json.dumps(row))
# Move the pole and its visible lamps together onto the sidewalk, without changing timing or admission.
walk=wkt.loads((S/'sidewalks.wkt').read_text()).buffer(-70).difference(corridor.buffer(30))
pole=next(a for a in aa.get_all_level_actors() if a.get_name()=='BP_BogotaSignal_C_17');old=pole.get_actor_location();target=nearest_points(Point(old.x,old.y),walk)[1]
assert math.hypot(target.x-old.x,target.y-old.y)<1500
pole.set_actor_location(unreal.Vector(target.x,target.y,old.z),False,True)
(R/'low_clearance_changes.json').write_text(json.dumps(dict(frontages=report,pole=dict(actor=pole.get_name(),old=list(old.to_tuple()),new=[target.x,target.y,old.z])),indent=2))
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/QA/AdaptationTraffic')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic');bp=unreal.load_asset('/Game/QA/BP_AdaptationTrafficProbe');probe=aa.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level()
hits=[]
for li in [0,1,2,3,6]:
 points=lanes[li]
 for i,q in enumerate(points):
  e=points[(i+1)%len(points)];start=unreal.Vector(q[0],q[1],q[2]+120);end=unreal.Vector(e[0],e[1],e[2]+120)
  blocked,actor,component,impact=probe.call_method('QueryRoadStatic',(start,end))
  if blocked:hits.append(dict(lane=li,segment=i,actor=actor.get_name() if actor else None,label=actor.get_actor_label() if actor else None,component=component,start=list(start.to_tuple()),end=list(end.to_tuple()),impact=list(impact.to_tuple())))
(R/'lane_static_obstacles_low_clearance.json').write_text(json.dumps(hits,indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('RESUME_LOW_CORRIDOR_AUDIT '+str(len(hits)))