import unreal, json, re, math
from pathlib import Path
root = Path(__file__).resolve().parent.parent
helpers = root / 'scripts/traffic_gameplay_repair/implement.py'
exec(compile(helpers.read_text().split('# Recovery never')[0],str(helpers),'exec'))
root = Path(__file__).resolve().parent.parent
data = root.parent/'BogotaVoxel/Continuacion/Trabajo/map_adaptation_v2'
frames={}; services={}; states={}
def vector(text): return [float(x) for x in re.findall(r'[XYZ]=([-+\d.]+)',text)]
for line in (root/'traffic_resume_v12.log').read_text(errors='replace').splitlines():
    if 'V2CAR|' in line:
        t,i,dist,speed,pos,yaw=line.split('V2CAR|')[1].split('|')[:6]
        frames.setdefault(float(t),{})[int(i)]=dict(distance=float(dist),speed=float(speed),position=vector(pos),yaw=float(yaw))
    if 'V2SERVICE|' in line:
        t,name,pos,velocity,forward=line.split('V2SERVICE|')[1].split('|')[:5]
        if not any(n in name for n in ['PoliceRoadPatrol','CivilMotorcycle','PoliceMotorcycle','TwoWheelerCitizen']):continue
        forward=vector(forward);services.setdefault(float(t),{})[name]=dict(position=vector(pos),yaw=math.degrees(math.atan2(forward[1],forward[0])),speed=math.hypot(*vector(velocity)[:2]))
    if 'V2CYCLEDETAIL|' in line:
        x=line.split('V2CYCLEDETAIL|')[1].split('|');states[(float(x[0]),x[1])]=float(x[2])
time=max(t for t,f in frames.items() if len(f)==90);frame=frames[time]
config=json.loads((data/'defaults.json').read_text())[TM.split('.')[0]]
models=json.loads((root/'work/pure_traffic_vehicle_foundation.json').read_text())['models']
indices=[int(i*140/80) for i in range(80)]+list(range(140,150))
fit={x['name']:x['lane'] for x in json.loads((data/'service_lane_fit.json').read_text())}
aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
bp=unreal.load_asset(V.split('.')[0])
fields=['Lane','Distance','PreviousDistance','PreviousPosition','NextPosition','PreviousYaw','NextYaw','HalfLength','HalfWidth','Parked','PlayerControlled','Speed']
for fieldname in fields:E.set_blueprint_variable_instance_editable(bp,fieldname,True)
assert E.compile_blueprint(bp)
def inspect(label):
    unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    lanes=[aa.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i)).generated_class(),unreal.Vector()) for i in range(7)]
    cars={};rows={}
    for i,row in frame.items():
        model=models[config['ModelIndices'][indices[i]]];rows['car:'+str(i)]=dict(row,lane=config['LaneIndices'][indices[i]],hl=model['half_length'],hw=model['half_width'],parked=False)
    for name,row in services.get(time,{}).items():
        if name not in fit:continue
        rows[name]=dict(row,lane=fit[name],hl=300 if 'Patrol' in name else 160,hw=135 if 'Patrol' in name else 70,parked=states.get((time,name),0)>=2)
    for name,row in rows.items():
        lane=lanes[row['lane']];position=unreal.Vector(*row['position']);distance=row.get('distance',lane.call_method('ClosestDistance',(position,)))
        car=aa.spawn_actor_from_class(bp.generated_class(),position)
        values=dict(Lane=lane,Distance=distance,PreviousDistance=distance,PreviousPosition=position,NextPosition=position,PreviousYaw=row['yaw'],NextYaw=row['yaw'],HalfLength=row['hl'],HalfWidth=row['hw'],Parked=row['parked'],PlayerControlled=False,Speed=row['speed'])
        for key,value in values.items():car.set_editor_property(key,value)
        cars[name]=car
    report={}
    for name,car in cars.items():
        if rows[name]['speed']>20 or rows[name]['parked']:continue
        blockers=[]
        for other,target in cars.items():
            if name==other or rows[other]['parked']:continue
            gap=car.call_method('ClearanceFromVehicle',(target,))
            if gap<2:blockers.append(dict(other=other,gap=gap,envelope=car.call_method('EnvelopeClearanceFromVehicle',(target,))))
        report[name]=blockers
    (root/('frozen_following_'+label+'.json')).write_text(json.dumps(dict(time=time,blockers=report),indent=2))
    unreal.log('FROZEN_FOLLOWING '+label+' '+json.dumps(report))
    unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
inspect('before')
patch=root/'scripts/fix_repeated_route_following.py'
exec(compile(patch.read_text(),str(patch),'exec'),{'__file__':str(patch)})
inspect('after')
