import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/build_pure_phone_navigation.py').read_text();exec(compile(s[:s.index('# Explicit declarations')],'PurePhoneDataSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'});TB='/Script/UMG.TextBlock';BTN='/Script/UMG.Button';STR='/Script/Engine.KismetStringLibrary';UDS='/Script/BogotaVoxel.DeliveryOrder'
def core(g,name,var):g.node(name,'getfield',owner=CORE,var=var);g.link('Delivery','Delivery',name,'self')
def text(g,id,widget,source,pin='ReturnValue'):
 g.get(widget);g.call(id+'Value','Conv_StringToText',TXT);g.link(source,pin,id+'Value','InString');g.call(id,'SetText',TB);g.link(widget,widget,id,'self');g.link(id+'Value','ReturnValue',id,'InText');return id

def cat(g,id,a,ap,b=None,bp='ReturnValue',literal=None):
 g.call(id,'Concat_StrStr',STR,**({'B':literal} if literal is not None else {}));g.link(a,ap,id,'A')
 if b:g.link(b,bp,id,'B')
 return id

def valid(g):
 g.get('Delivery');g.call('Valid','IsValid',K);g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');return 'Ready'
# Header and feedback remain based on the actual component values.
g=Graph();last=valid(g);core(g,'Balance','Balance');g.call('Money','Conv_IntToString',STR);g.link('Balance','Balance','Money','InInt');g.call('Wallet','Concat_StrStr',STR,A='BOG / BOLSILLO $');g.link('Money','ReturnValue','Wallet','B');n=text(g,'HeaderText','Header','Wallet');g.exec(last,n);last=n;core(g,'Status','StatusMessage');g.get('Notice');g.call('NoticeText','SetText',TB);g.link('Notice','Notice','NoticeText','self');g.link('Status','StatusMessage','NoticeText','InText');g.exec(last,'NoticeText');last='NoticeText';core(g,'Energy','Energy');core(g,'Capacity','Capacity');core(g,'Infinite','InfiniteBoost');core(g,'Hold','HoldProgress');g.call('SafeCap','FMax',M,B='1');g.link('Capacity','Capacity','SafeCap','A');g.call('Ratio','Divide_DoubleDouble',M);g.link('Energy','Energy','Ratio','A');g.link('SafeCap','ReturnValue','Ratio','B');g.call('ShownRatio','SelectFloat',M,A='1');g.link('Infinite','InfiniteBoost','ShownRatio','bPickA');g.link('Ratio','ReturnValue','ShownRatio','B')
for name,node,pin in [('EnergyBar','ShownRatio','ReturnValue'),('HoldBar','Hold','HoldProgress')]:
 g.get(name);g.call('Set'+name,'SetPercent','/Script/UMG.ProgressBar');g.link(name,name,'Set'+name,'self');g.link(node,pin,'Set'+name,'InPercent');g.exec(last,'Set'+name);last='Set'+name
