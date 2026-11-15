import unreal,json,re,math
from pathlib import Path
root=Path(__file__).resolve().parent.parent
frames={}
for line in (root/'traffic_resume_v12.log').read_text().splitlines():
    if 'V2CAR|' not in line:continue
    t,index,distance,speed,position,yaw=line.split('V2CAR|')[1].split('|')[:6]
    if int(index) not in [87,88] or not 145<float(t)<176:continue
    frames.setdefault(float(t),{})[int(index)]=(float(distance),unreal.Vector(*[float(x) for x in re.findall(r'[XYZ]=([-+\d.]+)',position)]),float(yaw))
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lane=aa.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_6').generated_class(),unreal.Vector())
cls=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle').generated_class();cars=[aa.spawn_actor_from_class(cls,unreal.Vector()) for _ in range(2)];result=[]
for time,frame in sorted(frames.items()):
    if len(frame)!=2:continue
    for car,index in zip(cars,[87,88]):
        d,p,y=frame[index]
        for name,value in dict(Lane=lane,Distance=d,PreviousDistance=d,NextPosition=p,PreviousPosition=p,PreviousYaw=y,NextYaw=y,HalfLength=915.,HalfWidth=155.,Parked=False,PlayerControlled=False).items():car.set_editor_property(name,value)
    gap=cars[0].call_method('ClearanceFromVehicle',(cars[1],));envelope=cars[0].call_method('EnvelopeClearanceFromVehicle',(cars[1],))
    aligned=math.cos(math.radians(frame[87][2]-frame[88][2]))>.95
    result.append(dict(time=time,gap=gap,envelope=envelope,aligned=aligned))
    if aligned:assert gap<=envelope+.01,(time,gap,envelope)
assert result
assert any(row['time']<170 and row['aligned'] and row['gap']<5000 for row in result),result
(root/'repeated_bus_following_verification.json').write_text(json.dumps(result,indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('REPEATED_BUS_FOLLOWING_VERIFIED '+str(len(result)))
