import unreal,json,time,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);manager=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_TrafficManager.BP_TrafficManager_C'),unreal.Vector());cars=[];lanes=[];junctions=[];cells=[];checks={};samples=[];collisions=[]
def pose(a):
 p=a.get_editor_property('NextPosition');yaw=math.radians(a.get_editor_property('NextYaw'));return p.x,p.y,math.cos(yaw),math.sin(yaw),a.get_editor_property('HalfLength'),a.get_editor_property('HalfWidth')
def overlap(a,b):
 ax,ay,afX,afY,al,aw=a;bx,by,bfX,bfY,bl,bw=b;dx=bx-ax;dy=by-ay
 for x,y in [(afX,afY),(-afY,afX),(bfX,bfY),(-bfY,bfX)]:
  ra=al*abs(x*afX+y*afY)+aw*abs(-x*afY+y*afX);rb=bl*abs(x*bfX+y*bfY)+bw*abs(-x*bfY+y*bfX)
  if abs(dx*x+dy*y)>=ra+rb-5:return False
 return True
try:
 manager.call_method('EnsureWorldState');manager.call_method('CreateTrafficCells');manager.call_method('CreateJunctions');manager.call_method('CreateTraffic');cars=list(manager.get_editor_property('Vehicles'));lanes=list(manager.get_editor_property('Lanes'));junctions=list(manager.get_editor_property('Junctions'));state=manager.get_editor_property('WorldState');cells=list(manager.get_editor_property('TrafficCells'));assert len(junctions)==35 and len(cells)==140
 for a in cars:a.call_method('CacheReferencePose');a.call_method('CacheArticulation')
 lengths=[a.get_editor_property('Lane').call_method('RouteLength') for a in cars];previous=[a.get_editor_property('Distance') for a in cars];travel=[0.]*100;idle=[0]*100;maxidle=[0]*100;start=time.perf_counter()
 for step in range(3000):
  state.call_method('ReceiveTick',(.1,));manager.call_method('SimulateFixedStep',(.1,))
  if step%10==9:
   moving=0;poses=[pose(a) for a in cars]
   for i,a in enumerate(cars):
    now=a.get_editor_property('Distance');delta=(now-previous[i]+lengths[i])%lengths[i];travel[i]+=delta;previous[i]=now;idle[i]=idle[i]+1 if delta<1 else 0;maxidle[i]=max(maxidle[i],idle[i]);moving+=delta>1
   for i in range(100):
    for j in range(i+1,100):
     if abs(poses[i][0]-poses[j][0])>2200 or abs(poses[i][1]-poses[j][1])>2200:continue
     if overlap(poses[i],poses[j]):collisions.append({'second':(step+1)/10,'a':i,'b':j})
   samples.append({'second':(step+1)/10,'moving':moving,'reservations':sum(len(j.get_editor_property('Owners')) for j in junctions)})
   if step%300==299:unreal.log('PURE_TRAFFIC_SIGNALS_STRESS_PROGRESS seconds='+str((step+1)/10)+' wall='+str(round(time.perf_counter()-start,2))+' overlaps='+str(len(collisions)))
 elapsed=time.perf_counter()-start;checks={'35_junctions':len(junctions)==35,'all_vehicles_make_progress':min(travel)>1000,'no_indefinite_stop':max(maxidle)<90,'no_body_overlap':not collisions};report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'simulated_seconds':300,'wall_seconds':elapsed,'minimum_travel_cm':min(travel),'max_idle_seconds':max(maxidle),'body_overlap_samples':collisions[:50],'samples':samples,'scope':'Signal/queue deterministic Blueprint simulation; pedestrian avoidance, buses and controlled cars still pending'};(r/'work/pure_traffic_signals_10hz_validation.json').write_text(json.dumps(report,indent=2));unreal.log('PURE_TRAFFIC_SIGNALS_STRESS_RESULT '+json.dumps({k:v for k,v in report.items() if k not in ['samples','body_overlap_samples']}))
finally:
 for a in cars+lanes+junctions+cells+[manager]:actors.destroy_actor(a)

