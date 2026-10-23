import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/extend_pure_phone_data.py').read_text();exec(compile(s[:s.index('# Header and feedback')],'PurePhoneDetailSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'});BTN='/Script/UMG.Button'
# Compact skill node captions are preserved from the authored pixel-art tree.
g=Graph();last=valid(g)
for row in info['widgets']:
 if row['class'].endswith('DeliveryChoiceButton') and (row['name'].startswith('App6_') or row['name'].startswith('App3_')):
  labels=[x for x in info['widgets'] if x['parent']==row['name'] and x.get('text')]
  if not labels:continue
  tag='Label'+str(len(g.nodes));g.call(tag+'Short','Concat_StrStr',STR,A=labels[0]['text'],B='');show=text(g,tag,row['name']+'Label',tag+'Short');g.exec(last,show);last=show
g.exec(last,'result');g.build('RefreshUpgradeCards',[])
# Page-specific details cannot retain a previous offer's instructions.
g=Graph();last=valid(g);g.get('Page');g.get('Selection');g.get('CatalogSelection');g.get('UpgradeIDs');g.get('ModelIDs');edge='then'
for page in range(7):
 tag='Page'+str(page);g.call(tag,'EqualEqual_IntInt',M,B=str(page));g.link('Page','Page',tag,'A');g.branch(tag+'Is',tag);g.exec(last,tag+'Is',edge);start=tag+'Is'
 if page==2:
  g.call(tag+'Offers','RefreshOfferDetails');g.exec(start,tag+'Offers');g.exec(tag+'Offers','result')
 elif page in [0,1]:
  g.call(tag+'Value','Concat_StrStr',STR,A='' if page==0 else 'Elige un punto del mapa para marcar una ruta.',B='');n=text(g,tag+'Text','Details',tag+'Value');g.exec(start,n);g.exec(n,'result')
 elif page in [3,4,6]:
  upgrade=page!=4;array='UpgradeIDs' if upgrade else 'ModelIDs';index='Selection' if upgrade else 'CatalogSelection';g.call(tag+'IndexValid','Array_IsValidIndex',AL);g.link(array,array,tag+'IndexValid','TargetArray');g.link(index,index,tag+'IndexValid','IndexToTest');g.branch(tag+'HasIndex',tag+'IndexValid');g.exec(start,tag+'HasIndex');g.exec(tag+'HasIndex','result','else');g.call(tag+'ID','Array_Get',AL);g.link(array,array,tag+'ID','TargetArray');g.link(index,index,tag+'ID','Index');g.call(tag+'Spec','GetUpgradeSpec' if upgrade else 'GetVehicleSpec',CORE);g.link('Delivery','Delivery',tag+'Spec','self');g.link(tag+'ID','Item',tag+'Spec','ID');g.node(tag+'Fields','break',type='/Script/BogotaVoxel.DeliveryUpgrade' if upgrade else '/Script/BogotaVoxel.DeliveryVehicleSpec');g.link(tag+'Spec','ReturnValue',tag+'Fields','DeliveryUpgrade' if upgrade else 'DeliveryVehicleSpec');g.call(tag+'Title','Conv_TextToString',TXT);g.link(tag+'Fields','Title',tag+'Title','InText');g.call(tag+'Cost','Conv_IntToString',STR);g.link(tag+'Fields','Price',tag+'Cost','InInt');n=cat(g,tag+'PricePrefix',tag+'Title','ReturnValue',literal=' / $');n=cat(g,tag+'WithPrice',n,'ReturnValue',tag+'Cost');n=text(g,tag+'Info','Details',n);g.exec(tag+'HasIndex',n);g.exec(n,'result')
 else:
  core(g,tag+'Orders','ActiveOrders');g.call(tag+'Count','Array_Length',AL);g.link(tag+'Orders','ActiveOrders',tag+'Count','TargetArray');g.call(tag+'Number','Conv_IntToString',STR);g.link(tag+'Count','ReturnValue',tag+'Number','InInt');g.call(tag+'Prefix','Concat_StrStr',STR,A='Entregas activas: ');g.link(tag+'Number','ReturnValue',tag+'Prefix','B');n=cat(g,tag+'Hint',tag+'Prefix','ReturnValue',literal='. Elige una para seguir su recorrido.');n=text(g,tag+'Text','Details',n);g.exec(start,n);g.exec(n,'result')
 last=start;edge='else'
g.exec(last,'result',edge);g.build('RefreshPageDetails',[])
g=Graph();last=valid(g)
for fn in ['RefreshHeader','RefreshOfferCards','RefreshActiveCards','RefreshUpgradeCards','RefreshVehicleCards','RefreshPageDetails']:
 g.call(fn,fn);g.exec(last,fn);last=fn
g.exec(last,'result');g.build('RefreshText');assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());titles=list(c.get_editor_property('PageNames'));titles[3]=unreal.Text('MEJORAS');c.set_editor_property('PageNames',titles);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/pure_phone_detail_polish.json').write_text(json.dumps({'status':'STAGING_COMPILED','changes':['Compact skill captions','Correct bike/motorcycle grouping','Page-specific detail text','Non-overlapping MEJORAS title'],'pending':['Full descriptions/requirements/action availability','Selection/color highlighting','Spatial tree keyboard movement','Map and vehicle preview']},indent=2));unreal.log('PURE_PHONE_DETAIL_POLISH_BUILD_PASS')
