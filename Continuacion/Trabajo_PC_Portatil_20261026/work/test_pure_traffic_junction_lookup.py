import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);allactors=[];manager=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_TrafficManager.BP_TrafficManager_C'),unreal.Vector());allactors.append(manager);manager.call_method('CreateJunctions');junctions=list(manager.get_editor_property('Junctions'));allactors+=junctions;car=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_Private.BP_Traffic_Private_C'),unreal.Vector());allactors.append(car);count=0
try:
 for laneidx in range(7):
  lane=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(laneidx)+'.BP_TrafficLane_'+str(laneidx)+'_C'),unreal.Vector());allactors.append(lane);length=lane.call_method('RouteLength')
  for d in range(0,int(length),500):
   car.call_method('InitializeRoute',(lane,float(d)));p=car.get_editor_property('NextPosition');angle=math.radians(car.get_editor_property('NextYaw'));dx=math.cos(angle);dy=math.sin(angle);expected=None;best=6000
   if abs(dx)>.9 or abs(dy)>.9:
    for j in junctions:
     c=j.get_actor_location();x=c.x-p.x;y=c.y-p.y;ahead=x*dx+y*dy;side=abs(x*dy-y*dx)
     if side<900 and 0<=ahead<best:expected=j;best=ahead
   actual=manager.call_method('FindUpcomingJunction',(car,));assert actual==expected,(laneidx,d,p,angle,actual,expected);count+=1
finally:
 for a in reversed(allactors):actors.destroy_actor(a)
(r/'work/pure_traffic_junction_lookup_validation.json').write_text(json.dumps({'status':'PASS','samples':count,'scope':'Three spatial candidates exactly match previous35-junction scan on all7 routes, every500cm'},indent=2));unreal.log('PURE_TRAFFIC_JUNCTION_LOOKUP_VALIDATION_PASS samples='+str(count))
