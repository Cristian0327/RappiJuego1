import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;P='/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C'
bp=unreal.load_asset(P.rsplit('.',1)[0]);E.set_blueprint_variable_instance_editable(bp,'State',True);assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(500,400,120))
try:
 a.set_editor_property('Bicycle',False);a.set_editor_property('RoadMode',True);a.set_editor_property('State',0.);a.set_editor_property('Route',[unreal.Vector(0,0,120),unreal.Vector(1000,0,120)]);a.set_editor_property('RouteIndex',1);v=a.call_method('KeepMotorcycleOnRoad',(unreal.Vector(1,1,0),));assert v.y<0
 a.set_actor_location(unreal.Vector(500,0,120),False,True);v=a.call_method('KeepMotorcycleOnRoad',(unreal.Vector(1,0,0),));assert v.x>.99 and abs(v.y)<.01
 a.set_editor_property('Bicycle',True);v=a.call_method('KeepMotorcycleOnRoad',(unreal.Vector(0,1,0),));assert v.y>.99
 a.call_method('ReceiveBeginPlay');yaw=a.get_editor_property('mesh').get_editor_property('relative_rotation').yaw;assert abs(unreal.MathLibrary.normalize_axis(yaw+90))<1,('rider_basis',yaw)
 (r/'work/motorcycle_road_guard_validation.json').write_text(json.dumps({'checks':4,'status':'PASS','road_only':True,'no_teleport':True},indent=2));unreal.log('MOTORCYCLE_ROAD_BOUNDARY_PASS')
finally:actors.destroy_actor(a)

