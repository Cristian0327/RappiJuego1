"""Stop a service before its real capsule reaches a blocking body this frame."""
from pathlib import Path
import unreal
root=Path(__file__).resolve().parent.parent
p=root/'scripts/traffic_gameplay_repair/implement.py';exec(compile(p.read_text().split('# Recovery never')[0],str(p),'exec'))
AC='/Script/Engine.ActorComponent';CH='/Script/Engine.Character';CAP='/Script/Engine.CapsuleComponent';PAWN='/Script/Engine.Pawn'
ROAD='/Game/Traffic/Services/BP_VoxelRoadVehicle.BP_VoxelRoadVehicle_C';CYCLE='/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C'
guard='/Game/Traffic/Services/BP_ServicePhysicalGuard';b=unreal.load_asset(guard)
if not b:
    factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.ActorComponent)
    b=unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_ServicePhysicalGuard','/Game/Traffic/Services',unreal.Blueprint,factory)
addvar(b,'GuardGoal',vec);addvar(b,'GuardLogTime',real);assert E.compile_blueprint(b)
g=d.Graph();g.call('Owner','GetOwner',AC);g.node('Character','cast',type=CH);g.link('Owner','ReturnValue','Character','Object')
g.node('Cycle','cast',type=CYCLE);g.link('Owner','ReturnValue','Cycle','Object');g.call('CycleValid','IsValid',K);g.link('Cycle','AsBP Two Wheeler Citizen','CycleValid','Object');g.branch('IsCycle','CycleValid');g.exec('entry','IsCycle')
field(g,'CycleState','State',('Cycle','AsBP Two Wheeler Citizen'),CYCLE);op(g,'Riding','Less_DoubleDouble',('CycleState','State'),B='2');g.branch('CycleRiding','Riding');g.exec('IsCycle','CycleRiding')
field(g,'CycleGoal','Goal',('Cycle','AsBP Two Wheeler Citizen'),CYCLE);g.setter('KeepCycleGoal','GuardGoal','CycleGoal','Goal');g.exec('CycleRiding','KeepCycleGoal')
g.node('Road','cast',type=ROAD);g.link('Owner','ReturnValue','Road','Object');field(g,'Route','Route',('Road','AsBP Voxel Road Vehicle'),ROAD);field(g,'Index','RouteIndex',('Road','AsBP Voxel Road Vehicle'),ROAD)
g.call('RoadGoal','Array_Get',AL);g.link('Route','Route','RoadGoal','TargetArray');g.link('Index','RouteIndex','RoadGoal','Index');g.setter('KeepRoadGoal','GuardGoal','RoadGoal','Item');g.exec('IsCycle','KeepRoadGoal','else')
field(g,'Movement','CharacterMovement',('Character','AsCharacter'),CH);field(g,'Capsule','CapsuleComponent',('Character','AsCharacter'),CH);field(g,'Limit','MaxWalkSpeed',('Movement','CharacterMovement'),CM)
g.call('Input','GetPendingMovementInputVector',PAWN);g.link('Character','AsCharacter','Input','self');g.call('Velocity','GetVelocity',A);g.link('Owner','ReturnValue','Velocity','self');op(g,'InputSize','VSizeXY',('Input','ReturnValue'));op(g,'Speed','VSizeXY',('Velocity','ReturnValue'))
op(g,'HasInput','Greater_DoubleDouble',('InputSize','ReturnValue'),B='.01');op(g,'HasSpeed','Greater_DoubleDouble',('Speed','ReturnValue'),B='1');op(g,'NeedsGuard','BooleanOR',('HasInput','ReturnValue'),('HasSpeed','ReturnValue'));g.branch('Active','NeedsGuard');g.exec('KeepCycleGoal','Active');g.exec('KeepRoadGoal','Active')
g.call('Travel','SelectVector',M);g.link('Input','ReturnValue','Travel','A');g.link('Velocity','ReturnValue','Travel','B');g.link('HasInput','ReturnValue','Travel','bPickA');op(g,'Direction','Normal2D',('Travel','ReturnValue'))
g.call('At','K2_GetActorLocation',A);g.link('Owner','ReturnValue','At','self');g.get('GuardGoal');op(g,'GoalDelta','Subtract_VectorVector',('GuardGoal','GuardGoal'),('At','ReturnValue'));op(g,'GoalDistance','VSizeXY',('GoalDelta','ReturnValue'))
op(g,'StepSpeed','FMax',('Limit','MaxWalkSpeed'),('Speed','ReturnValue'));op(g,'Step','Multiply_DoubleDouble',('StepSpeed','ReturnValue'),('entry','DeltaSeconds'));op(g,'AheadMargin','Add_DoubleDouble',('Step','ReturnValue'),B='60');op(g,'Ahead','FMin',('AheadMargin','ReturnValue'),('GoalDistance','ReturnValue'))
g.call('Radius','GetScaledCapsuleRadius',CAP);g.link('Capsule','CapsuleComponent','Radius','self');g.call('Height','GetScaledCapsuleHalfHeight',CAP);g.link('Capsule','CapsuleComponent','Height','self');op(g,'PadRadius','Add_DoubleDouble',('Radius','ReturnValue'),B='8');op(g,'SafeHeight','FMax',('Height','ReturnValue'),('PadRadius','ReturnValue'));op(g,'ExtraHeight','Subtract_DoubleDouble',('SafeHeight','ReturnValue'),('Height','ReturnValue'));op(g,'LiftHeight','Add_DoubleDouble',('ExtraHeight','ReturnValue'),B='3')
g.call('Lift','MakeVector',M);g.link('LiftHeight','ReturnValue','Lift','Z');op(g,'Start','Add_VectorVector',('At','ReturnValue'),('Lift','ReturnValue'));op(g,'AheadVector','Multiply_VectorFloat',('Direction','ReturnValue'),('Ahead','ReturnValue'));op(g,'End','Add_VectorVector',('Start','ReturnValue'),('AheadVector','ReturnValue'))
g.node('Ignore','makearray');g.link('Owner','ReturnValue','Ignore','[0]');g.call('PhysicalProfile','GetCollisionProfileName','/Script/Engine.PrimitiveComponent');g.link('Capsule','CapsuleComponent','PhysicalProfile','self')
g.call('Sweep','CapsuleTraceSingleByProfile',K,bTraceComplex='false',bIgnoreSelf='true',DrawDebugType='None');g.link('PhysicalProfile','ReturnValue','Sweep','ProfileName');g.link('Ignore','Array','Sweep','ActorsToIgnore');g.link('Start','ReturnValue','Sweep','Start');g.link('End','ReturnValue','Sweep','End');g.link('PadRadius','ReturnValue','Sweep','Radius');g.link('SafeHeight','ReturnValue','Sweep','HalfHeight');g.exec('Active','Sweep')
g.call('Hit','BreakHitResult',G);g.link('Sweep','OutHit','Hit','Hit');g.call('NormalXYZ','BreakVector',M);g.link('Hit','ImpactNormal','NormalXYZ','InVec');op(g,'NormalZ','Abs',('NormalXYZ','Z'));op(g,'Side','Less_DoubleDouble',('NormalZ','ReturnValue'),B='.8');op(g,'Blocked','BooleanAND',('Sweep','ReturnValue'),('Side','ReturnValue'));g.branch('Block','Blocked');g.exec('Sweep','Block')
g.call('Stop','StopMovementImmediately','/Script/Engine.MovementComponent');g.link('Movement','CharacterMovement','Stop','self');g.exec('Block','Stop');g.call('Consume','ConsumeMovementInputVector',PAWN);g.link('Character','AsCharacter','Consume','self');g.exec('Stop','Consume')
g.call('Time','GetGameTimeInSeconds',K);g.get('GuardLogTime');op(g,'SinceLog','Subtract_DoubleDouble',('Time','ReturnValue'),('GuardLogTime','GuardLogTime'));op(g,'Due','Greater_DoubleDouble',('SinceLog','ReturnValue'),B='1');g.branch('Log','Due');g.exec('Consume','Log');g.setter('LogClock','GuardLogTime','Time');g.exec('Log','LogClock')
for n,src,pin in [('SelfName','Owner','ReturnValue'),('OtherName','Hit','HitActor'),('OtherPart','Hit','HitComponent')]:g.call(n,'GetObjectName',K);g.link(src,pin,n,'Object')
fields=[('Time','ReturnValue','real'),('SelfName','ReturnValue','str'),('OtherName','ReturnValue','str'),('OtherPart','ReturnValue','str'),('Hit','ImpactPoint','vec')];previous=None
for i,(src,pin,typ) in enumerate(fields):
    tag='GuardMessage'+str(i)
    if typ!='str':
        fn,inp={'real':('Conv_DoubleToString','InDouble'),'vec':('Conv_VectorToString','InVec')}[typ];g.call(tag,fn,'/Script/Engine.KismetStringLibrary');g.link(src,pin,tag,inp);value=(tag,'ReturnValue')
    else:value=(src,pin)
    g.call(tag+'Join','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='V2GUARD|' if previous is None else '')
    if previous:g.link(*previous,tag+'Join','A')
    g.link(*value,tag+'Join','B');g.call(tag+'Sep','Concat_StrStr','/Script/Engine.KismetStringLibrary',B='|');g.link(tag+'Join','ReturnValue',tag+'Sep','A');previous=(tag+'Sep','ReturnValue')
g.call('Print','PrintString',K,bPrintToScreen='false');g.link(*previous,'Print','InString');g.exec('LogClock','Print');build(b,g,'ReceiveTick');unreal.get_default_object(b.generated_class()).set_tick_group(unreal.TickingGroup.TG_DURING_PHYSICS);save(b)

p=root/'scripts/fix_service_tick_groups.py';s=p.read_text();exec(compile(s[s.index('groups={'):s.index('def configure(actor):')],str(p),'exec'))
link=['EnableHeading','then','Append','execute'];assert link in g.links;g.links.remove(link)
g.call('PhysicalGuard','AddComponentByClass',A,Class=guard+'.BP_ServicePhysicalGuard_C',bManualAttachment='false',bDeferredFinish='false');g.link('Each','Array Element','PhysicalGuard','self');g.link('Identity','ReturnValue','PhysicalGuard','RelativeTransform')
g.call('GuardPhase','SetTickGroup',AC,NewTickGroup='TG_DuringPhysics');g.link('PhysicalGuard','ReturnValue','GuardPhase','self');g.call('GuardAfterControl','AddTickPrerequisiteActor',AC);g.link('PhysicalGuard','ReturnValue','GuardAfterControl','self');g.link('Each','Array Element','GuardAfterControl','PrerequisiteActor')
g.call('MovementAfterGuard','AddTickPrerequisiteComponent',AC);g.link('ControlledMovement','ReturnValue','MovementAfterGuard','self');g.link('PhysicalGuard','ReturnValue','MovementAfterGuard','PrerequisiteComponent')
for before,after in zip(['EnableHeading','PhysicalGuard','GuardPhase','GuardAfterControl','MovementAfterGuard'],['PhysicalGuard','GuardPhase','GuardAfterControl','MovementAfterGuard','Append']):g.exec(before,after)
link=['DisableTick','then','Invisible','execute'];assert link in g.links;g.links.remove(link);g.call('NoProxyCollision','SetActorEnableCollision',A,bNewActorEnableCollision='false');g.link('Spawn','ReturnValue','NoProxyCollision','self');g.exec('DisableTick','NoProxyCollision');g.exec('NoProxyCollision','Invisible');build(b,g,'EnsureServiceProxies',[]);save(b)
unreal.log('SERVICE_PHYSICAL_GUARD_READY')
