import unreal,json,sys,math,bisect,shutil
from pathlib import Path
R=Path(unreal.Paths.project_dir()).parent;S=R.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2';P=R/'scripts/map_adaptation_v2'
sys.path.insert(0,str(R/'python_deps'));sys.path.insert(0,str(R/'Herramientas'))
import blueprint_graph as d
from shapely.geometry import LineString,Point
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
TM='/Game/World/BlueprintWorld/Traffic/BP_TrafficManager';J='/Game/World/BlueprintWorld/Traffic/BP_TrafficJunction';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle';M='/Script/Engine.KismetMathLibrary';K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics'
def save(b):assert EL.save_loaded_asset(b,only_if_is_dirty=False)
def run_local(name):
 path=R/name;exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
# Build the segment-limited static probe while preserving parking, walking and traffic limits.
b=unreal.load_asset('/Game/Traffic/Services/BP_TwoWheelerCitizen');spec=json.loads((S/'cycle_unified_spec.json').read_text())
spec['nodes'] += [dict(id='RoadSegmentLength',kind='call',fn='FMin',owner=M,defaults={}),dict(id='RoadSegmentDelta',kind='call',fn='Multiply_VectorFloat',owner=M,defaults={}),dict(id='RoadSegmentEnd',kind='call',fn='Add_VectorVector',owner=M,defaults={})]
spec['links']=[x for x in spec['links'] if x!=['LookEnd','ReturnValue','RoadStatic','End']]+[['LookDistance','ReturnValue','RoadSegmentLength','A'],['GoalDistance','ReturnValue','RoadSegmentLength','B'],['GoalDirection','ReturnValue','RoadSegmentDelta','A'],['RoadSegmentLength','ReturnValue','RoadSegmentDelta','B'],['At','ReturnValue','RoadSegmentEnd','A'],['RoadSegmentDelta','ReturnValue','RoadSegmentEnd','B'],['RoadSegmentEnd','ReturnValue','RoadStatic','End']]
assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'ReceiveTick',json.dumps(spec));assert E.compile_blueprint(b);save(b)
# Build an oriented physical body sweep for the static corridor checks.
b=unreal.load_asset('/Game/QA/BP_AdaptationTrafficProbe');g=d.Graph();g.node('Types','makearray',defaults={'[0]':'ObjectTypeQuery1'});g.call('Size','MakeVector',M,Y='155',Z='155');g.link('entry','HalfLength','Size','X');g.call('Rot','MakeRotator',M);g.link('entry','Yaw','Rot','Yaw')
g.call('Sweep','BoxTraceSingleForObjects',K,bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true');g.link('entry','Start','Sweep','Start');g.link('entry','End','Sweep','End');g.link('Size','ReturnValue','Sweep','HalfSize');g.link('Rot','ReturnValue','Sweep','Orientation');g.link('Types','Array','Sweep','ObjectTypes');g.exec('entry','Sweep');g.call('Hit','BreakHitResult',G);g.link('Sweep','OutHit','Hit','Hit');g.call('Component','GetObjectName',K);g.link('Hit','HitComponent','Component','Object');g.link('Sweep','ReturnValue','result','Blocked');g.link('Hit','HitActor','result','Obstacle');g.link('Component','ReturnValue','result','Component');g.link('Hit','ImpactPoint','result','Impact');g.exec('Sweep','result')
params=[dict(name=n,category='struct',object='/Script/CoreUObject.Vector') for n in ['Start','End']]+[dict(name=n,category='real') for n in ['HalfLength','Yaw']]+[dict(name='Blocked',category='bool',out=True),dict(name='Obstacle',category='object',object='/Script/Engine.Actor',out=True),dict(name='Component',category='string',out=True),dict(name='Impact',category='struct',object='/Script/CoreUObject.Vector',out=True)]
assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'QueryRoadBody',json.dumps(dict(nodes=g.nodes,links=g.links,parameters=params)));assert E.compile_blueprint(b);save(b)
# Keep diagnostic static probes on the same current segment as the character.
probe_script=P/'build_resume_diagnostics.py';text=probe_script.read_text();text=text.replace("op(g,'DiagAhead','Multiply_VectorFloat',('DiagDir','ReturnValue'),B='500')","op(g,'DiagDistance','VSizeXY',('DiagDelta','ReturnValue'));op(g,'DiagCap','FMin',('DiagDistance','ReturnValue'),B='500');op(g,'DiagAhead','Multiply_VectorFloat',('DiagDir','ReturnValue'),('DiagCap','ReturnValue'))")
probe_script.write_text(text)
# Journal the bus stops and service starts once, so repeated iterations stay absolute.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
basefile=R/'clearance_install_baseline.json'
if basefile.exists():baseline=json.loads(basefile.read_text())
else:
 signals=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaServiceSignals_C');baseline=dict(indices={a.get_name():int(a.get_editor_property('RouteIndex')) for a in signals.get_editor_property('RoadActors')},stops={})
 for path in [V,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_TransMilenio']:
  baseline['stops'][path]=[list(p.to_tuple()) for p in unreal.get_default_object(unreal.load_asset(path).generated_class()).get_editor_property('TransitStopPositions')]
 basefile.write_text(json.dumps(baseline,indent=2))
for iteration in range(3):
 run_local('plan_clearance_lanes.py');run_local('remap_clearance_arcs.py')
 lanes=json.loads((R/'clearance_lanes.json').read_text());arcs=json.loads((R/'clearance_arc_conflicts.json').read_text());mapping=json.loads((R/'clearance_arc_distance_mapping.json').read_text())
 for i,points in enumerate(lanes):
  b=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i));parts={str(lib.get_variable_name(lib.get_data(h))):lib.get_object_for_blueprint(lib.get_data(h),b) for h in sub.k2_gather_subobject_data_for_blueprint(b)};curve=parts['Route'];curve.set_spline_points([unreal.Vector(*p) for p in points],unreal.SplineCoordinateSpace.LOCAL,False)
  for j in range(len(points)):curve.set_spline_point_type(j,unreal.SplinePointType.LINEAR,False)
  curve.set_closed_loop(True,True);assert E.compile_blueprint(b);cdo=unreal.get_default_object(b.generated_class())
  for name,key in [('ArcEntries','entry'),('ArcExits','exit'),('ArcJunctions','junction'),('ArcGroups','group'),('ArcMovements','movement')]:cdo.set_editor_property(name,[e[key] for e in arcs['lanes'][i]['events']])
  save(b)
 b=unreal.load_asset(J);cdo=unreal.get_default_object(b.generated_class());cdo.set_editor_property('ArcCompatible',arcs['compatible']);cdo.set_editor_property('ArcMovementCount',arcs['movement_count']);save(b)
 # Map bus stops by their position on the original route, retaining station IDs.
 old_points=json.loads((S/'actual_lanes.json').read_text())[6];old_line=LineString(old_points+[old_points[0]]);new_line=LineString(lanes[6]+[lanes[6][0]]);oc=mapping['old'][6];nc=mapping['new'][6]
 for path,stops in baseline['stops'].items():
  updated=[]
  for p in stops:
   dist=old_line.project(Point(p[:2]));j=min(len(oc)-2,bisect.bisect_right(oc,dist)-1);u=(dist-oc[j])/max(oc[j+1]-oc[j],1e-9);q=new_line.interpolate(nc[j]+u*(nc[j+1]-nc[j]));updated.append(unreal.Vector(q.x,q.y,p[2]))
  b=unreal.load_asset(path);unreal.get_default_object(b.generated_class()).set_editor_property('TransitStopPositions',updated);save(b)
 unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');signals=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaServiceSignals_C')
 for actor,li in zip(signals.get_editor_property('RoadActors'),signals.get_editor_property('ServiceLaneIndices')):actor.set_editor_property('Route',[unreal.Vector(*p) for p in lanes[li]]);actor.set_editor_property('RouteIndex',baseline['indices'][actor.get_name()])
 assert unreal.EditorLoadingAndSavingUtils.save_current_level();(P/'actual_lanes.json').write_text(json.dumps(lanes));(P/'arc_conflicts.json').write_text(json.dumps(arcs))
 exec(compile((P/'respace_clear_stoplines.py').read_text(),'clearance_initial_spacing','exec'),{})
 unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');manager=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_TrafficManager_C');cdo=unreal.get_default_object(unreal.load_asset(TM).generated_class())
 for name in ['InitialDistances','LeaderIndices']:manager.set_editor_property(name,cdo.get_editor_property(name))
 assert unreal.EditorLoadingAndSavingUtils.save_current_level()
 exec(compile(probe_script.read_text(),'clearance_probe','exec'),{'__file__':str(probe_script)})
 unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic');probe=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_AdaptationTrafficProbe_C');hits=[]
 for li in [0,1,2,3,6]:
  points=lanes[li];hl=915 if li==6 else 340
  for i,q in enumerate(points):
   end=points[(i+1)%len(points)];start=unreal.Vector(q[0],q[1],q[2]+190);finish=unreal.Vector(end[0],end[1],end[2]+190);yaw=math.degrees(math.atan2(end[1]-q[1],end[0]-q[0]));blocked,actor,component,impact=probe.call_method('QueryRoadBody',(start,finish,hl,yaw))
   if blocked:hits.append(dict(lane=li,segment=i,actor=actor.get_name() if actor else None,component=component,impact=list(impact.to_tuple())))
 (R/('clearance_body_audit_%d.json'%iteration)).write_text(json.dumps(hits,indent=2));unreal.log('RESUME_BODY_AUDIT iteration='+str(iteration)+' hits='+str(len(hits)))
 if not hits:
  (R/'clearance_install_result.json').write_text(json.dumps(dict(static_body_audit_passed=True,iterations=iteration+1),indent=2));break
 rows=json.loads((R/'route_obstacle_footprints.json').read_text());rows.extend([dict(actor=h['actor'],component=h['component'],wkt=Point(h['impact'][:2]).buffer(125).wkt,approximation=True) for h in hits]);(R/'route_obstacle_footprints.json').write_text(json.dumps(rows))
 unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
else:(R/'clearance_install_result.json').write_text(json.dumps(dict(static_body_audit_passed=False,remaining_hits=len(hits)),indent=2))
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('RESUME_CLEARANCE_BATCH_FINISHED')