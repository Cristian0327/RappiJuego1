exec(compile(__import__('pathlib').Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
def components(b):
 return {str(lib.get_variable_name(lib.get_data(h))):lib.get_object_for_blueprint(lib.get_data(h),b) for h in sub.k2_gather_subobject_data_for_blueprint(b)}
# The new roads already carry their physical height in their spline. The old
# Manhattan-grid height function was raising cars at unrelated coordinates.
b=use('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane');g=d.Graph();g.get('Route');g.call('Sample','GetLocationAtDistanceAlongSpline','/Script/Engine.SplineComponent',CoordinateSpace='World');g.link('Route','Route','Sample','self');g.link('entry','Distance','Sample','Distance');g.link('Sample','ReturnValue','result','ReturnValue');g.exec('entry','result');build(b,g,'SamplePosition',[dict(name='Distance',category='real'),dict(name='ReturnValue',category='struct',object='/Script/CoreUObject.Vector',out=True)],True);save(b)
# Set visual contact from each model's actual bounds, preserving model scale.
report=[]
for path in EL.list_assets('/Game/World/BlueprintWorld/Traffic',recursive=False,include_folder=False):
 if '/BP_Traffic_' not in path:continue
 b=use(path);parts=components(b);body=parts.get('Body')
 if not body:continue
 mesh=body.get_editor_property('skeletal_mesh')
 if not mesh:continue
 bounds=mesh.get_bounds();scale=body.get_editor_property('relative_scale3d');bottom=(bounds.origin.z-bounds.box_extent.z)*scale.z;at=body.get_editor_property('relative_location');at.z=-bottom;body.set_editor_property('relative_location',at);assert E.compile_blueprint(b);save(b);report.append(dict(asset=path,bottom=bottom,offset=at.z))
# Route height is baked from the road mesh, rather than sampled from traffic,
# station roofs, pedestrians, or the obsolete city's height formula.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();height_report=[]
b=use('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane');g=d.Graph()
for tag,z in [('Start',75),('End',-60)]:op(g,tag,'Add_VectorVector',('entry','Point'),B='(X=0,Y=0,Z='+str(z)+')')
g.call('Trace','LineTraceSingle',K,TraceChannel='TraceTypeQuery1',bTraceComplex='true',DrawDebugType='None',bIgnoreSelf='true');g.link('Start','ReturnValue','Trace','Start');g.link('End','ReturnValue','Trace','End');g.exec('entry','Trace');g.call('Hit','BreakHitResult',G);g.link('Trace','OutHit','Hit','Hit');g.call('XYZ','BreakVector',M);g.link('Hit','ImpactPoint','XYZ','InVec');g.call('Height','SelectFloat',M,B='13.5');g.link('XYZ','Z','Height','A');g.link('Trace','ReturnValue','Height','bPickA');g.link('Height','ReturnValue','result','ReturnValue');g.exec('Trace','result');build(b,g,'MeasuredGround',[dict(name='Point',category='struct',object='/Script/CoreUObject.Vector'),dict(name='ReturnValue',category='real',out=True)]);save(b);probe=aa.spawn_actor_from_class(b.generated_class(),unreal.Vector())
for i in range(7):
 b=use('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i));curve=components(b)['Route'];points=[];heights=[]
 for j in range(curve.get_number_of_spline_points()):
  p=curve.get_location_at_spline_point(j,unreal.SplineCoordinateSpace.LOCAL)
  p.z=probe.call_method('MeasuredGround',(unreal.Vector(p.x,p.y,0),))+.5
  points.append(p);heights.append(p.z)
 curve.set_spline_points(points,unreal.SplineCoordinateSpace.LOCAL,False)
 for j in range(len(points)):curve.set_spline_point_type(j,unreal.SplinePointType.LINEAR,False)
 curve.set_closed_loop(True,True);assert E.compile_blueprint(b);save(b);height_report.append(dict(lane=i,min=min(heights),max=max(heights),points=len(points)))
aa.destroy_actor(probe)
# Police body faces -X in the source asset. Rotate its visual, leaving its lane,
# obstacle checks, steering, and headlights in the direction of travel.
b=use('/Game/Traffic/Services/BP_VoxelRoadVehicle');addvar(b,'VisualYaw',real);assert E.compile_blueprint(b)
s=(root/'work/build_road_vehicle_blueprint.py').read_text();start=s.index("d.bp=bp;g=d.Graph();g.variables=");end=s.index("build(g,'ReceiveBeginPlay')",start);ns=dict(bp=b,d=d,E=E,M=M,A=A,SYS=K,GAME=G,ARR=AL,POSE='/Script/Engine.PoseableMeshComponent',SKIN='/Script/Engine.SkinnedMeshComponent',SKEL='/Script/Engine.SkeletalMeshComponent');ns['build']=lambda *a:None;exec(compile(s[start:end],'RoadVisualSetup','exec'),ns);g=ns['g'];g.get('VisualYaw');g.call('VisualRotation','MakeRotator',M);g.link('VisualYaw','VisualYaw','VisualRotation','Yaw');g.link('VisualRotation','ReturnValue','BodyTransform','Rotation');build(b,g,'ReceiveBeginPlay');save(b)
b=use('/Game/Traffic/Services/BP_PoliceRoadPatrol');unreal.get_default_object(b.generated_class()).set_editor_property('VisualYaw',180.);save(b)
# Bicycles can negotiate ordinary curbs; cars and service motorcycles retain
# their separate movement limits.
b=use(R);c=unreal.get_default_object(b.generated_class());move=c.get_editor_property('character_movement');move.set_editor_property('max_step_height',55.);move.set_editor_property('max_simulation_time_step',.016667);move.set_editor_property('max_simulation_iterations',12);move.set_editor_property('perch_radius_threshold',0.);move.set_editor_property('can_walk_off_ledges',True)
parts=components(b);bike=parts['Bicycle'];at=bike.get_editor_property('relative_location');at.z=-93.;bike.set_editor_property('relative_location',at);assert E.compile_blueprint(b);save(b)
(P/'contact_repair.json').write_text(json.dumps(dict(models=report,lanes=height_report,police_visual_yaw=180,bicycle_step=55),indent=2));unreal.log('CONTACT_REPAIR_DONE')
