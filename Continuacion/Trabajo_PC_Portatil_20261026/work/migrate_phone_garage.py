import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
bp=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone');reports=[]
D='/Script/BogotaVoxel.DeliveryComponent';A='/Script/Engine.KismetArrayLibrary'
def field(g,id,var):
 g.node(id,'getfield',owner=D,var=var);g.link('Delivery','Delivery',id,'self')
def valid(g):
 g.get('Delivery');g.call('Valid','IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','Valid','Object');g.branch('HasGameplay','Valid');g.exec('entry','HasGameplay')
def refresh(g):
 g.call('Refresh','RefreshText');g.exec('Refresh','result')
for name,moto in [('GarageBike',False),('GarageMoto',True)]:
 g=Graph();valid(g);g.setter('Preview','PreviewMoto',value=str(moto).lower());g.setter('SelectionValue','Selection',value=4 if moto else 0);g.setter('CatalogValue','CatalogSelection',value=3 if moto else 0)
 field(g,'SavedColor','MotoColor' if moto else 'BikeColor');g.setter('RestoreColor','PaintSelection','SavedColor','MotoColor' if moto else 'BikeColor');g.setter('DefaultColor','PaintSelection',value=0)
 g.exec('HasGameplay','RestoreColor');g.exec('HasGameplay','DefaultColor','else');g.exec('RestoreColor','Preview');g.exec('DefaultColor','Preview');g.exec('Preview','SelectionValue');g.exec('SelectionValue','CatalogValue')
 g.get('Page');g.call('Show','BuildPage');g.link('Page','Page','Show','NewPage');g.exec('CatalogValue','Show');g.exec('Show','result');reports.append(g.build(name))
for name,fn,array,index in [('BuySelected','PurchaseUpgrade','UpgradeIDs','Selection'),('BuyModel','BuyVehicle','ModelIDs','CatalogSelection'),('EquipModel','EquipVehicle','ModelIDs','CatalogSelection')]:
 g=Graph();valid(g);refresh(g);g.exec('HasGameplay','Refresh','else');g.get(array);g.get(index)
 g.call('IndexValid','Array_IsValidIndex',A);g.link(array,array,'IndexValid','TargetArray');g.link(index,index,'IndexValid','IndexToTest');g.branch('HasItem','IndexValid');g.exec('HasGameplay','HasItem');g.exec('HasItem','Refresh','else')
 g.call('Item','Array_Get',A);g.link(array,array,'Item','TargetArray');g.link(index,index,'Item','Index');g.call('Action',fn,D);g.link('Delivery','Delivery','Action','self');g.link('Item','Item','Action','ID');g.exec('HasItem','Action')
 if name=='EquipModel':
  g.branch('Equipped','Action');g.exec('Action','Equipped');g.exec('Equipped','Refresh','else');g.get('PreviewMoto');field(g,'BikeColor','BikeColor');field(g,'MotoColor','MotoColor');g.call('Color','SelectInt',M);g.link('MotoColor','MotoColor','Color','A');g.link('BikeColor','BikeColor','Color','B');g.link('PreviewMoto','PreviewMoto','Color','bPickA');g.setter('RestoreColor','PaintSelection','Color');g.exec('Equipped','RestoreColor');g.exec('RestoreColor','Refresh')
 else:g.exec('Action','Refresh')
 reports.append(g.build(name))
g=Graph();valid(g);refresh(g);g.exec('HasGameplay','Refresh','else');g.get('PreviewMoto');g.get('PaintSelection');g.call('Paint','PaintVehicle',D);g.link('Delivery','Delivery','Paint','self');g.link('PreviewMoto','PreviewMoto','Paint','Motorcycle');g.link('PaintSelection','PaintSelection','Paint','Color');g.exec('HasGameplay','Paint');g.exec('Paint','Refresh');reports.append(g.build('PaintSelected'))
g=Graph();valid(g);refresh(g);g.exec('HasGameplay','Refresh','else');g.get('PreviewMoto');field(g,'BikeModel','BikeModel');field(g,'MotoModel','MotoModel');g.call('Model','SelectName',M);g.link('MotoModel','MotoModel','Model','A');g.link('BikeModel','BikeModel','Model','B');g.link('PreviewMoto','PreviewMoto','Model','bPickA');g.call('Equip','EquipVehicle',D);g.link('Delivery','Delivery','Equip','self');g.link('Model','ReturnValue','Equip','ID');g.exec('HasGameplay','Equip');g.exec('Equip','Refresh');reports.append(g.build('SwitchPressed'))
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());data['phone_garage_graphs']=reports;p.write_text(json.dumps(data,indent=2))
unreal.log('PHONE_GARAGE_BLUEPRINTS_SAVED '+json.dumps(reports))
