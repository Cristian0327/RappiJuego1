exec(compile(__import__('pathlib').Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
# Cars used to ignore ordinary vehicles once their headings differed by more
# than 26 degrees. Use their oriented envelopes on curves and at crossings too.
s=(root/'work/build_pure_traffic_spatial_cells.py').read_text();s=s[:s.index("build(g,'ClearanceFromVehicle'")];ns={};exec(compile(s,'OrientedClearanceSetup','exec'),ns);g=ns['g'];b=ns['bp'];g.links=[l for l in g.links if l[2]!='GeneralObstacle']
for n in g.nodes:
 if n['id']=='GeneralObstacle':n['defaults']={'A':'true','B':'true'}
build(b,g,'ClearanceFromVehicle',[dict(name='Other',category='object',object=V),dict(name='ReturnValue',category='real',out=True)],True);save(b)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);stations=sorted([a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaTransmiStation_C'],key=lambda a:a.get_name());target=next(a for a in stations if a.get_name()=='BP_BogotaTransmiStation_C_2');target.set_actor_scale3d(unreal.Vector(.5,1,1));origin=target.get_actor_location();yaw=target.get_actor_rotation().yaw;t=unreal.Vector(math.cos(math.radians(yaw)),math.sin(math.radians(yaw)),0)
# Keep every stop. This one sits on a tight bend, so give it the shorter form
# of the same station model and retain its ramp/door proportions.
adjusted_people=[]
for a in aa.get_all_level_actors():
 cls=a.get_class().get_name();pos=a.get_actor_location();dpos=pos-origin;u=dpos.dot(t);v=dpos.x*(-t.y)+dpos.y*t.x
 if 'StationPassenger' in cls:
  try:sid=a.get_editor_property('StationId')
  except:sid=-1
  if sid==2:a.set_actor_location(pos-t*(u*.5),False,True);adjusted_people.append(a.get_name())
 if cls=='BP_CrosswalkCitizen_C' and abs(u)<4000 and abs(v)<2200:
  try:route=list(a.get_editor_property('Route'))
  except:continue
  # Only the station access route contains the platform-height waypoint.
  if not any(abs((q-origin).dot(t)+1350)<120 and 70<q.z<120 for q in route):continue
  updated=[]
  for q in route:
   x=(q-origin).dot(t)
   if abs(x+1350)<120 or abs(x+2400)<120:q=q-t*(x*.5)
   updated.append(q)
  a.set_editor_property('Route',updated)
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;b=use('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_6');curve=next(lib.get_object_for_blueprint(lib.get_data(h),b) for h in sub.k2_gather_subobject_data_for_blueprint(b) if str(lib.get_variable_name(lib.get_data(h)))=='Route');original=[curve.get_location_at_spline_point(i,unreal.SplineCoordinateSpace.LOCAL) for i in range(curve.get_number_of_spline_points())];N=len(original);route=[]
for i,p in enumerate(original):
 direction=original[(i+1)%N]-original[(i-1)%N];length=max(math.hypot(direction.x,direction.y),1);right=unreal.Vector(-direction.y/length,direction.x/length,0);shift=0
 for st in stations:
  at=st.get_actor_location();distance=math.hypot(p.x-at.x,p.y-at.y);weight=max(0,min(1,(6500-distance)/2500));shift=max(shift,weight*(250 if st==target else 120))
 route.append(p+right*shift)
curve.set_spline_points(route,unreal.SplineCoordinateSpace.LOCAL,False)
for i in range(N):curve.set_spline_point_type(i,unreal.SplinePointType.LINEAR,False)
curve.set_closed_loop(True,True);assert E.compile_blueprint(b);save(b)
# Stop coordinates track the new bus lane; passengers and doors still use the
# same seven station identifiers.
newstops=[]
b=use(V);c=unreal.get_default_object(b.generated_class());oldstops=list(c.get_editor_property('TransitStopPositions'))
for p in oldstops:newstops.append(min(route,key=lambda q:(q-p).length_squared()))
c.set_editor_property('TransitStopPositions',newstops);save(b);b=use('/Game/World/BlueprintWorld/Traffic/BP_Traffic_TransMilenio');unreal.get_default_object(b.generated_class()).set_editor_property('TransitStopPositions',newstops);save(b)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();(P/'traffic_isolated_report.json').write_text(json.dumps(dict(stations=len(stations),compact_station=target.get_name(),compact_scale_x=.5,station_passengers_adjusted=adjusted_people,bus_stop_count=len(newstops),moving_vehicles_use_oriented_clearance=True),indent=2));unreal.log('TRAFFIC_ISOLATED_REPAIR_READY')
