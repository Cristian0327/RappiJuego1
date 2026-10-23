exec(compile(__import__('pathlib').Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
def components(b):
 return {str(lib.get_variable_name(lib.get_data(h))):lib.get_object_for_blueprint(lib.get_data(h),b) for h in sub.k2_gather_subobject_data_for_blueprint(b)}
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
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_NEW_PAVEMENT_LANE_HEIGHTS '+json.dumps(height_report))
