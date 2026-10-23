from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');import random
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);b=unreal.load_asset(V.split('.')[0]);
for name in ['PreviousPosition','PreviousYaw','HalfLength','HalfWidth']:E.set_blueprint_variable_instance_editable(b,name,True)
assert E.compile_blueprint(b);cls=b.generated_class();rows=[];random.seed(55)
for index in range(60):
 yaw=random.uniform(-180,180);other_yaw=random.uniform(-180,180);p=unreal.Vector(0,0,4);q=unreal.Vector(random.uniform(-1800,1800),random.uniform(-1800,1800),4);hl=random.uniform(220,920);hw=random.uniform(95,140);ol=random.uniform(220,920);ow=random.uniform(95,140)
 actors=[]
 for at,angle,length,width in [(p,yaw,hl,hw),(q,other_yaw,ol,ow)]:
  a=aa.spawn_actor_from_class(cls,unreal.Vector())
  for n,value in [('PreviousPosition',at),('PreviousYaw',angle),('HalfLength',length),('HalfWidth',width)]:a.set_editor_property(n,value)
  actors.append(a)
 first,second=actors
 actual=first.call_method('EnvelopeClearanceFromVehicle',(second,));forward=unreal.Vector(math.cos(math.radians(yaw)),math.sin(math.radians(yaw)),0);right=unreal.Vector(-forward.y,forward.x,0);other_forward=unreal.Vector(math.cos(math.radians(other_yaw)),math.sin(math.radians(other_yaw)),0);other_right=unreal.Vector(-other_forward.y,other_forward.x,0);lo=0;hi=5000
 for axis in [forward,right,other_forward,other_right]:
  radius=(hl+60)*abs(forward.dot(axis))+(hw+10)*abs(right.dot(axis))+(ol+60)*abs(other_forward.dot(axis))+(ow+10)*abs(other_right.dot(axis));offset=(q-p).dot(axis);rate=forward.dot(axis)
  if abs(rate)<.00001:
   if abs(offset)>radius:hi=-1
  else:interval=sorted([(offset-radius)/rate,(offset+radius)/rate]);lo=max(lo,interval[0]);hi=min(hi,interval[1])
 expected=max(0,lo-25) if hi>=lo and lo<5000 else 100000000;rows.append(dict(case=index,actual=actual,expected=expected,error=abs(actual-expected)))
 aa.destroy_actor(first);aa.destroy_actor(second)
(P/'swept_math_verification.json').write_text(json.dumps(rows,indent=2));assert max(r['error'] for r in rows)<.1,str([r for r in rows if r['error']>.1][:8]);unreal.log('V2_SWEPT_MATH_PASS '+str(len(rows)));unreal.EditorLoadingAndSavingUtils.new_blank_map(False)

for name in ['PreviousPosition','PreviousYaw','HalfLength','HalfWidth']:E.set_blueprint_variable_instance_editable(b,name,False)
assert E.compile_blueprint(b)
