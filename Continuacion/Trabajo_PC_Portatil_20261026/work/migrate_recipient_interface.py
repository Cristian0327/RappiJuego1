import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
bp=unreal.load_asset('/Game/Delivery/Orders/BP_VoxelCustomer');reports=[]
g=Graph();g.get('Delivery');g.get('OrderID');g.call('Valid','IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','Valid','Object');g.branch('HasOrder','Valid');g.exec('entry','HasOrder');g.exec('HasOrder','result','else')
g.call('Owner','GetOwner','/Script/Engine.ActorComponent');g.link('Delivery','Delivery','Owner','self');g.call('MatchesRider','EqualEqual_ObjectObject',M);g.link('entry','Rider','MatchesRider','A');g.link('Owner','ReturnValue','MatchesRider','B');g.call('MatchesOrder','EqualEqual_GuidGuid',G);g.link('entry','OrderID','MatchesOrder','A');g.link('OrderID','OrderID','MatchesOrder','B');g.node('State','getfield',owner='/Script/BogotaVoxel.DeliveryComponent',var='State');g.link('Delivery','Delivery','State','self');g.call('Ready','EqualEqual_ByteByte',M,B='3');g.link('State','State','Ready','A');g.call('NearHome','IsAtTarget','/Script/BogotaVoxel.DeliveryComponent');g.link('Delivery','Delivery','NearHome','self')
last='MatchesRider'
for name in ['MatchesOrder','Ready','NearHome']:
 node='And'+name;g.call(node,'BooleanAND',M);g.link(last,'ReturnValue',node,'A');g.link(name,'ReturnValue',node,'B');last=node
g.node('Allowed','return');g.link(last,'ReturnValue','Allowed','ReturnValue');g.exec('HasOrder','Allowed');reports.append(g.build('CanDeliver'))
g=Graph();g.get('Delivery');g.call('Allowed','CanDeliver');g.link('entry','Rider','Allowed','Rider');g.link('entry','OrderID','Allowed','OrderID');g.branch('Ready','Allowed');g.exec('entry','Ready');g.exec('Ready','result','else');g.call('Finish','CompleteOrder','/Script/BogotaVoxel.DeliveryComponent');g.link('Delivery','Delivery','Finish','self');g.link('entry','OrderID','Finish','ExpectedID');g.exec('Ready','Finish');g.exec('Finish','result');reports.append(g.build('ReceiveDelivery'))
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
gameplay=unreal.EditorAssetLibrary.load_blueprint_class('/Game/Delivery/Core/BPC_DeliveryGameplay');default=unreal.get_default_object(gameplay)
default.set_editor_property('recipient_class',unreal.EditorAssetLibrary.load_blueprint_class('/Game/Delivery/Orders/BP_VoxelCustomer'))
assert unreal.EditorAssetLibrary.save_asset('/Game/Delivery/Core/BPC_DeliveryGameplay',only_if_is_dirty=False)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());data['recipient_interface_graphs']=reports;p.write_text(json.dumps(data,indent=2))
unreal.log('RECIPIENT_INTERFACE_BLUEPRINTS_SAVED '+json.dumps(reports))

