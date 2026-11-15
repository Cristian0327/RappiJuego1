from pathlib import Path
import unreal
P=Path(__file__).resolve().parent
s=(P/'build_traffic_probe.py').read_text()
marker="op(g,'Done','Greater_DoubleDouble'"
extra="""
CYCLE='/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C'
CH='/Script/Engine.Character'; CM='/Script/Engine.CharacterMovementComponent'
g.node('CycleCast','cast',type=CYCLE);g.link('ServiceEach','Array Element','CycleCast','Object')
g.call('ValidCycle','IsValid',K);g.link('CycleCast','AsBP Two Wheeler Citizen','ValidCycle','Object');g.branch('OnlyCycle','ValidCycle');g.exec('V2SERVICEPrint','OnlyCycle')
for n in ['State','RouteIndex','Goal','TrafficSpeedLimit']:
 field(g,'Diag'+n,n,('CycleCast','AsBP Two Wheeler Citizen'),CYCLE)
field(g,'DiagMove','CharacterMovement',('CycleCast','AsBP Two Wheeler Citizen'),CH)
field(g,'DiagMax','MaxWalkSpeed',('DiagMove','CharacterMovement'),CM)
field(g,'DiagModeField','MovementMode',('DiagMove','CharacterMovement'),CM);g.call('DiagMode','Conv_ByteToString',S);g.link('DiagModeField','MovementMode','DiagMode','InByte')
op(g,'DiagDelta','Subtract_VectorVector',('DiagGoal','Goal'),('At','ReturnValue'));g.call('DiagDir','Normal2D',M);g.link('DiagDelta','ReturnValue','DiagDir','A')
op(g,'DiagDistance','VSizeXY',('DiagDelta','ReturnValue'));op(g,'DiagCap','FMin',('DiagDistance','ReturnValue'),B='500');op(g,'DiagAhead','Multiply_VectorFloat',('DiagDir','ReturnValue'),('DiagCap','ReturnValue'));op(g,'DiagEnd','Add_VectorVector',('At','ReturnValue'),('DiagAhead','ReturnValue'))
g.node('DiagTypes','makearray',defaults={'[0]':'ObjectTypeQuery1'})
g.call('DiagTrace','SphereTraceSingleForObjects',K,Radius='70',bTraceComplex='false',DrawDebugType='None',bIgnoreSelf='true')
g.link('DiagTypes','Array','DiagTrace','ObjectTypes');g.link('At','ReturnValue','DiagTrace','Start');g.link('DiagEnd','ReturnValue','DiagTrace','End')
g.node('DiagIgnore','makearray');g.link('ServiceEach','Array Element','DiagIgnore','[0]');g.link('DiagIgnore','Array','DiagTrace','ActorsToIgnore');g.exec('OnlyCycle','DiagTrace')
g.call('DiagHit','BreakHitResult',G);g.link('DiagTrace','OutHit','DiagHit','Hit')
for n,pin in [('Actor','HitActor'),('Component','HitComponent')]:
 g.call('DiagHit'+n,'GetObjectName',K);g.link('DiagHit',pin,'DiagHit'+n,'Object')
line('V2CYCLEDETAIL',[('Age','Age','real'),('Name','ReturnValue','str'),('DiagState','State','real'),('DiagRouteIndex','RouteIndex','int'),('DiagGoal','Goal','vec'),('DiagTrafficSpeedLimit','TrafficSpeedLimit','real'),('DiagMax','MaxWalkSpeed','real'),('DiagMode','ReturnValue','str'),('At','ReturnValue','vec'),('Velocity','ReturnValue','vec'),('DiagHitActor','ReturnValue','str'),('DiagHitComponent','ReturnValue','str'),('DiagHit','ImpactPoint','vec')],'DiagTrace')
"""
extra += """
ROAD='/Game/Traffic/Services/BP_VoxelRoadVehicle.BP_VoxelRoadVehicle_C'
g.node('DiagRoadCast','cast',type=ROAD);g.link('ServiceEach','Array Element','DiagRoadCast','Object');g.call('DiagRoadValid','IsValid',K);g.link('DiagRoadCast','AsBP Voxel Road Vehicle','DiagRoadValid','Object');g.branch('DiagOnlyRoad','DiagRoadValid');g.exec('OnlyCycle','DiagOnlyRoad','else')
field(g,'DiagRoadIndex','RouteIndex',('DiagRoadCast','AsBP Voxel Road Vehicle'),ROAD);field(g,'DiagRoadRoute','Route',('DiagRoadCast','AsBP Voxel Road Vehicle'),ROAD);field(g,'DiagRoadObstacle','LastObstacle',('DiagRoadCast','AsBP Voxel Road Vehicle'),ROAD)
g.call('DiagRoadGoal','Array_Get',AL);g.link('DiagRoadRoute','Route','DiagRoadGoal','TargetArray');g.link('DiagRoadIndex','RouteIndex','DiagRoadGoal','Index');field(g,'DiagRoadMove','CharacterMovement',('DiagRoadCast','AsBP Voxel Road Vehicle'),CH);field(g,'DiagRoadMax','MaxWalkSpeed',('DiagRoadMove','CharacterMovement'),CM);field(g,'DiagRoadAcceleration','MaxAcceleration',('DiagRoadMove','CharacterMovement'),CM)
line('V2ROADDETAIL',[('Age','Age','real'),('Name','ReturnValue','str'),('DiagRoadIndex','RouteIndex','int'),('DiagRoadGoal','Item','vec'),('DiagRoadMax','MaxWalkSpeed','real'),('At','ReturnValue','vec'),('Velocity','ReturnValue','vec'),('DiagRoadObstacle','LastObstacle','str'),('DiagRoadAcceleration','MaxAcceleration','real')],'DiagOnlyRoad')
g.call('MeasuredLastInput','GetLastMovementInputVector','/Script/Engine.Pawn');g.link('ServiceEach','Array Element','MeasuredLastInput','self')
g.call('MeasuredAcceleration','GetCurrentAcceleration',CM);g.link('DiagRoadMove','CharacterMovement','MeasuredAcceleration','self')
input_fields=[]
for n,typ in [('MotorDeltaSeconds','real'),('MotorCommandDirection','vec'),('MotorGoalAtInput','vec'),('MotorPositionAtInput','vec'),('MotorInputLimit','real'),('MotorInputScale','real'),('MotorInputIndex','int')]:
 field(g,'Measured'+n,n,('DiagRoadCast','AsBP Voxel Road Vehicle'),ROAD);input_fields.append(('Measured'+n,n,typ))
field(g,'MeasuredRVO','bUseRVOAvoidance',('DiagRoadMove','CharacterMovement'),CM)
field(g,'MeasuredFriction','GroundFriction',('DiagRoadMove','CharacterMovement'),CM)
g.call('MeasuredController','GetController','/Script/Engine.Pawn');g.link('ServiceEach','Array Element','MeasuredController','self');g.call('MeasuredControllerName','GetObjectName',K);g.link('MeasuredController','ReturnValue','MeasuredControllerName','Object')
g.node('MeasuredAICast','cast',type='/Script/AIModule.AIController');g.link('MeasuredController','ReturnValue','MeasuredAICast','Object');g.call('MeasuredAIState','GetMoveStatus','/Script/AIModule.AIController');g.link('MeasuredAICast','AsAIController','MeasuredAIState','self');g.call('MeasuredAIText','Conv_ByteToString',S);g.link('MeasuredAIState','ReturnValue','MeasuredAIText','InByte')
g.call('MeasuredRootMotion','IsPlayingRootMotion',CH);g.link('DiagRoadCast','AsBP Voxel Road Vehicle','MeasuredRootMotion','self')
line('V2INPUT',[('Age','Age','real'),('Name','ReturnValue','str'),('MeasuredLastInput','ReturnValue','vec'),('MeasuredAcceleration','ReturnValue','vec')]+input_fields+[('MeasuredRVO','bUseRVOAvoidance','bool'),('MeasuredFriction','GroundFriction','real'),('MeasuredControllerName','ReturnValue','str'),('MeasuredAIText','ReturnValue','str'),('MeasuredRootMotion','ReturnValue','bool')],'V2ROADDETAILPrint')
motion_fields=[('Age','Age','real'),('Name','ReturnValue','str')]
for n in ['MovementMode','DefaultLandMovementMode']:
 field(g,'Actual'+n,n,('DiagRoadMove','CharacterMovement'),CM);g.call('Actual'+n+'Text','Conv_ByteToString',S);g.link('Actual'+n,n,'Actual'+n+'Text','InByte');motion_fields.append(('Actual'+n+'Text','ReturnValue','str'))
g.call('ActualMaximum','GetMaxSpeed',CM);g.link('DiagRoadMove','CharacterMovement','ActualMaximum','self');motion_fields.append(('ActualMaximum','ReturnValue','real'))
for n in ['BrakingDecelerationWalking','GravityScale','AirControl','BrakingDecelerationFalling','FallingLateralFriction','MaxStepHeight','MaxSimulationTimeStep']:
 field(g,'Actual'+n,n,('DiagRoadMove','CharacterMovement'),CM);motion_fields.append(('Actual'+n,n,'real'))
field(g,'ActualMaxSimulationIterations','MaxSimulationIterations',('DiagRoadMove','CharacterMovement'),CM);motion_fields.append(('ActualMaxSimulationIterations','MaxSimulationIterations','int'))
g.call('ActualMovementClass','GetObjectClass',G);g.link('DiagRoadMove','CharacterMovement','ActualMovementClass','Object');g.call('ActualClassName','GetClassDisplayName',K);g.link('ActualMovementClass','ReturnValue','ActualClassName','Class');motion_fields.append(('ActualClassName','ReturnValue','str'))
g.call('ActualMovementComponents','K2_GetComponentsByClass',A,ComponentClass=CM);g.link('DiagRoadCast','AsBP Voxel Road Vehicle','ActualMovementComponents','self');g.call('ActualMovementCount','Array_Length',AL);g.link('ActualMovementComponents','ReturnValue','ActualMovementCount','TargetArray');motion_fields.append(('ActualMovementCount','ReturnValue','int'))
for n in ['GetLastUpdateVelocity','GetLastUpdateLocation']:
 g.call('Actual'+n,n,CM);g.link('DiagRoadMove','CharacterMovement','Actual'+n,'self');motion_fields.append(('Actual'+n,'ReturnValue','vec'))
line('V2MOTIONSTATE',motion_fields,'V2INPUTPrint')
"""
assert marker in s
s=s.replace(marker,extra+'\n'+marker).replace("B='245'","B='365'")
exec(compile(s,'DetailedTrafficProbe','exec'),{})
unreal.log('RESUME_DETAILED_PROBE_READY')


