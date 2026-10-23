import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
root=Path(unreal.Paths.project_dir()).parent
bp=unreal.load_asset('/Game/Delivery/Vehicles/BP_DeliveryRider');reports=[]
D='/Script/BogotaVoxel.DeliveryComponent';C='/Script/BogotaVoxel.BogotaCity';S='/Script/Engine.KismetSystemLibrary'
def field(g,id,owner,var,target):
 g.node(id,'getfield',owner=owner,var=var);g.link(target,target,id,'self')
def method(g,id,fn,owner,target,**defaults):
 g.call(id,fn,owner,**defaults);g.link(target,target,id,'self')
def valid(g,var,id):
 g.get(var);g.call(id,'IsValid',S);g.link(var,var,id,'Object');g.branch(id+'Branch',id)
for name in ['ActionPressed','KeyboardActionPressed']:
 g=Graph();valid(g,'Delivery','HasDelivery');g.exec('entry','HasDeliveryBranch');g.exec('HasDeliveryBranch','result','else')
 field(g,'Phone',D,'PhoneOpen','Delivery');g.branch('PhoneOpen','Phone','PhoneOpen');g.exec('HasDeliveryBranch','PhoneOpen');g.exec('PhoneOpen','result')
 field(g,'State',D,'State','Delivery')
 if name=='ActionPressed':
  g.call('Idle','EqualEqual_ByteByte',M,B='0');g.link('State','State','Idle','A');g.branch('IsIdle','Idle');g.exec('PhoneOpen','IsIdle','else');g.call('Mount','Interact');g.exec('IsIdle','Mount');g.exec('Mount','result');method(g,'Action','BeginAction',D,'Delivery',PickupButton='false');g.exec('IsIdle','Action','else');g.exec('Action','result')
 else:
  g.call('Pickup','EqualEqual_ByteByte',M,B='2');g.link('State','State','Pickup','A');g.branch('IsPickup','Pickup');g.exec('PhoneOpen','IsPickup','else');method(g,'Collect','BeginAction',D,'Delivery',PickupButton='true');g.exec('IsPickup','Collect');g.exec('Collect','result')
  g.call('Dropoff','EqualEqual_ByteByte',M,B='3');g.link('State','State','Dropoff','A');g.branch('IsDropoff','Dropoff');g.exec('IsPickup','IsDropoff','else');g.call('Deliver','ActionPressed');g.exec('IsDropoff','Deliver');g.exec('Deliver','result');method(g,'Door','StoreDoorAction',D,'Delivery');g.exec('IsDropoff','Door','else');g.branch('DoorHandled','Door');g.exec('Door','DoorHandled');g.exec('DoorHandled','result');g.call('OtherAction','ActionPressed');g.exec('DoorHandled','OtherAction','else');g.exec('OtherAction','result')
 reports.append(g.build(name))

g=Graph();valid(g,'City','HasCity');g.exec('entry','HasCityBranch');g.exec('HasCityBranch','result','else');method(g,'Skip','AdvanceTime',C,'City');g.exec('HasCityBranch','Skip');g.exec('Skip','result');reports.append(g.build('SkipTime'))

g=Graph();valid(g,'Delivery','HasDelivery');g.exec('entry','HasDeliveryBranch');method(g,'CancelHold','EndAction',D,'Delivery');g.exec('HasDeliveryBranch','CancelHold');g.setter('StopBoost','Sprint',value='false');g.exec('CancelHold','StopBoost');g.exec('HasDeliveryBranch','StopBoost','else');g.get('Paused');g.call('Opposite','Not_PreBool',M);g.link('Paused','Paused','Opposite','A');g.setter('SetPause','Paused','Opposite');g.exec('StopBoost','SetPause');g.call('ApplyPause','SetGamePaused','/Script/Engine.GameplayStatics');g.link('Paused','Paused','ApplyPause','bPaused');g.exec('SetPause','ApplyPause');g.exec('ApplyPause','result');reports.append(g.build('TogglePause'))

g=Graph();g.get('Quality');g.call('High','EqualEqual_IntInt',M,B='2');g.link('Quality','Quality','High','A');g.call('Next','SelectInt',M,A='0',B='2');g.link('High','ReturnValue','Next','bPickA');g.setter('SetQuality','Quality','Next');g.exec('entry','SetQuality');valid(g,'City','HasCity');g.exec('SetQuality','HasCityBranch');method(g,'Detail','SetDetail',C,'City');g.link('Quality','Quality','Detail','Detail');g.exec('HasCityBranch','Detail');g.call('Low','EqualEqual_IntInt',M,B='0');g.link('Quality','Quality','Low','A');g.call('Command','SelectString',M,A='r.Shadow.MaxResolution 1024',B='r.Shadow.MaxResolution 2048');g.link('Low','ReturnValue','Command','bPickA');g.call('ShadowQuality','ExecuteConsoleCommand',S);g.link('Command','ReturnValue','ShadowQuality','Command');g.exec('Detail','ShadowQuality');g.exec('HasCityBranch','ShadowQuality','else');g.exec('ShadowQuality','result');reports.append(g.build('ToggleQuality'))
unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
(root/'work/input_blueprint_migration.json').write_text(json.dumps(reports,indent=2));unreal.log('INPUT_BLUEPRINTS_PASS '+str(len(reports)))