g.exec(last,'result');g.build('RefreshHeader',[])
# Empty offer/active rows are disabled rather than showing a stale selection.
for active in [False,True]:
 g=Graph();last=valid(g);array='ActiveOrders' if active else 'Offers';core(g,'Rows',array);core(g,'Selected','SelectedOffer' if not active else 'Order');maxrows=5 if active else 6
 for mode in ['Bike','Moto']:
  for i in range(maxrows):
   tag=mode+str(i);widget='App5_'+mode+'_'+str(i+1).zfill(2) if active else 'App2_'+mode+'_'+str(2+2*i).zfill(2);label=widget+'Label';g.get(widget);g.call(tag+'Valid','Array_IsValidIndex',AL,IndexToTest=str(i));g.link('Rows',array,tag+'Valid','TargetArray');g.call(tag+'Enable','SetIsEnabled',W);g.link(widget,widget,tag+'Enable','self');g.link(tag+'Valid','ReturnValue',tag+'Enable','bInIsEnabled');g.exec(last,tag+'Enable');g.branch(tag+'HasRow',tag+'Valid');g.exec(tag+'Enable',tag+'HasRow');g.call(tag+'Get','Array_Get',AL,Index=str(i));g.link('Rows',array,tag+'Get','TargetArray');row=tag+'Get';pin='Item'
   if active:g.node(tag+'Active','break',type='/Script/BogotaVoxel.ActiveDelivery');g.link(row,pin,tag+'Active','ActiveDelivery');row=tag+'Active';pin='Order'
   g.node(tag+'Fields','break',type=UDS);g.link(row,pin,tag+'Fields','DeliveryOrder');g.call(tag+'Place','Conv_TextToString',TXT);g.link(tag+'Fields','DropoffName' if active else 'PickupName',tag+'Place','InText');g.call(tag+'Reward','Conv_IntToString',STR);g.link(tag+'Fields','Reward',tag+'Reward','InInt');n=cat(g,tag+'Price',tag+'Place','ReturnValue',literal='  /  $');n=cat(g,tag+'Title',n,'ReturnValue',tag+'Reward');show=text(g,tag+'Show',label,n);g.exec(tag+'HasRow',show);g.call(tag+'EmptyLiteral','Concat_StrStr',STR,A='SIN ENTREGA' if active else 'SIN OFERTA',B='');empty=text(g,tag+'Empty',label,tag+'EmptyLiteral');g.exec(tag+'HasRow',empty,'else');g.call(tag+'Next','SetRenderOpacity',W,InOpacity='1');g.link(widget,widget,tag+'Next','self');g.exec(show,tag+'Next');g.exec(empty,tag+'Next');last=tag+'Next'
 g.exec(last,'result');g.build('RefreshActiveCards' if active else 'RefreshOfferCards',[])
# Upgrade nodes preserve the existing tree and display ownership/cost clearly.
g=Graph();last=valid(g);g.get('UpgradeIDs');entries=[('App3_Bike_'+str(7+i).zfill(2),i) for i in range(4)]+[('App3_Moto_'+str(7+i).zfill(2),4+i) for i in range(6)]+[('App6_'+mode+'_'+str(2+i).zfill(2),10+i) for mode in ['Bike','Moto'] for i in range(3)]
for i,(widget,index) in enumerate(entries):
 tag='U'+str(i);g.get(widget);g.call(tag+'ID','Array_Get',AL,Index=str(index));g.link('UpgradeIDs','UpgradeIDs',tag+'ID','TargetArray');g.call(tag+'Spec','GetUpgradeSpec',CORE);g.link('Delivery','Delivery',tag+'Spec','self');g.link(tag+'ID','Item',tag+'Spec','ID');g.node(tag+'Fields','break',type='/Script/BogotaVoxel.DeliveryUpgrade');g.link(tag+'Spec','ReturnValue',tag+'Fields','DeliveryUpgrade');g.call(tag+'Name','Conv_TextToString',TXT);g.link(tag+'Fields','Title',tag+'Name','InText');g.call(tag+'Owned','Owns',CORE);g.link('Delivery','Delivery',tag+'Owned','self');g.link(tag+'ID','Item',tag+'Owned','ID');g.call(tag+'Price','Conv_IntToString',STR);g.link(tag+'Fields','Price',tag+'Price','InInt');g.call(tag+'PriceTag','Concat_StrStr',STR,A='$');g.link(tag+'Price','ReturnValue',tag+'PriceTag','B');g.call(tag+'Status','SelectString',M,A='INSTALADO');g.link(tag+'Owned','ReturnValue',tag+'Status','bPickA');g.link(tag+'PriceTag','ReturnValue',tag+'Status','B');short=next(x['text'] for x in info['widgets'] if x['parent']==widget and 'text' in x);g.call(tag+'Short','Concat_StrStr',STR,A=short,B='');show=text(g,tag+'Text',widget+'Label',tag+'Short');g.exec(last,show);last=show
