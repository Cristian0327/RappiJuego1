import unreal,json,time
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);manager=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_TrafficManager.BP_TrafficManager_C'),unreal.Vector());cars=[];lanes=[];checks={}
def check(n,v):checks[n]=bool(v);assert v,n
try:
 manager.call_method('CreateTraffic');cars=list(manager.get_editor_property('Vehicles'));lanes=list(manager.get_editor_property('Lanes'));check('100_vehicles_7_lanes',len(cars)==100 and len(lanes)==7);check('23_model_variants',len(set(a.get_class().get_name() for a in cars))==23);check('16_taxis_4_buses',sum(a.get_editor_property('Taxi') for a in cars)==16 and sum(a.get_editor_property('Bus') for a in cars)==4)
 manager.call_method('CreateTraffic');check('initialization_idempotent',len(manager.get_editor_property('Vehicles'))==100)
 for a in cars:a.call_method('CacheReferencePose');a.call_method('CacheArticulation')
 initial=[float(a.get_editor_property('Distance')) for a in cars];start=time.perf_counter()
 for step in range(300):manager.call_method('SimulateFixedStep',(1/30,))
 elapsed=time.perf_counter()-start;check('all_vehicles_advance',all(abs(a.get_editor_property('Distance')-at)>100 for a,at in zip(cars,initial)))
 gapmin=1e9
 for a in cars:
  leader=a.get_editor_property('Leader');length=a.get_editor_property('Lane').call_method('RouteLength');gap=(leader.get_editor_property('Distance')-a.get_editor_property('Distance')+length)%length-a.get_editor_property('HalfLength')-leader.get_editor_property('HalfLength');gapmin=min(gapmin,gap)
 check('no_same_lane_overlap',gapmin>=189.9)
 manager.call_method('RenderTraffic',(.5,));check('all_wheel_caches_valid',all(len(a.get_editor_property('WheelRest'))==(6 if a.get_editor_property('Bus') else 4) for a in cars));check('all_leaders_same_lane',all(a.get_editor_property('Leader').get_editor_property('Lane')==a.get_editor_property('Lane') for a in cars))
 # Exercise the actual frame accumulator rather than directly simulating.
 before=manager.get_editor_property('SimulationSteps');manager.call_method('ReceiveTick',(.016,));check('substep_frame_renders_without_advancing',manager.get_editor_property('SimulationSteps')==before);manager.call_method('ReceiveTick',(.018,));check('fixed_step_accumulator_advances_once',manager.get_editor_property('SimulationSteps')==before+1);manager.call_method('ReceiveTick',(2.,));check('hitch_has_bounded_catchup',manager.get_editor_property('SimulationSteps')<=before+4)
finally:
 for a in cars+lanes+[manager]:actors.destroy_actor(a)
(r/'work/pure_traffic_manager_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'simulation_300_steps_seconds':elapsed,'min_body_gap_cm':gapmin,'scope':'100 vehicle Blueprint VM test. Signals, cross-lane junctions, player/pedestrians and real rendered performance remain pending.'},indent=2));unreal.log('PURE_TRAFFIC_MANAGER_VALIDATION_PASS checks='+str(len(checks)))
