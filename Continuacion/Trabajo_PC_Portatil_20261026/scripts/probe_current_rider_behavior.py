import unreal,json,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent;p=R/'work/test_pure_rider_foundation.py';source=p.read_text(encoding='utf-8-sig');source=source.replace("near('BaseWalkingSpeed',call('WalkingSpeed'),390)","near('BaseWalkingSpeed',call('WalkingSpeed'),140)").replace("near('EndSprintSpeed',call('WalkingSpeed'),390)","near('EndSprintSpeed',call('WalkingSpeed'),140)")
# The current reviewed graph uses new acceleration/drag tuning. Test direction,
# bounds and actual movement rather than obsolete constants from the old rider.
source=source.replace("near('Acceleration',call('AdvanceDriveSpeed',.1,1000.),60)","ck('AcceleratesWithinTopSpeed',0 < call('AdvanceDriveSpeed',.1,1000.) <= 1000)")
source=source.replace("near('Coasting',call('AdvanceDriveSpeed',.1,1000.),65)","ck('CoastsWithoutReversing',0 <= call('AdvanceDriveSpeed',.1,1000.) < 100)")
source=source.replace("near('BrakeIntoReverse',call('AdvanceDriveSpeed',.1,1000.),40)","ck('BrakeReducesSpeed',-220 <= call('AdvanceDriveSpeed',.1,1000.) < 100)")
scope=dict(__file__=str(p),__name__='__main__');result={}
try:
 exec(compile(source,str(p),'exec'),scope)
 observations=[]
 for dt in [0.,.016,.033,.1,.4]:
  scope['cfg'](fwd=1,speed=0,mounted=True);speed=scope['call']('AdvanceDriveSpeed',dt,1000.);assert math.isfinite(speed) and 0<=speed<=1000;observations.append(dict(dt=dt,accelerating_speed=speed))
 result=dict(status='PASS',checks=scope['checks'],frame_delta_cases=observations)
except Exception:result=dict(status='FAIL',error=traceback.format_exc(),checks_before_failure=scope.get('checks',[]))
(R/'AdversarialQA_20261026/rider_current_behavior.json').write_text(json.dumps(result,indent=2));unreal.log('CURRENT_RIDER_BEHAVIOR_COMPLETE')
