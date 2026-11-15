from pathlib import Path
import unreal,json
root=Path(__file__).resolve().parent.parent
helpers=root/'scripts/traffic_gameplay_repair/implement.py'
exec(compile(helpers.read_text().split('# Recovery never')[0],str(helpers),'exec'))
root=Path(__file__).resolve().parent.parent
path=root/'scripts/traffic_gameplay_repair/repair_patrol_heading.py'
source=path.read_text();exec(compile(source[:source.rindex("build(b,g,'ReceiveTick')")],str(path),'exec'))
# Match the static sensor to this segment, as already done for cyclists.
for node in g.nodes:
    if node['id']=='Trace':node['fn']='SphereTraceSingleForObjects';node['defaults'].pop('TraceChannel',None)
    if node['id']=='LookAhead':node['defaults'].pop('B',None)
g.node('CurrentStaticTypes','makearray',defaults={'[0]':'ObjectTypeQuery1'});g.link('CurrentStaticTypes','Array','Trace','ObjectTypes')
op(g,'CurrentSegmentLook','FMin',('Distance','ReturnValue'),B='600');g.link('CurrentSegmentLook','ReturnValue','LookAhead','B')
build(b,g,'ReceiveTick');save(b)
# At 650 cm/s, the inherited 500 cm/s² turn acceleration permits an ~8 m
# corner excursion. Higher lateral response keeps real capsules on the lane.
paths=['/Game/Traffic/Services/BP_VoxelRoadVehicle','/Game/Traffic/Services/BP_CivilMotorcycle','/Game/Traffic/Services/BP_PoliceMotorcycle','/Game/Traffic/Services/BP_PoliceRoadPatrol']
for asset in paths:
    bp=unreal.load_asset(asset);assert E.compile_blueprint(bp);movement=unreal.get_default_object(bp.generated_class()).get_editor_property('character_movement')
    movement.set_editor_property('max_acceleration',6500.);movement.set_editor_property('ground_friction',12.);movement.set_editor_property('braking_deceleration_walking',3000.);save(bp)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);changes=[]
for actor in aa.get_all_level_actors():
    if actor.get_class().get_name() not in ['BP_CivilMotorcycle_C','BP_PoliceMotorcycle_C','BP_PoliceRoadPatrol_C']:continue
    movement=actor.get_editor_property('character_movement');changes.append(dict(name=actor.get_name(),previous_acceleration=movement.get_editor_property('max_acceleration')))
    movement.set_editor_property('max_acceleration',6500.);movement.set_editor_property('ground_friction',12.);movement.set_editor_property('braking_deceleration_walking',3000.)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
(root/'motor_corner_changes.json').write_text(json.dumps(changes,indent=2));unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('MOTOR_SERVICE_CORNERS_FIXED '+str(len(changes)))
