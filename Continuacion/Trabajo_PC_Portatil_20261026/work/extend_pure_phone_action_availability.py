import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/extend_pure_phone_data.py').read_text(encoding='utf-8-sig');exec(compile(s[:s.index('# Header')],'PurePhoneActionSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'})
# UI guards query the same Blueprint tables used by the actual purchase functions.
g=Graph();g.get('Delivery');core(g,'Balance','Balance');g.call('Spec','GetUpgradeSpec',CORE);g.link('Delivery','Delivery','Spec','self');g.link('entry','ID','Spec','ID');g.node('Fields','break',type='/Script/BogotaVoxel.DeliveryUpgrade');g.link('Spec','ReturnValue','Fields','DeliveryUpgrade');g.call('Owned','Owns',CORE);g.link('Delivery','Delivery','Owned','self');g.link('entry','ID','Owned','ID');g.call('NotOwned','Not_PreBool',M);g.link('Owned','ReturnValue','NotOwned','A');g.call('NoRequirement','EqualEqual_NameName',M,B='None');g.link('Fields','Prerequisite','NoRequirement','A');g.call('RequiredOwned','Owns',CORE);g.link('Delivery','Delivery','RequiredOwned','self');g.link('Fields','Prerequisite','RequiredOwned','ID');g.call('Requirement','BooleanOR',M);g.link('NoRequirement','ReturnValue','Requirement','A');g.link('RequiredOwned','ReturnValue','Requirement','B');g.call('Money','GreaterEqual_IntInt',M);g.link('Balance','Balance','Money','A');g.link('Fields','Price','Money','B');last='Spec';pin='Found'
for tag,other in [('New','NotOwned'),('Unlocked','Requirement'),('Affordable','Money')]:
 g.call(tag,'BooleanAND',M);g.link(last,pin,tag,'A');g.link(other,'ReturnValue',tag,'B');last=tag;pin='ReturnValue'
g.link(last,pin,'result','ReturnValue');g.exec('entry','result');[x.update(owner=PHONE) for x in g.nodes if x.get('kind')=='call' and not x.get('owner')];[x.update(type=remap.get(x['type'],x['type'])) for x in g.nodes if x.get('kind') in ['make','break']];assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'CanPurchaseUpgrade',json.dumps({'nodes':g.nodes,'links':g.links,'type_remap':remap,'parameters':[{'name':'ID','category':'name'},{'name':'ReturnValue','category':'bool','out':True}],'pure':True,'const':True}))
g=Graph();last=valid(g);g.get('UpgradeIDs');g.get('ModelIDs');g.get('Selection');g.get('CatalogSelection');g.get('PreviewMoto');g.call('UpgradeIndex','Clamp',M,Min='0',Max='12');g.link('Selection','Selection','UpgradeIndex','Value');g.call('UpgradeID','Array_Get',AL);g.link('UpgradeIDs','UpgradeIDs','UpgradeID','TargetArray');g.link('UpgradeIndex','ReturnValue','UpgradeID','Index');g.call('UpgradeAllowed','CanPurchaseUpgrade');g.link('UpgradeID','Item','UpgradeAllowed','ID')
# Install buttons appear on both the vehicle tree and cargo page.
for page,num in [(3,11),(6,5)]:
 for mode in ['Bike','Moto']:
  # Locate by caption instead of relying on layout-specific numeric IDs.
  pass
byparent={}
for row in info['widgets']:byparent.setdefault(row['parent'],[]).append(row)
for i,row in enumerate(info['widgets']):
 if row['class']!='/Script/UMG.Button':continue
 texts=[x.get('text','') for x in byparent.get(row['name'],[])];label=' / '.join(texts)
 if label not in ['INSTALAR PIEZA','COMPRAR Y EQUIPAR']:continue
 name=row['name'];tag='Install'+str(i);g.get(name);g.call(tag,'SetIsEnabled',W);g.link(name,name,tag,'self');g.link('UpgradeAllowed','ReturnValue',tag,'bInIsEnabled');g.exec(last,tag);last=tag
