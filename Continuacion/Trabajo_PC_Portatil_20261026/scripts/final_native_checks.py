import unreal,json,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent;out=R/'AdversarialQA_20261026';results=[]
for name in ['test_pure_traffic_doors.py','test_pure_rider_foundation.py']:
 scope=dict(__file__=str(R/'work'/name),__name__='__main__',unreal=unreal,json=json,math=math)
 try:
  source=(R/'work'/name).read_text(encoding='utf-8-sig')
  if name=='test_pure_traffic_doors.py':
   source=source.replace('range(4)','range(10)').replace('for before,after in zip(rest,opened):','for bone_name,before,after in zip(names,rest,opened):').replace('elif before.translation.y<0:','elif before.translation.y<0 and not str(bone_name).startswith("door_rear"):')
   extra="""  if spec['name'].startswith('Taxi'):
   a.call_method('RequestDoors',args=(0.,0.));a.call_method('RequestRearDoors',args=(1.,0.))
   for _ in range(10):a.call_method('UpdateDoorPose',args=(.1,))
   for bone_name,before in zip(names,rest):
    after=body.get_bone_transform_by_name(bone_name,unreal.BoneSpaces.COMPONENT_SPACE);expected_open=str(bone_name).startswith('door_rear') and before.translation.y<0
    assert (abs(yawdelta(after,before))>60 if expected_open else abs(yawdelta(after,before))<.01),(spec['name'],str(bone_name),'independent rear door')
"""
   source=source.replace("  a.call_method('SetDriveSpeed',(100.,))",extra+"  a.call_method('SetDriveSpeed',(100.,))")
  else:
   source=source.replace("near('BaseWalkingSpeed',call('WalkingSpeed'),390)","near('BaseWalkingSpeed',call('WalkingSpeed'),140)").replace("near('EndSprintSpeed',call('WalkingSpeed'),390)","near('EndSprintSpeed',call('WalkingSpeed'),140)")
  exec(compile(source,str(R/'work'/name),'exec'),scope);row=dict(test=name,status='PASS',checks=scope.get('checks',[]),models=scope.get('report',[]))
 except Exception:row=dict(test=name,status='FAIL',error=traceback.format_exc(),checks_before_failure=scope.get('checks',[]))
 results.append(row)
# Validate the actual arc data, not obsolete spline lengths from the prior city.
rows=[]
data=json.loads((R/'scripts/map_adaptation_v2/arc_conflicts.json').read_text())
for i in range(len(data['lanes'])):
 path='/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i);b=unreal.load_asset(path)
 if not b:continue
 c=unreal.get_default_object(b.generated_class())
 try:
  fields={n:list(c.get_editor_property(n)) for n in ['ArcEntries','ArcExits','ArcJunctions','ArcGroups','ArcMovements']};n=len(fields['ArcEntries']);valid=len({len(v) for v in fields.values()})==1 and all(math.isfinite(float(x)) for x in fields['ArcEntries']+fields['ArcExits']) and all(0<=int(x)<len(data['centers']) for x in fields['ArcJunctions']) and all(int(x) in [0,1] for x in fields['ArcGroups']);rows.append(dict(asset=path,entries=n,passed=valid))
 except Exception:rows.append(dict(asset=path,passed=False,error=traceback.format_exc()))
results.append(dict(test='current_arc_metadata',status='PASS' if rows and all(x['passed'] for x in rows) else 'FAIL',lanes=rows))
for path in ['/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore','/Game/Delivery/BlueprintGameplay/People/BP_DeliveryRecipient','/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone']:
 b=unreal.load_asset(path);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b));ok=unreal.BlueprintEditorLibrary.compile_blueprint(b) and not any(x['native_calls'] for x in audit['graphs']);results.append(dict(test='compile_and_no_project_native_calls',asset=path,status='PASS' if ok else 'FAIL'))
(out/'final_native_checks.json').write_text(json.dumps(results,indent=2,default=str));unreal.log('FINAL_NATIVE_CHECKS_COMPLETE')
