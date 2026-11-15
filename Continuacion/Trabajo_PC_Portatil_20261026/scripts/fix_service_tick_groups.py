"""Give service control, physical movement and visible heading distinct tick phases."""
from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/fix_precise_motor_tracking.py'
exec(compile(p.read_text(),str(p),'exec'),{'__file__':str(p)})
p=root/'scripts/traffic_gameplay_repair/implement.py'
exec(compile(p.read_text().split('# Recovery never')[0],str(p),'exec'))
groups={n:getattr(unreal.TickingGroup,'TG_'+n) for n in ['PRE_PHYSICS','DURING_PHYSICS','POST_PHYSICS','POST_UPDATE_WORK']}
heading='/Game/Traffic/Services/BP_ServiceTravelHeading'
b=unreal.load_asset(heading)
if not b:
    factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.ActorComponent)
    b=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_ServiceTravelHeading','/Game/Traffic/Services',unreal.Blueprint,factory)
g=d.Graph();g.call('Owner','GetOwner','/Script/Engine.ActorComponent');g.call('Velocity','GetVelocity',A);g.link('Owner','ReturnValue','Velocity','self')
op(g,'Speed','VSizeXY',('Velocity','ReturnValue'));op(g,'Moving','Greater_DoubleDouble',('Speed','ReturnValue'),B='5');g.branch('HaveMotion','Moving');g.exec('entry','HaveMotion')
g.call('PlanarVelocity','Normal2D',M);g.link('Velocity','ReturnValue','PlanarVelocity','A');g.call('Rotation','Conv_VectorToRotator',M);g.link('PlanarVelocity','ReturnValue','Rotation','InVec');g.call('Align','K2_SetActorRotation',A,bTeleportPhysics='true');g.link('Owner','ReturnValue','Align','self');g.link('Rotation','ReturnValue','Align','NewRotation');g.exec('HaveMotion','Align')
build(b,g,'ReceiveTick');c=unreal.get_default_object(b.generated_class());c.set_tick_group(groups['POST_UPDATE_WORK']);tick=c.get_editor_property('primary_component_tick');tick.set_editor_property('start_with_tick_enabled',True);c.set_editor_property('primary_component_tick',tick);save(b)

b=use('/Game/World/BogotaUrban/BP_BogotaServiceSignals')
source=(root/'scripts/fix_precise_motor_tracking.py').read_text();start=source.index("b=use('/Game/World/BogotaUrban/BP_BogotaServiceSignals');source=");end=source.index("build(b,g,'EnsureServiceProxies',[]);save(b)",start)
exec(compile(source[start:end],'GroupedServiceProxies','exec'))
link=['ControllerBeforeMovement','then','Append','execute'];assert link in g.links;g.links.remove(link)
g.call('TravelHeading','AddComponentByClass',A,Class=heading+'.BP_ServiceTravelHeading_C',bManualAttachment='false',bDeferredFinish='false');g.link('Each','Array Element','TravelHeading','self');g.link('Identity','ReturnValue','TravelHeading','RelativeTransform')
g.call('SetServicePhase','SetTickGroup',A,NewTickGroup='TG_PrePhysics');g.call('SetServiceInterval','SetActorTickInterval',A,TickInterval='0')
g.call('SetControlPhase','SetTickGroup',A,NewTickGroup='TG_DuringPhysics');g.link('Each','Array Element','SetControlPhase','self')
g.call('SetMovementPhase','SetTickGroup','/Script/Engine.ActorComponent',NewTickGroup='TG_PostPhysics');g.link('ControlledMovement','ReturnValue','SetMovementPhase','self')
g.call('SetHeadingPhase','SetTickGroup','/Script/Engine.ActorComponent',NewTickGroup='TG_PostPhysics');g.link('TravelHeading','ReturnValue','SetHeadingPhase','self')
g.call('HeadingAfterMovement','AddTickPrerequisiteComponent','/Script/Engine.ActorComponent');g.link('TravelHeading','ReturnValue','HeadingAfterMovement','self');g.link('ControlledMovement','ReturnValue','HeadingAfterMovement','PrerequisiteComponent')
g.call('EnableHeading','SetComponentTickEnabled','/Script/Engine.ActorComponent',bEnabled='true');g.link('TravelHeading','ReturnValue','EnableHeading','self')
for before,after in zip(['ControllerBeforeMovement','SetServicePhase','SetServiceInterval','SetControlPhase','SetMovementPhase','TravelHeading','SetHeadingPhase','HeadingAfterMovement','EnableHeading'],['SetServicePhase','SetServiceInterval','SetControlPhase','SetMovementPhase','TravelHeading','SetHeadingPhase','HeadingAfterMovement','EnableHeading','Append']):g.exec(before,after)
build(b,g,'EnsureServiceProxies',[]);save(b)

def configure(actor):
    group=groups['PRE_PHYSICS'] if actor.get_class().get_name()=='BP_BogotaServiceSignals_C' else groups['DURING_PHYSICS']
    actor.set_tick_group(group);actor.set_actor_tick_interval(0.)
    if group==groups['PRE_PHYSICS']:return
    move=actor.get_editor_property('character_movement');move.set_tick_group(groups['POST_PHYSICS'])
    move.set_editor_property('tick_before_owner',False);move.set_editor_property('use_rvo_avoidance',False);move.set_editor_property('min_analog_walk_speed',0.)
classes=['BP_VoxelRoadVehicle','BP_CivilMotorcycle','BP_PoliceMotorcycle','BP_PoliceRoadPatrol','BP_TwoWheelerCitizen']
for name in classes:
    bp=use('/Game/Traffic/Services/'+name);configure(unreal.get_default_object(bp.generated_class()));save(bp)
bp=use('/Game/World/BogotaUrban/BP_BogotaServiceSignals');configure(unreal.get_default_object(bp.generated_class()));save(bp)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if actor.get_class().get_name() in [n+'_C' for n in classes]+['BP_BogotaServiceSignals_C']:configure(actor)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
for name in ['build_current_traffic_causes.py','prepare_current_regressions.py']:
    path=root/'scripts'/name;exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path)})
unreal.log('SERVICE_TICK_GROUPS_READY')


