from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');CYCLE='/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C';b=use(CYCLE);addvar(b,'TrafficSpeedLimit',real);assert E.compile_blueprint(b);unreal.get_default_object(b.generated_class()).set_editor_property('TrafficSpeedLimit',650.);save(b)
source=(root/'work/build_two_wheeler_citizen.py').read_text();header=source[:source.index('g=d.Graph();g.variables=')];start=source.index('# Per-frame movement');end=source.index("try:g.build('ReceiveTick')",start);ns={};exec(compile(header+source[start:end],'CycleCurrentMotion','exec'),ns);g=ns['g'];b=ns['bp'];g.get('TrafficSpeedLimit');g.call('TrafficCap','FMin',M);g.link('TrafficSpeedLimit','TrafficSpeedLimit','TrafficCap','A');g.link('TargetSpeed','ReturnValue','TrafficCap','B');g.call('RoadOrParking','BooleanOR',M);g.link('IsRiding','ReturnValue','RoadOrParking','A');g.link('IsParking','ReturnValue','RoadOrParking','B');g.call('StateSpeed','SelectFloat',M);g.link('TrafficCap','ReturnValue','StateSpeed','A');g.link('TargetSpeed','ReturnValue','StateSpeed','B');g.link('RoadOrParking','ReturnValue','StateSpeed','bPickA');g.links.remove(['TargetSpeed','ReturnValue','MoveStart','MaxWalkSpeed']);g.link('StateSpeed','ReturnValue','MoveStart','MaxWalkSpeed')
g.node('StaticTypes','makearray',defaults={'[0]':'ObjectTypeQuery1'});g.call('RoadStatic','SphereTraceSingleForObjects',K,Radius='70',bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true');g.link('At','ReturnValue','RoadStatic','Start');g.link('LookEnd','ReturnValue','RoadStatic','End');g.link('StaticTypes','Array','RoadStatic','ObjectTypes');g.links.remove(['LookTrace','then','SideTrace','execute']);g.exec('LookTrace','RoadStatic');g.exec('RoadStatic','SideTrace')
for link in g.links:
 if link[0]=='Blocked':link[0]='CurrentRoadBlock'
op(g,'RoadProbeOn','BooleanAND',('RoadStatic','ReturnValue'),('IsRiding','ReturnValue'));op(g,'NotRidingState','Not_PreBool',('IsRiding','ReturnValue'));op(g,'WalkProbeOn','BooleanAND',('Blocked','ReturnValue'),('NotRidingState','ReturnValue'));op(g,'CurrentRoadBlock','BooleanOR',('RoadProbeOn','ReturnValue'),('WalkProbeOn','ReturnValue'))
for link in list(g.links):
 if link[2:] in [['CanDetourMode','A'],['CanDetourMode','B']]:g.links.remove(link)
g.link('IsWalking','ReturnValue','CanDetourMode','A')
for node in g.nodes:
 if node['id']=='CanDetourMode':node['defaults']={'B':'false'}
(P/'cycle_unified_spec.json').write_text(json.dumps(dict(nodes=g.nodes,links=g.links),indent=2));assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'ReceiveTick',json.dumps(dict(nodes=g.nodes,links=g.links)));assert E.compile_blueprint(b);save(b)
# Keep existing patrol heading correction, use static obstacle probes alongside shared traffic envelopes.
source=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/repair_patrol_heading.py').read_text();exec(compile(source[:source.rindex("build(b,g,'ReceiveTick')")],'CurrentRoadVehicleMotion','exec'))
for node in g.nodes:
 if node['id']=='Trace':node['fn']='SphereTraceSingleForObjects';node['defaults'].pop('TraceChannel',None)
g.node('StaticRoadTypes','makearray',defaults={'[0]':'ObjectTypeQuery1'});g.link('StaticRoadTypes','Array','Trace','ObjectTypes');build(b,g,'ReceiveTick');save(b)
# Refresh dependent service classes after replacing their inherited functions.
for asset in ['/Game/Traffic/Services/BP_CivilMotorcycle','/Game/Traffic/Services/BP_PoliceMotorcycle','/Game/Traffic/Services/BP_PoliceRoadPatrol']:
 b=use(asset);assert E.compile_blueprint(b);save(b)
unreal.log('V2_SERVICE_CONTROLLERS_UNIFIED')
