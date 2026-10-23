import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
bp=unreal.load_asset('/Game/Delivery/Orders/BP_DeliveryBuilding')
assert bp
A='/Script/Engine.KismetArrayLibrary';S='/Script/Engine.SceneComponent'
g=Graph()
def call(n,f,**d):g.call(n,f,M,**d)
def wire(a,b,p='A',out='ReturnValue'):g.link(a,out,b,p)
for v in ['WalkingCustomers','CustomerWaits','CustomerStops','HalfDepth','StoreKind','CounterDistanceMeters']:g.get(v)
previous='entry'
for v in ['WalkingCustomers','CustomerWaits','CustomerStops']:
 g.call('Valid'+v,'Array_IsValidIndex',A);g.link(v,v,'Valid'+v,'TargetArray');g.link('entry','Index','Valid'+v,'IndexToTest');g.branch('Guard'+v,'Valid'+v);g.exec(previous,'Guard'+v);g.exec('Guard'+v,'result','else');previous='Guard'+v
 g.call('Read'+v,'Array_Get',A);g.link(v,v,'Read'+v,'TargetArray');g.link('entry','Index','Read'+v,'Index')
g.call('ValidCustomer','IsValid','/Script/Engine.KismetSystemLibrary');g.link('ReadWalkingCustomers','Item','ValidCustomer','Object');g.branch('GuardCustomer','ValidCustomer');g.exec(previous,'GuardCustomer');g.exec('GuardCustomer','result','else')
def write_array(n,v,source,out='ReturnValue'):
 g.call(n,'Array_Set',A,bSizeToFit='false');g.link(v,v,n,'TargetArray');g.link('entry','Index',n,'Index');g.link(source,out,n,'Item')
call('Waiting','Greater_DoubleDouble',B='0');g.link('ReadCustomerWaits','Item','Waiting','A');g.branch('Wait','Waiting');g.exec('GuardCustomer','Wait')
call('WaitRemaining','Subtract_DoubleDouble');g.link('ReadCustomerWaits','Item','WaitRemaining','A');g.link('entry','Dt','WaitRemaining','B');write_array('ReduceWait','CustomerWaits','WaitRemaining');g.exec('Wait','ReduceWait');g.exec('ReduceWait','result')
call('LeftAisle','EqualEqual_IntInt',B='0');g.link('entry','Index','LeftAisle','A');call('AisleX','SelectFloat',A='-430',B='430');wire('LeftAisle','AisleX','bPickA')
call('Depth','Multiply_DoubleDouble',B='2');g.link('HalfDepth','HalfDepth','Depth','A');call('FrontLimit','Subtract_DoubleDouble',B='450');wire('Depth','FrontLimit');call('FrontY','FMin',B='850');wire('FrontLimit','FrontY');call('BackY','Subtract_DoubleDouble',B='500');wire('Depth','BackY')
call('FoodShop','EqualEqual_IntInt',B='1');g.link('StoreKind','StoreKind','FoodShop','A');call('CounterY','Multiply_DoubleDouble',B='100');g.link('CounterDistanceMeters','CounterDistanceMeters','CounterY','A');call('BeforeCounter','Subtract_DoubleDouble',B='175');wire('CounterY','BeforeCounter');call('SafeBackY','SelectFloat');wire('BeforeCounter','SafeBackY');wire('BackY','SafeBackY','B');wire('FoodShop','SafeBackY','bPickA')
call('FrontStop','EqualEqual_IntInt',B='0');g.link('ReadCustomerStops','Item','FrontStop','A');call('StopY','SelectFloat');wire('FrontY','StopY');wire('SafeBackY','StopY','B');wire('FrontStop','StopY','bPickA');call('Target','MakeVector',Z='0');wire('AisleX','Target','X');wire('StopY','Target','Y')
g.node('Position','getfield',owner=S,var='RelativeLocation');g.link('ReadWalkingCustomers','Item','Position','self');call('Delta','Subtract_VectorVector');wire('Target','Delta');g.link('Position','RelativeLocation','Delta','B');call('Distance','VSizeXY');wire('Delta','Distance');call('Arrived','Less_DoubleDouble',B='4');wire('Distance','Arrived');g.branch('AtStop','Arrived');g.exec('Wait','AtStop','else')
call('NextStop','Subtract_IntInt',A='1');g.link('ReadCustomerStops','Item','NextStop','B');write_array('ChangeStop','CustomerStops','NextStop');call('PauseSeconds','Add_IntInt',A='3');g.link('entry','Index','PauseSeconds','B');write_array('Pause','CustomerWaits','PauseSeconds');g.exec('AtStop','ChangeStop');g.exec('ChangeStop','Pause');g.exec('Pause','result')
call('Direction','Normal');wire('Delta','Direction');call('StepLength','Multiply_DoubleDouble',B='65');g.link('entry','Dt','StepLength','A');call('ClampedStep','FMin');wire('Distance','ClampedStep');wire('StepLength','ClampedStep','B');call('Step','Multiply_VectorFloat');wire('Direction','Step');wire('ClampedStep','Step','B');call('Next','Add_VectorVector');g.link('Position','RelativeLocation','Next','A');wire('Step','Next','B')
g.call('Player','GetPlayerPawn','/Script/Engine.GameplayStatics',PlayerIndex='0');g.call('PlayerValid','IsValid','/Script/Engine.KismetSystemLibrary');wire('Player','PlayerValid','Object');g.branch('HasPlayer','PlayerValid');g.exec('AtStop','HasPlayer','else');g.exec('HasPlayer','result','else')
g.call('StorePosition','K2_GetActorLocation','/Script/Engine.Actor');g.call('PlayerPosition','K2_GetActorLocation','/Script/Engine.Actor');wire('Player','PlayerPosition','self');call('WorldNext','Add_VectorVector');wire('StorePosition','WorldNext');wire('Next','WorldNext','B');call('PlayerDistance','Vector_Distance2D');wire('WorldNext','PlayerDistance','V1');wire('PlayerPosition','PlayerDistance','V2');call('Blocked','Less_DoubleDouble',B='75');wire('PlayerDistance','Blocked');g.branch('Yield','Blocked');g.exec('HasPlayer','Yield');g.exec('Yield','result')
call('Facing','Conv_VectorToRotator',InVec='0,0,0');wire('Delta','Facing','InVec');call('Angles','BreakRotator');wire('Facing','Angles','InRot');call('ModelYaw','Subtract_DoubleDouble',B='90');g.link('Angles','Yaw','ModelYaw','A');call('Rotation','MakeRotator');wire('ModelYaw','Rotation','Yaw');g.node('CurrentRotation','getfield',owner=S,var='RelativeRotation');g.link('ReadWalkingCustomers','Item','CurrentRotation','self');call('SmoothRotation','RInterpTo',InterpSpeed='5');g.link('CurrentRotation','RelativeRotation','SmoothRotation','Current');wire('Rotation','SmoothRotation','Target');g.link('entry','Dt','SmoothRotation','DeltaTime')
g.call('Turn','K2_SetRelativeRotation',S);g.link('ReadWalkingCustomers','Item','Turn','self');wire('SmoothRotation','Turn','NewRotation');g.call('Move','K2_SetRelativeLocation',S);g.link('ReadWalkingCustomers','Item','Move','self');wire('Next','Move','NewLocation');g.exec('Yield','Turn','else');g.exec('Turn','Move');g.exec('Move','result')
report=g.build('UpdateCustomer')
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());data['customer_motion_graph']=report;p.write_text(json.dumps(data,indent=2))
unreal.log('CUSTOMER_MOTION_BLUEPRINT_SAVED '+json.dumps(report))

