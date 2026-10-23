from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');assert 'isolated_repair' in root.parts
unreal.EditorLoadingAndSavingUtils.new_blank_map(False);aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);b=use(V)
for name in ['Lane','Distance','PreviousDistance','PreviousPosition','NextPosition','PreviousYaw','NextYaw','HalfLength','HalfWidth','Parked','PlayerControlled']:E.set_blueprint_variable_instance_editable(b,name,True)
assert E.compile_blueprint(b);vehicleclass=b.generated_class();lanes=[aa.spawn_actor_from_class(unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i)).generated_class(),unreal.Vector()) for i in range(7)];config=json.loads((P/'defaults.json').read_text())[TM.split('.')[0]];meta=json.loads((root/'work/pure_traffic_vehicle_foundation.json').read_text())['models'];frame=json.loads((P/'frozen_traffic_frame.json').read_text());cars=[]
for i in range(150):
 row=frame[str(i)];model=meta[config['ModelIndices'][i]];car=aa.spawn_actor_from_class(vehicleclass,unreal.Vector(*row['position']));fields=dict(Lane=lanes[config['LaneIndices'][i]],Distance=row['distance'],PreviousDistance=row['distance'],PreviousPosition=unreal.Vector(*row['position']),NextPosition=unreal.Vector(*row['position']),PreviousYaw=row['yaw'],NextYaw=row['yaw'],HalfLength=model['half_length'],HalfWidth=model['half_width'],Parked=False,PlayerControlled=False)
 for name,value in fields.items():car.set_editor_property(name,value)
 cars.append(car)
report={}
for i in [8,16,35,57,58,78,97,100,117,125]:
 blocks=[]
 for j,other in enumerate(cars):
  if i==j:continue
  gap=cars[i].call_method('ClearanceFromVehicle',(other,))
  if gap<2:blocks.append(dict(other=j,gap=gap,envelope=cars[i].call_method('EnvelopeClearanceFromVehicle',(other,))))
 report[i]=blocks
(P/'frozen_direct_blocks.json').write_text(json.dumps(report,indent=2));unreal.log('V2_FROZEN_DIRECT_BLOCKS '+json.dumps(report));b=use(TM)
for name in ['Vehicles']:E.set_blueprint_variable_instance_editable(b,name,True)
assert E.compile_blueprint(b);manager=aa.spawn_actor_from_class(b.generated_class(),unreal.Vector());manager.call_method('CreateTrafficCells');manager.set_editor_property('Vehicles',cars);manager.call_method('RebuildTrafficCells');grid={i:manager.call_method('NearbyTrafficClearance',(cars[i],)) for i in report};(P/'frozen_grid_results.json').write_text(json.dumps(grid,indent=2));unreal.log('V2_FROZEN_GRID '+json.dumps(grid));unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
