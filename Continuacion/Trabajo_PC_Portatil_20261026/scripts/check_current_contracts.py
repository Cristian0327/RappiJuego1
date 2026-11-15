import unreal,json,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent;out=R/'AdversarialQA_20261026';result={'map':[],'doors':[],'rider':{},'failures':[]}
phone=unreal.get_default_object(unreal.load_class(None,'/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.WBP_BlueprintPhone_C'))
for name,p,center,full,expect in [('full_center',(0,0,0),(0,0,0),True,(.5,.5)),('full_northwest',(42000,-52000,0),(0,0,0),True,(0,0)),('full_southeast',(-42000,52000,0),(0,0,0),True,(1,1)),('mini_center',(1000,-2200,90),(1000,-2200,100),False,(.5,.5)),('mini_northwest',(9000,-7700,90),(1000,-2200,100),False,(0,0))]:
 v=phone.call_method('MapNormalizedPoint',args=(unreal.Vector(*p),unreal.Vector(*center),full));ok=math.isclose(v.x,expect[0],abs_tol=.0001) and math.isclose(v.y,expect[1],abs_tol=.0001);result['map'].append(dict(case=name,actual=[v.x,v.y],expected=expect,passed=ok))
 if not ok:result['failures'].append(name)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
for spec in json.loads((R/'work/pure_traffic_vehicle_foundation.json').read_text())['models']:
 a=None
 try:
  a=actors.spawn_actor_from_class(unreal.load_class(None,spec['asset']+'.'+spec['asset'].rsplit('/',1)[-1]+'_C'),unreal.Vector());body=a.get_component_by_class(unreal.PoseableMeshComponent);names=list(a.get_editor_property('DoorNames'));a.call_method('CacheReferencePose');rest=list(a.get_editor_property('DoorRest'));initial_speed=float(a.get_editor_property('Speed'));a.call_method('SetDriveSpeed',args=(0.,));a.call_method('RequestDoors',args=(1.,0.))
  for _ in range(10):a.call_method('UpdateDoorPose',args=(.1,))
  data=[]
  for name,before in zip(names,rest):
   after=body.get_bone_transform_by_name(name,unreal.BoneSpaces.COMPONENT_SPACE);data.append(dict(bone=str(name),side_y=before.translation.y,yaw=unreal.MathLibrary.normalized_delta_rotator(after.rotation.rotator(),before.rotation.rotator()).yaw,translation=(before.translation-after.translation).length()))
  moved=any(abs(d['yaw'])>10 or d['translation']>10 for d in data);result['doors'].append(dict(model=spec['name'],initial_speed=initial_speed,passed=moved,bones=data))
  if not moved:result['failures'].append('Doors_'+spec['name'])
 except Exception:result['failures'].append(spec['name']+':'+traceback.format_exc())
 finally:
  if a:actors.destroy_actor(a)
(out/'current_contracts.json').write_text(json.dumps(result,indent=2));unreal.log('CURRENT_CONTRACTS_COMPLETE')
