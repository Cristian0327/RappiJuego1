import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);allactors=[];checks={}
def check(name,value):
 checks[name]=bool(value);assert value,name
try:
 lane=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_0.BP_TrafficLane_0_C'),unreal.Vector());allactors.append(lane);length=lane.call_method('RouteLength')
 car=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_Private.BP_Traffic_Private_C'),unreal.Vector());allactors.append(car);car.call_method('InitializeRoute',(lane,1000.));car.call_method('CacheReferencePose');initial=car.get_actor_location();expected=lane.call_method('SamplePosition',(1000.,));check('starts_on_assigned_lane',(initial-expected).length()<.1)
 car.call_method('SimulateMovement',(1/30,1000000.,975.));check('acceleration_240_cm_s2',abs(car.get_editor_property('Speed')-8)<.001);check('single_step_distance_not_reevaluated',abs(car.get_editor_property('Distance')-1000-8/30)<.01)
 prev=car.get_editor_property('PreviousPosition');nxt=car.get_editor_property('NextPosition');car.call_method('RenderMovement',(.5,));check('render_interpolates_half_step',(car.get_actor_location()-(prev+nxt)*.5).length()<.02)
 refdist=car.get_editor_property('Distance');refspeed=8.
 for i in range(299):
  refspeed=min(975.,refspeed+240/30);refdist=(refdist+refspeed/30)%length;car.call_method('SimulateMovement',(1/30,1000000.,975.))
 check('matches_300_step_reference',abs(car.get_editor_property('Distance')-refdist)<.15 and abs(car.get_editor_property('Speed')-refspeed)<.01)
 before=car.get_editor_property('Distance');car.call_method('SimulateMovement',(0.,1000000.,975.));check('zero_dt_does_not_reset_or_move',abs(car.get_editor_property('Speed')-975.)<.01 and abs(car.get_editor_property('Distance')-before)<.01)
 car.call_method('SimulateMovement',(1/30,0.,975.));check('obstacle_hard_limit_no_penetration',abs(car.get_editor_property('Distance')-before)<.01 and abs(car.get_editor_property('Speed'))<.01)
 car.call_method('SimulateMovement',(1/30,-200.,975.));check('negative_gap_does_not_reverse',abs(car.get_editor_property('Distance')-before)<.01 and car.get_editor_property('Speed')>=0)
 car.call_method('InitializeRoute',(lane,length-.1));car.call_method('SetDriveSpeed',(975.,));car.call_method('SimulateMovement',(1/30,1000000.,975.));check('wraps_circuit_without_jump',0<=car.get_editor_property('Distance')<40);car.call_method('RenderMovement',(1.,));sample=lane.call_method('SamplePosition',(car.get_editor_property('Distance'),));check('wrapped_render_matches_route',(car.get_actor_location()-sample).length()<.1)
 car.call_method('SetDriveSpeed',(0.,));car.call_method('RequestDoors',(1.,0.));car.call_method('UpdateDoorPose',(.1,));before=car.get_editor_property('Distance');car.call_method('SimulateMovement',(1/30,1000000.,975.));check('does_not_accelerate_with_open_door',abs(car.get_editor_property('Speed'))<.01 and abs(car.get_editor_property('Distance')-before)<.01)
 car.call_method('RequestDoors',(0.,0.));car.call_method('UpdateDoorPose',(.1,));car.call_method('SimulateMovement',(1/30,1000000.,975.));check('resumes_after_door_closed',car.get_editor_property('Speed')>0)
 colors=[]
 for i in range(12):
  car.call_method('ApplyPaintIndex',(i,));mat=car.get_editor_property('BodyMaterial');color=mat.call_method('K2_GetVectorParameterValue',(unreal.Name('BodyPaint'),));colors.append(tuple(round(getattr(color,x),4) for x in ['r','g','b']))
 check('twelve_distinct_body_colors',len(set(colors))==12)
 car.call_method('SetHeadlights',(True,));check('headlights_show_actual_spotlights',all(x.get_editor_property('visible') for x in car.get_components_by_class(unreal.SpotLightComponent)));car.call_method('SetHeadlights',(False,));check('headlights_turn_off',not any(x.get_editor_property('visible') for x in car.get_components_by_class(unreal.SpotLightComponent)))
finally:
 for a in reversed(allactors):actors.destroy_actor(a)
(r/'work/pure_traffic_movement_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'scope':'Blueprint VM deterministic simulation/interpolation/art; full city manager/signals/pedestrians still pending'},indent=2));unreal.log('PURE_TRAFFIC_MOVEMENT_VALIDATION_PASS checks='+str(len(checks)))

