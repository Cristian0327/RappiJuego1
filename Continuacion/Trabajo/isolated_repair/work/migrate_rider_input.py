import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
bp=unreal.load_asset('/Game/Delivery/Vehicles/BP_DeliveryRider');reports=[]
D='/Script/BogotaVoxel.DeliveryComponent';P='/Script/Engine.Pawn';C='/Script/Engine.Character';SYS='/Script/Engine.KismetSystemLibrary'
def valid_delivery(g):
 g.get('Delivery');g.call('ValidDelivery','IsValid',SYS);g.link('Delivery','Delivery','ValidDelivery','Object');g.branch('HasDelivery','ValidDelivery');g.exec('entry','HasDelivery')
def phone_gate(g,allowed,blocked='result'):
 valid_delivery(g);g.node('Open','getfield',owner=D,var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.branch('PhoneIsOpen','Open','PhoneOpen');g.exec('HasDelivery','PhoneIsOpen');g.exec('HasDelivery',allowed,'else');g.exec('PhoneIsOpen',blocked);g.exec('PhoneIsOpen',allowed,'else')
for name,var,axis in [('MoveForward','ForwardInput','GetForwardVector'),('MoveRight','SideInput','GetRightVector')]:
 g=Graph();g.setter('SetAxis',var,'entry','V');g.setter('ClearAxis',var,value=0);g.exec('ClearAxis','result');phone_gate(g,'SetAxis','ClearAxis');g.get('Riding');g.branch('Mounted','Riding','Riding');g.exec('SetAxis','Mounted');g.exec('Mounted','result')
 g.call('Controller','GetController',P);g.call('ControllerValid','IsValid',SYS);g.link('Controller','ReturnValue','ControllerValid','Object');g.branch('CanWalk','ControllerValid');g.exec('Mounted','CanWalk','else');g.exec('CanWalk','result','else')
 g.call('ViewRotation','GetControlRotation',P);g.call('Angles','BreakRotator',M);g.link('ViewRotation','ReturnValue','Angles','InRot');g.call('HorizontalRotation','MakeRotator',M);g.link('Angles','Yaw','HorizontalRotation','Yaw');g.call('Direction',axis,M);g.link('HorizontalRotation','ReturnValue','Direction','InRot');g.call('Move','AddMovementInput',P);g.link('Direction','ReturnValue','Move','WorldDirection');g.link('entry','V','Move','ScaleValue');g.exec('CanWalk','Move');g.exec('Move','result');reports.append(g.build(name))
for name,fn in [('Turn','AddControllerYawInput'),('Look','AddControllerPitchInput')]:
 g=Graph();g.call('LookInput',fn,P);g.link('entry','V','LookInput','Val');phone_gate(g,'LookInput');g.exec('LookInput','result');reports.append(g.build(name))
for name,value in [('StartSprint',True),('EndSprint',False)]:
 g=Graph();g.setter('SetSprint','Sprint',value=str(value).lower())
 if value:phone_gate(g,'SetSprint')
 else:g.exec('entry','SetSprint')
 g.exec('SetSprint','result');reports.append(g.build(name))
g=Graph();g.get('Riding');g.branch('Mounted','Riding','Riding');phone_gate(g,'Mounted');g.setter('Brake','BikeSpeed',value=0);g.exec('Mounted','Brake');g.exec('Brake','result');g.call('Jump','Jump',C);g.exec('Mounted','Jump','else');g.exec('Jump','result');reports.append(g.build('JumpOrBrake'))
g=Graph();g.call('Stop','StopJumping',C);g.exec('entry','Stop');g.exec('Stop','result');reports.append(g.build('StopJump'))
g=Graph();previous='entry'
for var,value in [('ForwardInput',0),('SideInput',0),('Sprint','false'),('BikeSpeed',0)]:
 g.setter('Clear'+var,var,value=value);g.exec(previous,'Clear'+var);previous='Clear'+var
g.get('CharacterMovement');g.call('Stop','StopMovementImmediately','/Script/Engine.MovementComponent');g.link('CharacterMovement','CharacterMovement','Stop','self');g.exec(previous,'Stop');g.exec('Stop','result');reports.append(g.build('StopForPhone'))
for name,fn in [('ActionReleased','EndAction'),('PickupReleased','EndAction'),('PickupPressed','BeginAction'),('PhonePressed','TogglePhone'),('VehiclePressed','SwitchVehicle')]:
 g=Graph();valid_delivery(g);g.exec('HasDelivery','result','else');g.call('Action',fn,D,**({'PickupButton':'true'} if name=='PickupPressed' else {}));g.link('Delivery','Delivery','Action','self');g.exec('HasDelivery','Action');g.exec('Action','result');reports.append(g.build(name))
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());data['rider_input_graphs']=reports;p.write_text(json.dumps(data,indent=2))
unreal.log('RIDER_INPUT_BLUEPRINTS_SAVED '+json.dumps(reports))
