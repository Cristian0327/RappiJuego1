import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
bp=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone');reports=[]
D='/Script/BogotaVoxel.DeliveryComponent';A='/Script/Engine.KismetArrayLibrary'
g=Graph();g.get('Page');g.get('Delivery');g.call('Refresh','RefreshText');g.exec('Refresh','result')
g.call('ColorEntry','GreaterEqual_IntInt',M,B='100');g.link('entry','Index','ColorEntry','A');g.branch('IsColor','ColorEntry');g.exec('entry','IsColor')
g.call('ColorIndex','Subtract_IntInt',M,B='100');g.link('entry','Index','ColorIndex','A');g.call('ClampColor','Clamp',M,Min='0',Max='5');g.link('ColorIndex','ReturnValue','ClampColor','Value');g.setter('SetPaint','PaintSelection','ClampColor');g.exec('IsColor','SetPaint');g.exec('SetPaint','Refresh')
previous='IsColor'
for page in [2,5,3,6,4]:
 tag='Page'+str(page);g.call(tag,'EqualEqual_IntInt',M,B=str(page));g.link('Page','Page',tag,'A');g.branch('Is'+tag,tag);g.exec(previous,'Is'+tag,'else');previous='Is'+tag
 if page in [2,5]:
  g.call('Valid'+tag,'IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','Valid'+tag,'Object');g.branch('Has'+tag,'Valid'+tag);g.exec(previous,'Has'+tag);g.exec('Has'+tag,'Refresh','else');g.call('Choose'+tag,'SelectOffer' if page==2 else 'SelectActiveOrder',D);g.link('Delivery','Delivery','Choose'+tag,'self');g.link('entry','Index','Choose'+tag,'Index');g.exec('Has'+tag,'Choose'+tag);g.branch('Chosen'+tag,'Choose'+tag);g.exec('Choose'+tag,'Chosen'+tag);g.exec('Chosen'+tag,'Refresh','else');g.setter('Save'+tag,'OrderSelection','entry','Index');g.exec('Chosen'+tag,'Save'+tag);g.exec('Save'+tag,'Refresh')
 elif page in [3,6]:
  g.setter('Save'+tag,'Selection','entry','Index');g.exec(previous,'Save'+tag);g.exec('Save'+tag,'Refresh')
 else:
  g.setter('SaveCatalog','CatalogSelection','entry','Index');g.exec(previous,'SaveCatalog');g.get('ModelIDs');g.call('ValidModelIndex','Array_IsValidIndex',A);g.link('ModelIDs','ModelIDs','ValidModelIndex','TargetArray');g.link('entry','Index','ValidModelIndex','IndexToTest');g.call('ValidDelivery','IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','ValidDelivery','Object');g.call('CanReadPaint','BooleanAND',M);g.link('ValidModelIndex','ReturnValue','CanReadPaint','A');g.link('ValidDelivery','ReturnValue','CanReadPaint','B');g.branch('ReadPaint','CanReadPaint');g.exec('SaveCatalog','ReadPaint');g.exec('ReadPaint','Refresh','else')
  g.call('Model','Array_Get',A);g.link('ModelIDs','ModelIDs','Model','TargetArray');g.link('entry','Index','Model','Index');g.node('Colors','getfield',owner=D,var='ModelColors');g.link('Delivery','Delivery','Colors','self');g.call('FindColor','Map_Find','/Script/Engine.BlueprintMapLibrary');g.link('Colors','ModelColors','FindColor','TargetMap');g.link('Model','Item','FindColor','Key');g.setter('RestorePaint','PaintSelection','FindColor','Value');g.exec('ReadPaint','RestorePaint');g.exec('RestorePaint','Refresh')
g.exec(previous,'Refresh','else');reports.append(g.build('SelectEntry'))
for name,next_item in [('SelectPrevious',False),('SelectNext',True)]:
 g=Graph()
 for var in ['Page','OrderSelection','CatalogSelection','Selection','PreviewMoto','Delivery']:g.get(var)
 previous='entry';prevpin='then'
 for page in [5,6,2,4,3]:
  tag='P'+str(page);g.call('Page'+tag,'EqualEqual_IntInt',M,B=str(page));g.link('Page','Page','Page'+tag,'A');g.branch('Is'+tag,'Page'+tag);g.exec(previous,'Is'+tag,prevpin);previous='Is'+tag;prevpin='else'
  index='OrderSelection' if page in [2,5] else 'CatalogSelection' if page==4 else 'Selection'
  g.call('Step'+tag,'Add_IntInt' if next_item else 'Subtract_IntInt',M,B='1');g.link(index,index,'Step'+tag,'A')
  if page in [3,4]:
   low_b,low_m,high_b,high_m=(0,4,3,9) if page==3 else (0,3,2,5)
   g.call('Low'+tag,'SelectInt',M,A=str(low_m),B=str(low_b));g.call('High'+tag,'SelectInt',M,A=str(high_m),B=str(high_b))
   for n in ['Low','High']:g.link('PreviewMoto','PreviewMoto',n+tag,'bPickA')
   g.call('Clamp'+tag,'Clamp',M);g.link('Low'+tag,'ReturnValue','Clamp'+tag,'Min');g.link('High'+tag,'ReturnValue','Clamp'+tag,'Max')
  elif page==5:
   g.call('Valid','IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','Valid','Object');g.branch('HasGameplay','Valid');g.exec(previous,'HasGameplay');g.exec('HasGameplay','result','else')
   g.node('Orders','getfield',owner=D,var='ActiveOrders');g.link('Delivery','Delivery','Orders','self');g.call('Count','Array_Length',A);g.link('Orders','ActiveOrders','Count','TargetArray');g.call('Last','Subtract_IntInt',M,B='1');g.link('Count','ReturnValue','Last','A');g.call('NonNegative','Max',M,B='0');g.link('Last','ReturnValue','NonNegative','A');g.call('Clamp'+tag,'Clamp',M,Min='0');g.link('NonNegative','ReturnValue','Clamp'+tag,'Max')
  else:g.call('Clamp'+tag,'Clamp',M,Min='10' if page==6 else '0',Max='12' if page==6 else '5')
  g.link('Step'+tag,'ReturnValue','Clamp'+tag,'Value');g.call('Choose'+tag,'SelectEntry');g.link('Clamp'+tag,'ReturnValue','Choose'+tag,'Index');g.exec('HasGameplay' if page==5 else previous,'Choose'+tag);g.exec('Choose'+tag,'result')
 g.exec(previous,'result','else');reports.append(g.build(name))
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());data['phone_selection_graphs']=reports;p.write_text(json.dumps(data,indent=2))
unreal.log('PHONE_SELECTION_BLUEPRINTS_SAVED '+json.dumps(reports))

