import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);spawned=[];checks={}
def spawn(path,where=unreal.Vector()):
 a=actors.spawn_actor_from_class(unreal.load_class(None,path),where);assert a;spawned.append(a);return a
def check(n,v):checks[n]=bool(v);assert v,n
def lane(points):
 a=spawn('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane.BP_TrafficLane_C');s=a.get_component_by_class(unreal.SplineComponent);s.set_spline_points([unreal.Vector(x,y,35) for x,y in points],unreal.SplineCoordinateSpace.LOCAL,False)
 for i in range(len(points)):s.set_spline_point_type(i,unreal.SplinePointType.LINEAR,False)
 s.set_closed_loop(True,True);return a
def closest_distance(l,x,y):
 s=l.get_component_by_class(unreal.SplineComponent);points=[s.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.WORLD) for i in range(s.get_number_of_spline_points())];best=(1e30,0);distance=0
 for a,b in zip(points,points[1:]+points[:1]):
  dx=b.x-a.x;dy=b.y-a.y;length=math.hypot(dx,dy);t=max(0,min(1,((x-a.x)*dx+(y-a.y)*dy)/(length*length)));err=(a.x+t*dx-x)**2+(a.y+t*dy-y)**2
  if err<best[0]:best=(err,distance+t*length)
  distance+=length
 return best[1]
def car(l,x,y):
 a=spawn('/Game/World/BlueprintWorld/Traffic/BP_Traffic_Private.BP_Traffic_Private_C');a.call_method('InitializeRoute',(l,closest_distance(l,x,y)));return a
try:
 probe=spawn('/Game/World/BlueprintWorld/Traffic/BP_TrafficJunction.BP_TrafficJunction_C',unreal.Vector(12000,11000,0));check('junction_preserves_authored_position',(probe.get_actor_location()-unreal.Vector(12000,11000,0)).length()<.01)
 j=spawn('/Game/World/BlueprintWorld/Traffic/BP_TrafficJunction.BP_TrafficJunction_C');j.call_method('ConfigureJunction');check('central_avenue_band_1925',abs(j.get_editor_property('EastHalfBand')-1925)<.01)
 north=lane([(-270,-15000),(-270,15000),(-15000,15000),(-15000,-15000)]);south=lane([(270,15000),(270,-15000),(15000,-15000),(15000,15000)]);east=lane([(-15000,-270),(15000,-270),(15000,15000),(-15000,15000)])
 hl=260.96;a=car(north,-270,-1925-hl);b=car(south,270,1925+hl);cross=car(east,-1550-hl,-270);check('approach_is_straight',a.call_method('RemainsStraight',(5000.,)))
 check('red_stops_at_line',j.call_method('RequestPass',(a,False,True))<.1 and len(j.get_editor_property('Owners'))==0)
 check('blocked_exit_prevents_entry',j.call_method('RequestPass',(a,True,False))<.1 and len(j.get_editor_property('Owners'))==0)
 check('green_admits_and_reserves',j.call_method('RequestPass',(a,True,True))>1e7 and list(j.get_editor_property('Owners'))==[a])
 check('admitted_vehicle_keeps_right_of_way_after_red',j.call_method('RequestPass',(a,False,False))>1e7)
 check('opposing_straight_lanes_can_pass_together',j.call_method('RequestPass',(b,True,True))>1e7 and len(j.get_editor_property('Owners'))==2)
 check('perpendicular_traffic_waits',j.call_method('RequestPass',(cross,True,True))<.1 and len(j.get_editor_property('Owners'))==2)
 # Front clear is insufficient: retain until rear has passed the full crossing.
 a.call_method('InitializeRoute',(north,closest_distance(north,-270,1925+hl-5)));j.call_method('ReleaseClearedOwners');check('rear_not_clear_retains_reservation',a in list(j.get_editor_property('Owners')))
 a.call_method('InitializeRoute',(north,closest_distance(north,-270,1925+hl+10)));j.call_method('ReleaseClearedOwners');check('rear_clear_releases_reservation',a not in list(j.get_editor_property('Owners')) and b in list(j.get_editor_property('Owners')))
 b.call_method('InitializeRoute',(south,closest_distance(south,270,-1925-hl-10)));j.call_method('ReleaseClearedOwners');check('all_cleared_releases_crossing',len(j.get_editor_property('Owners'))==0)
 check('waiting_cross_traffic_can_then_enter',j.call_method('RequestPass',(cross,True,True))>1e7)
finally:
 for a in reversed(spawned):actors.destroy_actor(a)
(r/'work/pure_traffic_junction_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'scope':'Blueprint VM junction admission and rear clearance; city manager integration and congestion stress still pending'},indent=2));unreal.log('PURE_TRAFFIC_JUNCTION_VALIDATION_PASS checks='+str(len(checks)))
