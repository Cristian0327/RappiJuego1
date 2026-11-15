import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
bp=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone');reports=[]
for name,page in [('OpenHome',0),('OpenMap',1),('OpenOrders',2),('OpenShop',3),('OpenCatalog',4),('OpenActiveOrders',5),('OpenCargo',6)]:
 g=Graph();previous='entry'
 if name in ['OpenShop','OpenCatalog']:
  g.get('PreviewMoto');g.call('InitialSelection','SelectInt',M,A='4' if page==3 else '3',B='0');g.link('PreviewMoto','PreviewMoto','InitialSelection','bPickA');g.setter('Choose', 'Selection' if page==3 else 'CatalogSelection','InitialSelection');g.exec('entry','Choose');previous='Choose'
 elif name=='OpenCargo':g.setter('Choose','Selection',value='10');g.exec('entry','Choose');previous='Choose'
 g.call('ShowPage','BuildPage',NewPage=str(page));g.exec(previous,'ShowPage');g.exec('ShowPage','result');reports.append(g.build(name))
for name,fn in [('AcceptPressed','BeginAction'),('AcceptReleased','EndAction'),('IgnorePressed','IgnoreOffer'),('ClearPoint','ClearWaypoint'),('ClosePressed','TogglePhone')]:
 g=Graph();g.get('Delivery');g.call('Valid','IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','Valid','Object');g.branch('HasGameplay','Valid');g.exec('entry','HasGameplay');g.exec('HasGameplay','result','else');previous='HasGameplay'
 if name=='ClosePressed':
  g.node('Open','getfield',owner='/Script/BogotaVoxel.DeliveryComponent',var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.branch('IsOpen','Open','PhoneOpen');g.exec(previous,'IsOpen');g.exec('IsOpen','result','else');previous='IsOpen'
 g.call('Action',fn,'/Script/BogotaVoxel.DeliveryComponent');g.link('Delivery','Delivery','Action','self');g.exec(previous,'Action');g.exec('Action','result');reports.append(g.build(name))
g=Graph();g.get('PaintSelection');g.call('Next','Add_IntInt',M,B='1');g.link('PaintSelection','PaintSelection','Next','A');g.call('Wrap','Percent_IntInt',M,B='6');g.link('Next','ReturnValue','Wrap','A');g.setter('SetColor','PaintSelection','Wrap');g.call('Refresh','RefreshText');g.exec('entry','SetColor');g.exec('SetColor','Refresh');g.exec('Refresh','result');reports.append(g.build('NextColor'))
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());data['phone_navigation_graphs']=reports;p.write_text(json.dumps(data,indent=2))
unreal.log('PHONE_NAVIGATION_BLUEPRINTS_SAVED '+json.dumps(reports))
