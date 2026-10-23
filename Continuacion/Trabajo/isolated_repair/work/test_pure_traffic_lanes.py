import unreal,json,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);results=[]
expected=json.loads((r/'work/pure_traffic_lane_foundation.json').read_text())['lanes']
for spec in expected:
 bp=unreal.load_asset(spec['asset']);a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert a
 try:
  spline=a.get_component_by_class(unreal.SplineComponent);length=a.call_method('RouteLength');assert abs(length-spec['length'])<1,(spec,length);assert spline.get_number_of_spline_points()==52;assert spline.is_closed_loop();assert a.get_editor_property('LaneGroup')==spec['lane']
  maxerr=0
  for fraction in [-2,-1.75,-.01,0,.001,.3,.999,1,1.1,2,10.5]:
   distance=length*fraction;actual=a.call_method('SamplePosition',(distance,));reference=spline.get_location_at_distance_along_spline(distance%length,unreal.SplineCoordinateSpace.WORLD);reference.z=a.call_method('AsphaltHeight',(reference,));error=(actual-reference).length();maxerr=max(maxerr,error);assert error<.2,(spec['lane'],fraction,error)
   heading=a.call_method('SampleHeading',(distance,));assert abs(heading.length()-1)<.001
  audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert not any(g['native_calls'] for g in audit['graphs']);results.append({'lane':spec['lane'],'length':length,'samples':12,'max_error_cm':maxerr})
 finally:actors.destroy_actor(a)
(r/'work/pure_traffic_lane_validation.json').write_text(json.dumps({'status':'PASS','lanes':results,'scope':'Fresh-process persisted component and Blueprint VM sampling; signal/following simulation not implemented yet'},indent=2));unreal.log('PURE_TRAFFIC_LANE_VALIDATION_PASS lanes=7 samples=84')
exec(compile((r/'work/audit_pure_dependency_closure.py').read_text(),str(r/'work/audit_pure_dependency_closure.py'),'exec'))

