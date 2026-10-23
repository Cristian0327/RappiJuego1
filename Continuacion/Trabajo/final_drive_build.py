import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/fix_drive_doors.py').read_text();exec(s[s.index('# Generated skeletal reductions'):])
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);made=[];checks={}
def ck(n,v):checks[n]=bool(v);assert v,n
try:
 floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(150000,150000,-50));made.append(floor);floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(400,400,1));floor.static_mesh_component.set_collision_profile_name('BlockAll')
 rider=actors.spawn_actor_from_class(unreal.load_class(None,'/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C'),unreal.Vector(170000,150000,100));made.append(rider)
 rider.set_editor_property('ForwardInput',1.);rider.set_editor_property('BikeSpeed',0.);v=rider.call_method('AdvanceDriveSpeed',(.1,3000.));ck('moto_progressive_acceleration',abs(v-22)<.1)
 rider.set_editor_property('BikeSpeed',1000.);v=rider.call_method('AdvanceDriveSpeed',(1.,3000.));ck('moto_top_speed_36_kmh',v<=1000.01)
 rider.set_editor_property('ForwardInput',-1.);v=rider.call_method('AdvanceDriveSpeed',(1.,3000.));ck('moto_brakes_before_reversing',abs(v-350)<.1)
 rider.set_editor_property('SideInput',1.);v=rider.call_method('SteeringAngle',(.1,));ck('moto_turn_rate_limited',0<v<=3.81)
 rider.set_editor_property('SideInput',0.);ck('moto_no_input_no_turn',abs(rider.call_method('SteeringAngle',(.1,)))<.001)
 for i,row in enumerate(json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']):
  car=actors.spawn_actor_from_class(unreal.load_class(None,row['asset']+'.'+row['asset'].rsplit('/',1)[-1]+'_C'),unreal.Vector(180000+i*2000,150000,2));made.append(car);car.call_method('CacheReferencePose');body=car.get_editor_property('Body');ck('original_voxel_lod_'+str(i),body.get_editor_property('forced_lod_model')==1)
  car.call_method('RequestDoors',(1.,1.));car.call_method('UpdateDoorPose',(1.,));car.call_method('RequestDoors',(0.,0.));car.call_method('UpdateDoorPose',(1.,));ck('doors_close_'+str(i),car.get_editor_property('DoorAlphaLeft')<.001 and car.get_editor_property('DoorAlphaRight')<.001)
 (r/'work/drive_doors_validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'total':len(checks),'runtime_cpp':False},indent=2));unreal.log('DRIVE_DOORS_VM_PASS '+str(len(checks)))
finally:
 for a in reversed(made):actors.destroy_actor(a)


exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_comfort_drive_qa.py').read_text(),'ComfortDriveQA','exec'))
