import unreal,json,sys,math,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;M=d.M;AL='/Script/Engine.KismetArrayLibrary';A='/Script/Engine.Actor';K='/Script/Engine.KismetSystemLibrary';plan=json.loads(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/integration_plan.json').read_text());folder='/Game/World/BlueprintWorld/Traffic';sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
# Polyline pedestrian routes follow each curved sidewalk, with no rectangle shortcuts across buildings.
bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrowdManager');d.bp=bp;C='/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen.BP_StreetCitizen_C';P=bp.generated_class().get_path_name();vec=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'));known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in [('CityRoutePoints',E.get_array_type(vec)),('CitySpawnRoutes',E.get_array_type(E.get_basic_type_by_name('int'))),('CityRouteIndices',E.get_array_type(E.get_basic_type_by_name('int'))),('CityRouteScratch',E.get_array_type(vec))]:
 if n not in known:assert E.add_member_variable(bp,n,t)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());rows=plan['pedestrians'];c.set_editor_property('CityRoutePoints',[unreal.Vector(*p) for route in plan['walk_routes'] for p in route]);c.set_editor_property('CitySpawnRoutes',[s['route'] for s in rows]);c.set_editor_property('CityRouteIndices',list(range(32)));c.set_editor_property('SpawnPositions',[unreal.Vector(*s['position']) for s in rows]);c.set_editor_property('Headings',[s['yaw'] for s in rows]);c.set_editor_property('Models',[s['model'] for s in rows]);c.set_editor_property('StartIndices',[s['next'] for s in rows])
g=d.Graph()
for n in ['CityRoutePoints','CitySpawnRoutes','CityRouteIndices','CityRouteScratch','StartIndices']:g.get(n)
g.call('RouteAt','Array_Get',AL);g.link('CitySpawnRoutes','CitySpawnRoutes','RouteAt','TargetArray');g.link('entry','Index','RouteAt','Index');g.call('Offset','Multiply_IntInt',M,B='32');g.link('RouteAt','Item','Offset','A');g.call('Clear','Array_Clear',AL);g.link('CityRouteScratch','CityRouteScratch','Clear','TargetArray');g.exec('entry','Clear');g.node('Each','foreach');g.link('CityRouteIndices','CityRouteIndices','Each','Array');g.link('Clear','then','Each','Exec');g.call('FlatIndex','Add_IntInt',M);g.link('Offset','ReturnValue','FlatIndex','A');g.link('Each','Array Element','FlatIndex','B');g.call('Point','Array_Get',AL);g.link('CityRoutePoints','CityRoutePoints','Point','TargetArray');g.link('FlatIndex','ReturnValue','Point','Index');g.call('Append','Array_Add',AL);g.link('CityRouteScratch','CityRouteScratch','Append','TargetArray');g.link('Point','Item','Append','NewItem');g.link('Each','LoopBody','Append','execute');g.node('Assign','setfield',owner=C,var='Route');g.link('entry','Citizen','Assign','self');g.link('CityRouteScratch','CityRouteScratch','Assign','Route');g.link('Each','Completed','Assign','execute');g.call('NextAt','Array_Get',AL);g.link('StartIndices','StartIndices','NextAt','TargetArray');g.link('entry','Index','NextAt','Index');g.node('Next','setfield',owner=C,var='RouteIndex');g.link('entry','Citizen','Next','self');g.link('NextAt','Item','Next','RouteIndex');g.exec('Assign','Next');g.call('Wake','SetFarMode',C,NewFar='false');g.link('entry','Citizen','Wake','self');g.call('InitializeDormant','SetFarMode',C,NewFar='true');g.link('entry','Citizen','InitializeDormant','self');g.exec('Next','InitializeDormant');g.exec('InitializeDormant','Wake');g.exec('Wake','result');cg=g
g=d.Graph()
for n in ['Citizens','SpawnPositions','Headings','Models']:g.get(n)
g.node('Each','foreach');g.link('SpawnPositions','SpawnPositions','Each','Array');g.link('entry','then','Each','Exec')
for n in ['Headings','Models']:g.call(n+'At','Array_Get',AL);g.link(n,n,n+'At','TargetArray');g.link('Each','Array Index',n+'At','Index')
g.call('Spawn','SpawnModel',P);g.link('ModelsAt','Item','Spawn','ModelIndex');g.link('Each','Array Element','Spawn','Position');g.link('HeadingsAt','Item','Spawn','Facing');g.link('Each','LoopBody','Spawn','execute');
rename={'Each':'RouteEach','Append':'RouteAppend'}
for n in cg.nodes:
 n=n.copy();n['id']=rename.get(n['id'],n['id']);g.nodes.append(n)
for l in cg.links:
 l=l.copy();l[0]=rename.get(l[0],l[0]);l[2]=rename.get(l[2],l[2])
 if l[0]=='entry':
  if l[1]=='then':l[0]='Spawn'
  elif l[1]=='Citizen':l[0]='Spawn';l[1]='ReturnValue'
  elif l[1]=='Index':l[0]='Each';l[1]='Array Index'
 if l[2]=='result':l[2]='AppendCitizen'
 g.links.append(l)
g.call('AppendCitizen','Array_Add',AL);g.link('Citizens','Citizens','AppendCitizen','TargetArray');g.link('Spawn','ReturnValue','AppendCitizen','NewItem');g.link('Each','Completed','result','execute');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'CreateCrowd',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[]}));assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('NEW_MAP_CROWD_READY')
