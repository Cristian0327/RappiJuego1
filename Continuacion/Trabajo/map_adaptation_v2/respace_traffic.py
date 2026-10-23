from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');data=json.loads((P/'arc_conflicts.json').read_text());unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);laneactors=[aa.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i)).generated_class(),unreal.Vector()) for i in range(7)]
def conflict(li,d,radius):
 length=data['lanes'][li]['length']
 return any((d-e['entry']+radius+100+length)%length<e['span']+2*(radius+100) for e in data['lanes'][li]['events'])
signals=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaServiceSignals_C');services=list(signals.get_editor_property('RoadActors'));service_lanes=list(signals.get_editor_property('ServiceLaneIndices'));occupied=[];radii=[]
for i,(a,li) in enumerate(zip(services,service_lanes)):
 route=list(a.get_editor_property('Route'));idx=int(a.get_editor_property('RouteIndex'));radius=300 if 'Patrol' in a.get_class().get_name() else 180;z=a.get_actor_location().z
 for attempt in range(len(route)*2):
  idx=(idx+7)%len(route);p=route[idx];dist=laneactors[li].call_method('ClosestDistance',(p,))
  if not conflict(li,dist,radius) and all(math.hypot(p.x-q.x,p.y-q.y)>radius+r+100 for q,r in zip(occupied,radii)):break
 else:raise RuntimeError('No service start '+a.get_name())
 a.set_actor_location(unreal.Vector(p.x,p.y,z),False,True);a.set_editor_property('RouteIndex',(idx+1)%len(route));delta=route[(idx+1)%len(route)]-p;a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(delta.y,delta.x)),roll=0),True);occupied.append(p);radii.append(radius)
b=use(TM);c=unreal.get_default_object(b.generated_class());models=list(c.get_editor_property('ModelIndices'));lanes=list(c.get_editor_property('LaneIndices'));meta=json.loads((root/'work/pure_traffic_vehicle_foundation.json').read_text())['models'];distances=[]
for i,li in enumerate(lanes):
 route=laneactors[li];length=route.call_method('RouteLength');d=length*((i*.61803398875)%1);radius=meta[models[i]]['half_length']+80
 for attempt in range(30000):
  p=route.call_method('SamplePosition',(d,))
  if not conflict(li,d,radius) and all(math.hypot(p.x-q.x,p.y-q.y)>radius+r+100 for q,r in zip(occupied,radii)):break
  d=(d+177.7)%length
 else:raise RuntimeError('No traffic slot '+str(i))
 distances.append(d);occupied.append(p);radii.append(radius)
leaders=[]
for i,li in enumerate(lanes):
 group={4:0,5:1}.get(li,li);indices=sorted([j for j,lj in enumerate(lanes) if {4:0,5:1}.get(lj,lj)==group],key=lambda j:distances[j]);leaders.append(indices[(indices.index(i)+1)%len(indices)])
c.set_editor_property('InitialDistances',distances);c.set_editor_property('LeaderIndices',leaders);save(b)
for a in laneactors:aa.destroy_actor(a)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_TRAFFIC_STARTS_OUTSIDE_CONFLICT_ZONES '+str(len(distances)))
