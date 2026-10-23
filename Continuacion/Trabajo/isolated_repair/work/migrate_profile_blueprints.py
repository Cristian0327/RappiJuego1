import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0]);SAVE='/Script/BogotaVoxel.DeliverySave';U='/Script/Engine.GameplayStatics';A='/Script/Engine.KismetArrayLibrary';SYS='/Script/Engine.KismetSystemLibrary';reports=[]
def field(g,var,source='Cast',pin='AsDelivery Save'):
 id='Saved'+var;g.node(id,'getfield',var=var,owner=SAVE);g.link(source,pin,id,'self');return id
g=Graph();g.get('DeveloperMode');g.branch('Developer','DeveloperMode','DeveloperMode');g.exec('entry','Developer');g.returner('DevOK',True);g.exec('Developer','DevOK');g.call('Create','CreateSaveGameObject',U,SaveGameClass=SAVE);g.exec('Developer','Create','else');g.node('Cast','cast',type=SAVE);g.link('Create','ReturnValue','Cast','Object');g.call('ValidObject','IsValid',SYS);g.link('Cast','AsDelivery Save','ValidObject','Object');g.branch('Valid','ValidObject');g.exec('Create','Valid');g.exec('Valid','result','else');chain=['Valid']
for var in ['Balance','Purchased','Vehicle','BikeColor','MotoColor','OwnedModels','BikeModel','MotoModel','ModelColors']:
 g.get(var);id='Store'+var;g.node(id,'setfield',var=var,owner=SAVE);g.link('Cast','AsDelivery Save',id,'self');g.link(var,var,id,var);chain.append(id)
g.call('Slot','ProfileSlot');g.call('Save','SaveGameToSlot',U,UserIndex='0');g.link('Cast','AsDelivery Save','Save','SaveGameObject');g.link('Slot','ReturnValue','Save','SlotName');chain.append('Save')
for a,b in zip(chain,chain[1:]):g.exec(a,b)
g.branch('Written','Save');g.exec('Save','Written');g.returner('OK',True);g.exec('Written','OK');g.call('Error','Conv_StringToText',T,InString='No se pudo guardar el progreso.');g.setter('Message','StatusMessage','Error');g.exec('Written','Message','else');g.exec('Message','result');reports.append(g.build('SaveProfile'))
g=Graph();g.get('bValidation');g.branch('Validation','bValidation','bValidation');g.exec('entry','Validation');g.exec('Validation','result');g.call('Slot','ProfileSlot');g.call('Load','LoadGameFromSlot',U,UserIndex='0');g.link('Slot','ReturnValue','Load','SlotName');g.exec('Validation','Load','else');g.node('Cast','cast',type=SAVE);g.link('Load','ReturnValue','Cast','Object');g.call('ValidObject','IsValid',SYS);g.link('Cast','AsDelivery Save','ValidObject','Object');g.branch('Valid','ValidObject');g.exec('Load','Valid');g.exec('Valid','result','else');version=field(g,'Version');g.call('Supported','EqualEqual_IntInt',M,B='1');g.link(version,'Version','Supported','A');g.branch('Version','Supported');g.exec('Valid','Version');g.exec('Version','result','else');balance=field(g,'Balance');g.call('SafeBalance','Max',M,B='0');g.link(balance,'Balance','SafeBalance','A');g.setter('Wallet','Balance','SafeBalance');g.exec('Version','Wallet');chain=['Wallet']
for var in ['BikeColor','MotoColor']:
 saved=field(g,var);g.call('Clamp'+var,'Clamp',M,Min='0',Max='5');g.link(saved,var,'Clamp'+var,'Value');g.setter('Restore'+var,var,'Clamp'+var);chain.append('Restore'+var)
for var in ['OwnedModels','ModelColors']:
 saved=field(g,var);g.setter('Restore'+var,var,saved,var);chain.append('Restore'+var)
g.get('Purchased');g.call('ClearUpgrades','Array_Clear',A);g.link('Purchased','Purchased','ClearUpgrades','TargetArray');chain.append('ClearUpgrades')
for a,b in zip(chain,chain[1:]):g.exec(a,b)
purchased=field(g,'Purchased');g.node('Loop','foreach');g.link(purchased,'Purchased','Loop','Array');g.link('ClearUpgrades','then','Loop','Exec');g.call('Spec','GetUpgradeSpec');g.link('Loop','Array Element','Spec','ID');g.branch('Recognized','Spec','Found');g.link('Loop','LoopBody','Recognized','execute');g.call('RestoreUpgrade','Array_AddUnique',A);g.link('Purchased','Purchased','RestoreUpgrade','TargetArray');g.link('Loop','Array Element','RestoreUpgrade','NewItem');g.exec('Recognized','RestoreUpgrade');vehicle=field(g,'Vehicle');g.call('WasMoto','EqualEqual_ByteByte',M,B='1');g.link(vehicle,'Vehicle','WasMoto','A');g.call('OwnMoto','Owns',ID='Motorcycle');g.call('CanMoto','BooleanAND',M);g.link('WasMoto','ReturnValue','CanMoto','A');g.link('OwnMoto','ReturnValue','CanMoto','B');g.branch('Moto','CanMoto');g.link('Loop','Completed','Moto','execute');g.setter('RestoreMoto','Vehicle',value='Motorcycle');g.setter('RestoreBike','Vehicle',value='Bicycle');g.exec('Moto','RestoreMoto');g.exec('Moto','RestoreBike','else')
previous=[('RestoreMoto','then'),('RestoreBike','then')]
for var in ['BikeModel','MotoModel']:
 saved=field(g,var);g.call('Own'+var,'OwnsVehicle');g.link(saved,var,'Own'+var,'ID');g.branch('Allow'+var,'Own'+var)
 for id,pin in previous:g.exec(id,'Allow'+var,pin)
 g.setter('Restore'+var,var,saved,var);g.exec('Allow'+var,'Restore'+var);previous=[('Restore'+var,'then'),('Allow'+var,'else')]
for id,pin in previous:g.exec(id,'result',pin)
reports.append(g.build('LoadProfile'))
unreal.EditorAssetLibrary.save_loaded_asset(bp);p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());names={r['function'] for r in reports};data['graphs']=[r for r in data['graphs'] if r['function'] not in names]+reports;p.write_text(json.dumps(data,indent=2))