g.exec(last,'result');g.build('RefreshUpgradeCards',[])
# Vehicle cards share the same validated catalog as purchase/equip logic.
g=Graph();last=valid(g);g.get('ModelIDs')
for mode,base in [('Bike',0),('Moto',3)]:
 for i in range(3):
  tag=mode+str(i);widget='App4_'+mode+'_'+str(7+i).zfill(2);g.call(tag+'ID','Array_Get',AL,Index=str(base+i));g.link('ModelIDs','ModelIDs',tag+'ID','TargetArray');g.call(tag+'Spec','GetVehicleSpec',CORE);g.link('Delivery','Delivery',tag+'Spec','self');g.link(tag+'ID','Item',tag+'Spec','ID');g.node(tag+'Fields','break',type='/Script/BogotaVoxel.DeliveryVehicleSpec');g.link(tag+'Spec','ReturnValue',tag+'Fields','DeliveryVehicleSpec');g.call(tag+'Name','Conv_TextToString',TXT);g.link(tag+'Fields','Title',tag+'Name','InText');g.call(tag+'Price','Conv_IntToString',STR);g.link(tag+'Fields','Price',tag+'Price','InInt');g.call(tag+'Owned','OwnsVehicle',CORE);g.link('Delivery','Delivery',tag+'Owned','self');g.link(tag+'ID','Item',tag+'Owned','ID');g.call(tag+'PriceTag','Concat_StrStr',STR,A='$');g.link(tag+'Price','ReturnValue',tag+'PriceTag','B');g.call(tag+'Status','SelectString',M,A='EN TU GARAJE');g.link(tag+'Owned','ReturnValue',tag+'Status','bPickA');g.link(tag+'PriceTag','ReturnValue',tag+'Status','B');n=cat(g,tag+'Line',tag+'Name','ReturnValue',literal=' / ');n=cat(g,tag+'Title',n,'ReturnValue',tag+'Status');show=text(g,tag+'Text',widget+'Label',n);g.exec(last,show);last=show
g.exec(last,'result');g.build('RefreshVehicleCards',[])
# The selected offer gets its destination/reward detail and an explicit enabled accept control.
g=Graph();last=valid(g);g.call('Chosen','GetSelectedOffer',CORE);g.link('Delivery','Delivery','Chosen','self');g.branch('Selected','Chosen','Found');g.exec(last,'Selected');g.node('Fields','break',type=UDS);g.link('Chosen','ReturnValue','Fields','DeliveryOrder');g.call('Destination','Conv_TextToString',TXT);g.link('Fields','DropoffName','Destination','InText');show=text(g,'SelectedDetails','Details','Destination');g.exec('Selected',show);g.call('Prompt','Concat_StrStr',STR,A='Elige una oferta. Mantén E para aceptar la ruta.',B='');empty=text(g,'EmptyDetails','Details','Prompt');g.exec('Selected',empty,'else');last=show
for mode in ['Bike','Moto']:
 widget='App2_'+mode+'_14';g.get(widget);g.call('Enable'+mode,'SetIsEnabled',W);g.link(widget,widget,'Enable'+mode,'self');g.link('Chosen','Found','Enable'+mode,'bInIsEnabled');g.exec(last,'Enable'+mode)
 if mode=='Bike':g.exec(empty,'Enable'+mode)
 last='Enable'+mode
g.exec(last,'result');g.build('RefreshOfferDetails',[])
g=Graph();last=valid(g)
for fn in ['RefreshHeader','RefreshOfferCards','RefreshActiveCards','RefreshUpgradeCards','RefreshVehicleCards']:
 g.call(fn,fn);g.exec(last,fn);last=fn
g.get('Page');g.call('Offers','EqualEqual_IntInt',M,B='2');g.link('Page','Page','Offers','A');g.branch('OfferPage','Offers');g.exec(last,'OfferPage');g.call('Details','RefreshOfferDetails');g.exec('OfferPage','Details');g.exec('Details','result');g.exec('OfferPage','result','else');g.build('RefreshText');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert not any(x['native_calls'] for x in audit['graphs']);(r/'work/pure_phone_data_migration.json').write_text(json.dumps({'status':'STAGING_DATA_RENDERING_COMPILED','functions':reports,'pending':['Page details for upgrades/catalog/cargo','Selection highlighting and action availability','HUD layout/tick','Map and garage preview','Bindings and core creation']},indent=2));unreal.log('PURE_PHONE_DATA_RENDERING_BUILD_PASS functions='+str(len(reports)))
