from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'RepairHelpers','exec'))
# Remove inherited square-grid traffic timing and sidewalk overtaking from service motorcycles.
b=use('/Game/Traffic/Services/BP_VoxelRoadVehicle');d.bp=b;s=(root/'work/build_road_vehicle_blueprint.py').read_text();start=s.index("g=d.Graph()\nfor n in ['Route','RouteIndex'");end=s.index("build(g,'ReceiveTick')",start);body=s[start:end]
ns=dict(r=root,d=d,E=E,M=M,A=A,SYS=K,GAME=G,ARR=AL,POSE='/Script/Engine.PoseableMeshComponent',bp=b);exec(compile(body,'ServiceRoadMotion','exec'),ns);g=ns['g']
# Use only the authored lane, brake for obstacles instead of swerving onto pavements.
for link in list(g.links):
 if link[2:] in [['Drive','WorldDirection'],['Drive','ScaleValue'],['SignalStop','A'],['SignalStop','B']]:g.links.remove(link)
g.link('Direction','ReturnValue','Drive','WorldDirection');g.link('Blocked','ReturnValue','Throttle','bPickA') if not any(l[2:] == ['Throttle','bPickA'] for l in g.links) else None
for l in g.links:
 if l[2:] == ['Throttle','bPickA']:l[0]='Blocked';l[1]='ReturnValue'
g.link('Throttle','ReturnValue','Drive','ScaleValue')
for n in g.nodes:
 if n['id']=='SignalStop':n['defaults']={'A':'false','B':'false'}
# A blocking hit always yields, including parked bikes.
for l in g.links:
 if l[2:] == ['Blocked','A']:l[0]='Trace';l[1]='ReturnValue'
build(b,g,'ReceiveTick');save(b)
# Apply identical physical crossing clearance to every road-going service and lifecycle rider.
b=use('/Game/World/BogotaUrban/BP_BogotaServiceSignals');d.bp=b;g=d.Graph()
for n in ['RoadActors','RoadSpeeds','Manager']:g.get(n)
g.call('Valid','IsValid',K);g.link('Manager','Manager','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.call('Find','GetActorOfClass',G,ActorClass=TM);g.exec('Ready','Find','else');g.node('Cast','cast',type=TM);g.link('Find','ReturnValue','Cast','Object');g.setter('Cache','Manager','Cast','AsBP Traffic Manager');g.exec('Find','Cache');g.exec('Cache','result');g.node('Each','foreach');g.link('RoadActors','RoadActors','Each','Array');g.link('Ready','then','Each','Exec');g.call('At','K2_GetActorLocation',A);g.link('Each','Array Element','At','self');g.call('Forward','GetActorForwardVector',A);g.link('Each','Array Element','Forward','self');g.call('Limit','CrossingClearanceAt',TM,VehicleHalfLength='140');g.link('Manager','Manager','Limit','self');g.link('At','ReturnValue','Limit','Position');g.link('Forward','ReturnValue','Limit','Direction');g.link('Each','LoopBody','Limit','execute');g.call('Base','Array_Get',AL);g.link('RoadSpeeds','RoadSpeeds','Base','TargetArray');g.link('Each','Array Index','Base','Index');op(g,'Headway','Divide_DoubleDouble',('Limit','ReturnValue'),B='1.4');op(g,'Speed','FMin',('Headway','ReturnValue'),('Base','Item'));g.node('Character','cast',type='/Script/Engine.Character');g.link('Each','Array Element','Character','Object');field(g,'Move','CharacterMovement',('Character','AsCharacter'),'/Script/Engine.Character');g.node('SpeedSet','setfield',owner=CM,var='MaxWalkSpeed');g.link('Move','CharacterMovement','SpeedSet','self');g.link('Speed','ReturnValue','SpeedSet','MaxWalkSpeed');g.exec('Limit','SpeedSet');op(g,'Stop','Less_DoubleDouble',('Limit','ReturnValue'),B='25');g.branch('Brake','Stop');g.exec('SpeedSet','Brake');g.call('Halt','StopMovementImmediately','/Script/Engine.MovementComponent');g.link('Move','CharacterMovement','Halt','self');g.exec('Brake','Halt');g.link('Each','Completed','result','execute');build(b,g,'ReceiveTick');save(b)
# One globally distributed spawn index; never restart it for another motorcycle subtype.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);services=[];speeds=[];occupied=[];records=[]
for a in actors.get_all_level_actors():
 if a.get_class().get_name() not in ['BP_CivilMotorcycle_C','BP_PoliceMotorcycle_C','BP_PoliceRoadPatrol_C','BP_TwoWheelerCitizen_C']:continue
 route=list(a.get_editor_property('Route'));i=len(services);idx=(i*83+31)%len(route)
 for attempt in range(len(route)):
  q=route[idx]
  if all(math.hypot(q.x-p.x,q.y-p.y)>550 for p in occupied):break
  idx=(idx+7)%len(route)
 occupied.append(q);z=154 if 'RoadPatrol' in a.get_class().get_name() else 102 if 'TwoWheeler' in a.get_class().get_name() else 134;a.set_actor_location(unreal.Vector(q.x,q.y,z),False,True);a.set_editor_property('RouteIndex',(idx+1)%len(route));target=route[(idx+1)%len(route)];yaw=math.degrees(math.atan2(target.y-q.y,target.x-q.x));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),True);move=a.get_editor_property('character_movement');move.set_editor_property('use_rvo_avoidance',False);move.set_editor_property('max_step_height',5.);move.set_editor_property('braking_deceleration_walking',2000.);speed=420. if 'TwoWheeler' in a.get_class().get_name() else min(float(a.get_editor_property('RoadSpeed')),650.);services.append(a);speeds.append(speed);records.append(dict(name=a.get_name(),position=[q.x,q.y,z],route_index=idx))
for a in actors.get_all_level_actors():
 if a.get_class().get_name()=='BP_BogotaServiceSignals_C':a.set_editor_property('RoadActors',services);a.set_editor_property('RoadSpeeds',speeds)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();(P/'road_agent_distribution.json').write_text(json.dumps(records,indent=2));unreal.log('ROAD_AGENTS_SHARED_SIGNALS_AND_UNIQUE_SPAWNS '+str(len(services)))
# Export authored pedestrian routes for actual polygon safety validation.
rows=[]
for a in actors.get_all_level_actors():
 try:
  route=a.get_editor_property('Route')
  if len(route)>1 and not a in services:rows.append(dict(name=a.get_name(),cls=a.get_class().get_name(),route=[list(p.to_tuple()) for p in route]))
 except:pass
(P/'pedestrian_routes.json').write_text(json.dumps(rows))

