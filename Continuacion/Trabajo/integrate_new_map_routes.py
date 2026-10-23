import unreal,json,sys,math,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;M=d.M;AL='/Script/Engine.KismetArrayLibrary';A='/Script/Engine.Actor';K='/Script/Engine.KismetSystemLibrary';plan=json.loads(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/integration_plan.json').read_text());folder='/Game/World/BlueprintWorld/Traffic';sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for i,points in enumerate(plan['lanes']):
 bp=unreal.load_asset(folder+'/BP_TrafficLane_'+str(i));spline=next(lib.get_object_for_blueprint(lib.get_data(h),bp) for h in sub.k2_gather_subobject_data_for_blueprint(bp) if str(lib.get_variable_name(lib.get_data(h)))=='Route');p=[unreal.Vector(v[0],v[1],14) for v in points];spline.set_spline_points(p,unreal.SplineCoordinateSpace.LOCAL,False)
 for j in range(len(p)):spline.set_spline_point_type(j,unreal.SplinePointType.LINEAR,False)
 spline.set_closed_loop(True,True);assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Space the existing vehicle catalog over the new physical routes.
bp=unreal.load_asset(folder+'/BP_TrafficManager');c=unreal.get_default_object(bp.generated_class());models=list(c.get_editor_property('ModelIndices'));lanes=list(c.get_editor_property('LaneIndices'));dist=[];spawn=[];actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);routeactors=[actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_TrafficLane_'+str(i)).generated_class(),unreal.Vector()) for i in range(7)]
for i,li in enumerate(lanes):
 route=routeactors[li];length=route.call_method('RouteLength');v=length*((i*.61803398875)%1)
 for attempt in range(500):
  p=route.call_method('SamplePosition',(v,))
  if all((p-q).length()>950 for q in spawn):break
  v=(v+775)%length
 else:raise RuntimeError('Cannot safely place vehicle '+str(i))
 spawn.append(p);dist.append(v)
for a in routeactors:actors.destroy_actor(a)
c.set_editor_property('InitialDistances',dist);leaders=[]
for i,li in enumerate(lanes):
 group=sorted([j for j in range(len(lanes)) if lanes[j]==li],key=lambda j:dist[j]);leaders.append(group[(group.index(i)+1)%len(group)])
c.set_editor_property('LeaderIndices',leaders);c.set_editor_property('JunctionCentres',[]);assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Rebuild the occupied-cell grid for the full height of the new map, preserving its external object probe.
s=(r/'work/optimize_traffic_grid_queries.py').read_text(encoding='utf-8-sig');s=s[:s.index("exec(compile(s,'CachedThreeMeterTrafficGrid'")];ns={};exec(compile(s,'GridSource','exec'),ns);source=ns['s'];source=source.replace('range(560)','range(1120)').replace("B='560'","B='1120'").replace("('Y',30000,19)","('Y',60000,39)").replace("('Y',20)","('Y',40)").replace("B='20'","B='40'")
source=source.replace("g.setter('ResetLimit','ProbeClearance',value='100000000')","g.setter('ResetLimit','ProbeClearance','ExternalClearance')").replace("g.exec('entry','ResetLimit')","g.call('ExternalClearance','ExternalPawnClearance',V);g.link('entry','Visitor','ExternalClearance','self');g.exec('entry','ExternalClearance');g.exec('ExternalClearance','ResetLimit')");exec(compile(source,'MapSizedTrafficGrid','exec'),{})
# Polyline pedestrian routes follow each curved sidewalk, with no rectangle shortcuts across buildings.
bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrowdManager');d.bp=bp;C='/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen.BP_StreetCitizen_C';P=bp.generated_class().get_path_name();vec=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'));known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in [('CityRoutePoints',E.get_array_type(vec)),('CitySpawnRoutes',E.get_array_type(E.get_basic_type_by_name('int'))),('CityRouteIndices',E.get_array_type(E.get_basic_type_by_name('int'))),('CityRouteScratch',E.get_array_type(vec))]:
 if n not in known:assert E.add_member_variable(bp,n,t)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());rows=plan['pedestrians'];c.set_editor_property('CityRoutePoints',[unreal.Vector(*p) for route in plan['walk_routes'] for p in route]);c.set_editor_property('CitySpawnRoutes',[s['route'] for s in rows]);c.set_editor_property('CityRouteIndices',list(range(32)));c.set_editor_property('SpawnPositions',[unreal.Vector(*s['position']) for s in rows]);c.set_editor_property('Headings',[s['yaw'] for s in rows]);c.set_editor_property('Models',[s['model'] for s in rows]);c.set_editor_property('StartIndices',[s['next'] for s in rows])
