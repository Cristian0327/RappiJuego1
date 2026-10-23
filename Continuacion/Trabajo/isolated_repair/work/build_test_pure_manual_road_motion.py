import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
exec(compile((r/'work/build_pure_manual_road_motion.py').read_text(encoding='utf-8-sig'),'ManualRoadMotion','exec'))
g=d.Graph();g.setter('Control','PlayerControlled','entry','Enabled');g.exec('entry','Control');g.setter('Parking','Parked','entry','Enabled');g.exec('Control','Parking');g.setter('Stopped','Speed',value='0');g.exec('Parking','Stopped');g.call('Close','RequestDoors',P,Left='0',Right='0');g.exec('Stopped','Close');g.exec('Close','result');build(g,'SetManualRoadControl',[{'name':'Enabled','category':'bool'}]);assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);created=[];checks={}
try:
 floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(150000,150000,-50));created.append(floor);floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(400,400,1));car=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/World/BlueprintWorld/Traffic/BP_Traffic_Private.BP_Traffic_Private_C'),unreal.Vector(150000,150000,2));created.append(car);car.call_method('CacheReferencePose');car.call_method('CacheArticulation');car.call_method('SetManualRoadControl',(True,));start=car.get_actor_location()
 for i in range(60):car.call_method('UpdateManualRoadMotion',(1/60,1.,0.))
 forward=car.get_actor_location();unreal.log('MANUAL_PROBE '+str(car.get_editor_property('ManualProbeStage'))+' '+str(car.get_editor_property('PlayerControlled'))+' speed='+str(car.get_editor_property('Speed'))+' position='+str(forward));checks['accelerates_forward']=forward.x-start.x>200 and abs(forward.y-start.y)<1
 for i in range(180):car.call_method('UpdateManualRoadMotion',(1/60,-1.,0.))
 checks['reverse_works']=car.get_editor_property('Speed')<0
 car.call_method('SetManualRoadControl',(True,));before=car.get_actor_rotation().yaw
 for i in range(90):car.call_method('UpdateManualRoadMotion',(1/60,1.,.6))
 checks['steering_changes_heading']=abs(car.get_actor_rotation().yaw-before)>10
 car.call_method('SetManualRoadControl',(False,));stopped=car.get_actor_location();car.call_method('UpdateManualRoadMotion',(.1,1.,1.));checks['not_controlled_no_motion']=car.get_actor_location().distance(stopped)<.01
 checks['ground_height_stable']=abs(car.get_actor_location().z-2)<1
 report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'scope':'Blueprint VM driving only; player mount/input integration not yet implemented'};(r/'work/pure_manual_road_motion_validation.json').write_text(json.dumps(report,indent=2));unreal.log('PURE_MANUAL_ROAD_VM_RESULT '+json.dumps(report))
finally:
 for a in created:
  if a:actors.destroy_actor(a)


