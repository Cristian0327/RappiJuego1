import unreal,json,sys,math
from pathlib import Path
R=Path(unreal.Paths.project_dir()).parent;S=R.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
sys.path.insert(0,str(R/'python_deps'))
from shapely.geometry import LineString,Point
from shapely.ops import unary_union,nearest_points
from shapely import wkt
old=unreal.Vector(13436.757076822068,-29330.868837787522,0)
yaw=math.radians(125.56925201416013);t=unreal.Vector(math.cos(yaw),math.sin(yaw),0);n=unreal.Vector(-t.y,t.x,0);delta=t*-4000;new=old+delta
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
station=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaTransmiStation_C' and a.get_editor_property('StationId')==4)
assert (station.get_actor_location()-old).length()<5 or (station.get_actor_location()-new).length()<5
changed=[]
if (station.get_actor_location()-old).length()<5:
 # Translate only the station's access and crossing geometry; preserve all other stations and materials.
 for name in ['SM_Bogota_AccesosEstaciones','SM_Bogota_MarcasInterseccion']:
  mesh=unreal.load_asset('/Game/World/BogotaUrban/Geometry/'+name);backup_path='/Game/QA/Station4Baseline/'+name;baseline_mesh=unreal.load_asset(backup_path) or unreal.EditorAssetLibrary.duplicate_asset(mesh.get_path_name().split('.')[0],backup_path);assert unreal.EditorAssetLibrary.save_loaded_asset(baseline_mesh,only_if_is_dirty=False);dm=unreal.DynamicMesh()
  unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(baseline_mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.RENDER_DATA))
  _,vl,_=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dm,False);vs=unreal.GeometryScript_List.convert_vector_list_to_array(vl);count=0
  assert max(abs(v.x) for v in vs)>20000
  for i,v in enumerate(vs):
   off=v-old
   if abs(off.dot(t))<4000 and abs(off.dot(n))<2800:vs[i]=v+delta;count+=1
  if count==0:
   assert name!='SM_Bogota_AccesosEstaciones',(name,count)
   changed.append(dict(asset=name,vertices=0));continue
  vl=unreal.GeometryScript_List.convert_array_to_vector_list(vs)
  unreal.GeometryScript_MeshEdits.set_all_mesh_vertex_positions(dm,vl)
  unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm,mesh,unreal.GeometryScriptCopyMeshToAssetOptions(use_build_scale=False),unreal.GeometryScriptMeshWriteLOD())
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);changed.append(dict(asset=name,vertices=count))
 station.set_actor_location(new,False,True)
 for a in aa.get_all_level_actors():
  cls=a.get_class().get_name();p=a.get_actor_location();off=p-old
  if cls=='BP_StationPassenger_C' and a.get_editor_property('Station')==4:a.set_actor_location(p+delta,False,True);changed.append(dict(passenger=a.get_name()))
  if cls=='BP_BogotaSignal_C' and a.get_editor_property('SignalGroup')==2 and abs(off.dot(t))<4000 and abs(off.dot(n))<2800:a.set_actor_location(p+delta,False,True);changed.append(dict(signal=a.get_name()))
  if cls=='BP_CrosswalkCitizen_C':
   route=list(a.get_editor_property('Route'))
   if any(abs((q-old).dot(t))<3500 and abs((q-old).dot(n))<2500 and q.z>60 for q in route):a.set_editor_property('Route',[q+delta for q in route]);a.set_actor_location(p+delta,False,True);changed.append(dict(crosswalk=a.get_name()))
 TM='/Game/World/BlueprintWorld/Traffic/BP_TrafficManager'
 bp=unreal.load_asset(TM);cdo=unreal.get_default_object(bp.generated_class());centers=list(cdo.get_editor_property('UrbanCrossingCenters'));groups=list(cdo.get_editor_property('UrbanSignalGroups'))
 basefile=R/'station4_metadata_baseline.json'
 if basefile.exists():
  metadata=json.loads(basefile.read_text());centers=[unreal.Vector(*p) for p in metadata['centers']];groups=metadata['groups']
 else:
  base_vehicle=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');initial_stops=list(unreal.get_default_object(base_vehicle.generated_class()).get_editor_property('TransitStopPositions'));metadata=dict(centers=[list(p.to_tuple()) for p in centers],groups=groups,stops=[list(p.to_tuple()) for p in initial_stops]);basefile.write_text(json.dumps(metadata,indent=2))
 for i,p in enumerate(centers):
  off=p-old
  if groups[i]==2 and abs(off.dot(t))<4000 and abs(off.dot(n))<2800:centers[i]=p+delta
 cdo.set_editor_property('UrbanCrossingCenters',centers);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
 for a in aa.get_all_level_actors():
  if a.get_class().get_name()=='BP_TrafficManager_C':a.set_editor_property('UrbanCrossingCenters',centers)
 lane=aa.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_6').generated_class(),unreal.Vector())
 base=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');stops=[unreal.Vector(*p) for p in metadata['stops']];distance=lane.call_method('ClosestDistance',(stops[4]+delta,));stops[4]=lane.call_method('SamplePosition',(distance,))
 for path in ['/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle','/Game/World/BlueprintWorld/Traffic/BP_Traffic_TransMilenio']:
  bp=unreal.load_asset(path);unreal.get_default_object(bp.generated_class()).set_editor_property('TransitStopPositions',stops);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
 aa.destroy_actor(lane)
 # Put moved signal poles back on a safe sidewalk position while keeping their complete heads together.
 lanes=json.loads((S/'actual_lanes.json').read_text());corridor=unary_union([LineString(p+[p[0]]).buffer(255) for i,p in enumerate(lanes) if i not in [4,5]])
 safe=wkt.loads((S/'sidewalks.wkt').read_text()).buffer(-70).difference(corridor)
 signal_names={x['signal'] for x in changed if 'signal' in x}
 for a in aa.get_all_level_actors():
  if a.get_name() not in signal_names:continue
  p=a.get_actor_location();q=nearest_points(Point(p.x,p.y),safe)[1];assert math.hypot(q.x-p.x,q.y-p.y)<2000;a.set_actor_location(unreal.Vector(q.x,q.y,p.z),False,True)
 assert unreal.EditorLoadingAndSavingUtils.save_current_level()
(R/'station4_synchronized_move.json').write_text(json.dumps(dict(old=list(old.to_tuple()),new=list(new.to_tuple()),delta=list(delta.to_tuple()),changes=changed),indent=2))
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/QA/AdaptationTraffic')
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic');bp=unreal.load_asset('/Game/QA/BP_AdaptationTrafficProbe');aa.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
unreal.log('RESUME_STATION4_SYNCHRONIZED '+str(len(changed)))
exec(compile((R/'scripts/export_route_obstacles.py').read_text(),'export_route_obstacles','exec'),{})