# Catalog purchase and equip use ownership, requirements, cash, and available cargo capacity.
g.call('ModelIndex','Clamp',M,Min='0',Max='5');g.link('CatalogSelection','CatalogSelection','ModelIndex','Value');g.call('ModelID','Array_Get',AL);g.link('ModelIDs','ModelIDs','ModelID','TargetArray');g.link('ModelIndex','ReturnValue','ModelID','Index');g.call('ModelSpec','GetVehicleSpec',CORE);g.link('Delivery','Delivery','ModelSpec','self');g.link('ModelID','Item','ModelSpec','ID');g.node('VehicleFields','break',type='/Script/BogotaVoxel.DeliveryVehicleSpec');g.link('ModelSpec','ReturnValue','VehicleFields','DeliveryVehicleSpec');g.call('ModelOwned','OwnsVehicle',CORE);g.link('Delivery','Delivery','ModelOwned','self');g.link('ModelID','Item','ModelOwned','ID');g.call('ModelNew','Not_PreBool',M);g.link('ModelOwned','ReturnValue','ModelNew','A');core(g,'Balance','Balance');g.call('ModelMoney','GreaterEqual_IntInt',M);g.link('Balance','Balance','ModelMoney','A');g.link('VehicleFields','Price','ModelMoney','B');g.call('NoPrerequisite','EqualEqual_NameName',M,B='None');g.link('VehicleFields','Prerequisite','NoPrerequisite','A');g.call('PrerequisiteOwned','Owns',CORE);g.link('Delivery','Delivery','PrerequisiteOwned','self');g.link('VehicleFields','Prerequisite','PrerequisiteOwned','ID');g.call('RequirementMet','BooleanOR',M);g.link('NoPrerequisite','ReturnValue','RequirementMet','A');g.link('PrerequisiteOwned','ReturnValue','RequirementMet','B');g.call('BuyCash','BooleanAND',M);g.link('ModelNew','ReturnValue','BuyCash','A');g.link('ModelMoney','ReturnValue','BuyCash','B');g.call('BuyAllowed','BooleanAND',M);g.link('BuyCash','ReturnValue','BuyAllowed','A');g.link('RequirementMet','ReturnValue','BuyAllowed','B');g.call('BaseMoto','EqualEqual_NameName',M,B='MotoStreet');g.link('ModelID','Item','BaseMoto','A');g.call('UnlockAllowed','CanPurchaseUpgrade',ID='Motorcycle');g.call('UnlockCase','BooleanAND',M);g.link('BaseMoto','ReturnValue','UnlockCase','A');g.link('UnlockAllowed','ReturnValue','UnlockCase','B');g.call('OtherModel','Not_PreBool',M);g.link('BaseMoto','ReturnValue','OtherModel','A');g.call('OtherCase','BooleanAND',M);g.link('OtherModel','ReturnValue','OtherCase','A');g.link('BuyAllowed','ReturnValue','OtherCase','B');g.call('BuyFinal','BooleanOR',M);g.link('UnlockCase','ReturnValue','BuyFinal','A');g.link('OtherCase','ReturnValue','BuyFinal','B')
for i,row in enumerate(info['widgets']):
 if row['class']!='/Script/UMG.Button':continue
 label=' / '.join(x.get('text','') for x in byparent.get(row['name'],[]))
 if label not in ['COMPRAR VEHÍCULO','EQUIPAR']:continue
 name=row['name'];tag='CatalogAction'+str(i);g.get(name);g.call(tag,'SetIsEnabled',W);g.link(name,name,tag,'self');g.link('BuyFinal' if label=='COMPRAR VEHÍCULO' else 'ModelOwned','ReturnValue',tag,'bInIsEnabled');g.exec(last,tag);last=tag
g.exec(last,'result');g.build('RefreshActionAvailability',[])
g=Graph();last=valid(g)
for fn in ['RefreshHeader','RefreshOfferCards','RefreshActiveCards','RefreshUpgradeCards','RefreshVehicleCards','RefreshPageDetails','RefreshGaragePreview','RefreshSelectionStyles','RefreshActionAvailability']:
 g.call(fn,fn);g.exec(last,fn);last=fn
g.exec(last,'result');g.build('RefreshText');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('PURE_PHONE_ACTION_AVAILABILITY_PASS')