g=d.Graph()
for n in ['CityRoutePoints','CitySpawnRoutes','CityRouteIndices','CityRouteScratch','StartIndices']:g.get(n)
g.call('RouteAt','Array_Get',AL);g.link('CitySpawnRoutes','CitySpawnRoutes','RouteAt','TargetArray');g.link('entry','Index','RouteAt','Index');g.call('Offset','Multiply_IntInt',M,B='32');g.link('RouteAt','Item','Offset','A');g.call('Clear','Array_Clear',AL);g.link('CityRouteScratch','CityRouteScratch','Clear','TargetArray');g.exec('entry','Clear');g.node('Each','foreach');g.link('CityRouteIndices','CityRouteIndices','Each','Array');g.link('Clear','then','Each','Exec');g.call('FlatIndex','Add_IntInt',M);g.link('Offset','ReturnValue','FlatIndex','A');g.link('Each','Array Element','FlatIndex','B');g.call('Point','Array_Get',AL);g.link('CityRoutePoints','CityRoutePoints','Point','TargetArray');g.link('FlatIndex','ReturnValue','Point','Index');g.call('Append','Array_Add',AL);g.link('CityRouteScratch','CityRouteScratch','Append','TargetArray');g.link('Point','Item','Append','NewItem');g.link('Each','LoopBody','Append','execute');g.node('Assign','setfield',owner=C,var='Route');g.link('entry','Citizen','Assign','self');g.link('CityRouteScratch','CityRouteScratch','Assign','Route');g.link('Each','Completed','Assign','execute');g.call('NextAt','Array_Get',AL);g.link('StartIndices','StartIndices','NextAt','TargetArray');g.link('entry','Index','NextAt','Index');g.node('Next','setfield',owner=C,var='RouteIndex');g.link('entry','Citizen','Next','self');g.link('NextAt','Item','Next','RouteIndex');g.exec('Assign','Next');g.call('Wake','SetFarMode',C,NewFar='false');g.link('entry','Citizen','Wake','self');g.exec('Next','Wake');g.exec('Wake','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'ConfigureCityRoute',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'Citizen','category':'object','object':C},{'name':'Index','category':'int'}]}))
assert E.compile_blueprint(bp)
g=d.Graph()
for n in ['Citizens','SpawnPositions','Headings','Models']:g.get(n)
g.node('Each','foreach');g.link('SpawnPositions','SpawnPositions','Each','Array');g.link('entry','then','Each','Exec')
for n in ['Headings','Models']:g.call(n+'At','Array_Get',AL);g.link(n,n,n+'At','TargetArray');g.link('Each','Array Index',n+'At','Index')
g.call('Spawn','SpawnModel',P);g.link('ModelsAt','Item','Spawn','ModelIndex');g.link('Each','Array Element','Spawn','Position');g.link('HeadingsAt','Item','Spawn','Facing');g.link('Each','LoopBody','Spawn','execute');g.call('Configure','ConfigureCityRoute',P);g.link('Spawn','ReturnValue','Configure','Citizen');g.link('Each','Array Index','Configure','Index');g.exec('Spawn','Configure');g.call('Append','Array_Add',AL);g.link('Citizens','Citizens','Append','TargetArray');g.link('Spawn','ReturnValue','Append','NewItem');g.exec('Configure','Append');g.link('Each','Completed','result','execute');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'CreateCrowd',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[]}));assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False)
(r/'outputs/MapRebuild/traffic_crowd_integration.json').write_text(json.dumps({'lanes':7,'vehicles':len(models),'pedestrians':len(rows),'sidewalk_loops':len(plan['walk_routes']),'traffic_grid_cells':1120}));unreal.log('NEW_MAP_TRAFFIC_AND_CROWD_READY')
