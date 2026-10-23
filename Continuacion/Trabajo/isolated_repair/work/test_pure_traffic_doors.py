import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');d.bp=bp;g=d.Graph();g.setter('SpeedValue','Speed','entry','Value');g.exec('entry','SpeedValue');g.exec('SpeedValue','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'SetDriveSpeed',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'Value','category':'real'}]}));assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);report=[];models=json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']
def yawdelta(a,b):return unreal.MathLibrary.normalized_delta_rotator(a.rotation.rotator(),b.rotation.rotator()).yaw
for spec in models:
 bp=unreal.load_asset(spec['asset']);a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());assert a
 try:
  body=a.get_component_by_class(unreal.PoseableMeshComponent);assert body;assert abs(body.get_editor_property('relative_scale3d').x-spec['scale'])<.001
  names=list(a.get_editor_property('DoorNames'));wheels=list(a.get_editor_property('WheelNames'));assert all(body.get_bone_index(n)>=0 for n in names+wheels),(spec['name'],names,wheels)
  a.call_method('CacheReferencePose');rest=list(a.get_editor_property('DoorRest'));assert len(rest)==len(names);wheelrest=[body.get_bone_transform_by_name(n,unreal.BoneSpaces.COMPONENT_SPACE) for n in wheels]
  a.call_method('RequestDoors',(1.,0.))
  for _ in range(4):a.call_method('UpdateDoorPose',(.1,))
  bus=spec['name']=='TransMilenio';opened=[body.get_bone_transform_by_name(n,unreal.BoneSpaces.COMPONENT_SPACE) for n in names];moved=0
  for before,after in zip(rest,opened):
   assert (before.scale3d-after.scale3d).length()<.001
   if bus:assert (before.translation-after.translation).length()>45;moved+=1
   elif before.translation.y<0:assert abs(yawdelta(after,before))>60;assert (before.translation-after.translation).length()<.001;moved+=1
   else:assert abs(yawdelta(after,before))<.01
  assert moved>0
  for before,n in zip(wheelrest,wheels):
   after=body.get_bone_transform_by_name(n,unreal.BoneSpaces.COMPONENT_SPACE);assert (before.translation-after.translation).length()<.001;assert abs(yawdelta(after,before))<.01
  a.call_method('SetDriveSpeed',(100.,))
  for _ in range(4):a.call_method('UpdateDoorPose',(.1,))
  for before,n in zip(rest,names):
   after=body.get_bone_transform_by_name(n,unreal.BoneSpaces.COMPONENT_SPACE);assert (before.translation-after.translation).length()<.001;assert abs(yawdelta(after,before))<.01
  lights=a.get_components_by_class(unreal.SpotLightComponent);assert len(lights)==2;assert all(l.get_editor_property('intensity')>0 for l in lights)
  report.append({'model':spec['name'],'doors':len(names),'wheels':len(wheels),'scale':spec['scale'],'checks':'hinge/slide, opposite side, no panel scaling, unaffected wheels, movement safety close, two real headlights'})
 finally:actors.destroy_actor(a)
(r/'work/pure_traffic_doors_validation.json').write_text(json.dumps({'status':'PASS','models':report,'scope':'Actual Blueprint VM, all23 models; not yet integrated into main traffic'},indent=2));unreal.log('PURE_TRAFFIC_DOORS_VALIDATION_PASS models=23')

