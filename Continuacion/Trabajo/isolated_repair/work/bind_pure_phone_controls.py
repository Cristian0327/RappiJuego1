import unreal,json,sys,re
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/build_pure_phone_navigation.py').read_text();exec(compile(s[:s.index('# Explicit declarations')],'PurePhoneControlSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'});UI='/Script/UMG.WidgetBlueprintLibrary';INPUT='/Script/Engine.KismetInputLibrary'
g=Graph();g.get('Delivery');g.call('Valid','IsValid',K);g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');g.call('Close','ClosePhoneForWorld',CORE);g.link('Delivery','Delivery','Close','self');g.exec('Ready','Close');g.exec('Close','result');g.build('ClosePressed')
g=Graph();g.get('Page');last='entry';edge='then'
for page,fn in [(2,'AcceptPressed'),(3,'BuySelected'),(6,'BuySelected'),(4,'BuyModel')]:
 tag='P'+str(page);g.call(tag,'EqualEqual_IntInt',M,B=str(page));g.link('Page','Page',tag,'A');g.branch('Is'+tag,tag);g.exec(last,'Is'+tag,edge);g.call('Action'+tag,fn);g.exec('Is'+tag,'Action'+tag);g.exec('Action'+tag,'result');last='Is'+tag;edge='else'
g.exec(last,'result',edge);g.build('ConfirmPressed',[])
for name,fn in [('UISelectNext','SelectNext'),('UISelectPrevious','SelectPrevious')]:
 g=Graph();g.get('Page');g.get('Delivery');g.call('IsOffers','EqualEqual_IntInt',M,B='2');g.link('Page','Page','IsOffers','A');g.call('Chosen','GetSelectedOffer',CORE);g.link('Delivery','Delivery','Chosen','self');g.call('NoSelection','Not_PreBool',M);g.link('Chosen','Found','NoSelection','A');g.call('First','BooleanAND',M);g.link('IsOffers','ReturnValue','First','A');g.link('NoSelection','ReturnValue','First','B');g.branch('BeginSelection','First');g.exec('entry','BeginSelection');g.call('FirstEntry','SelectEntry',Index='0');g.exec('BeginSelection','FirstEntry');g.exec('FirstEntry','result');g.call('Step',fn);g.exec('BeginSelection','Step','else');g.exec('Step','result');g.build(name,[])
# Bind every existing button, including hold-to-accept pressed/released events.
info=json.loads((r/'work/phone_designer_tree.json').read_text());byparent={}
for row in info['widgets']:byparent.setdefault(row['parent'],[]).append(row)
text_actions={'X':'ClosePressed','QUITAR MI MARCA':'ClearPoint','CASA':'OpenHome','MAPA':'OpenMap','PEDIDOS':'OpenOrders','TALLER':'OpenShop','MALETAS':'OpenCargo','VEHÍCULOS':'OpenCatalog','PIEZAS':'OpenShop','CICLAS':'GarageBike','MOTOS':'GarageMoto','MIS ENTREGAS / CAPACIDAD':'OpenActiveOrders','PASAR ESTA OFERTA':'IgnorePressed','INSTALAR PIEZA':'BuySelected','COMPRAR Y EQUIPAR':'BuySelected','USAR':'SwitchPressed','PINTAR $2.000':'PaintSelected','COMPRAR VEHÍCULO':'BuyModel','EQUIPAR':'EquipModel','BUSCAR OTRO PEDIDO':'OpenOrders'};home={'HomeMap':'OpenMap','HomeOrders':'OpenOrders','HomeWorkshop':'OpenShop','HomeCargo':'OpenCargo','HomeVehicles':'OpenCatalog'};bindings=[];buttons=0
for row in info['widgets']:
 if 'Button' not in row['class']:continue
 buttons+=1;name=row['name'];spec={'widget':name,'delegate':'OnClicked'}
 if name in home:spec['function']=home[name]
 elif row['class'].endswith('DeliveryChoiceButton'):
  m=re.match(r'App(\d)_(Bike|Moto)_(\d+)',name);assert m,name;page=int(m[1]);mode=m[2];n=int(m[3])
  if page==2:index=(n-2)//2
  elif page==5:index=n-1
  elif page==4:index=n-7+(3 if mode=='Moto' else 0)
  elif page==6:index=n-2+10
  elif page==3:index=n-7+(4 if mode=='Moto' else 0) if n<(15 if mode=='Moto' else 13) else 100+n-(15 if mode=='Moto' else 13)
  else:raise AssertionError(name)
  spec.update(function='SelectEntry',defaults={'Index':str(index)})
 else:
  texts=[x.get('text','') for x in byparent.get(name,[])];label=' / '.join(texts)
  if label=='MANTÉN PARA TOMAR LA RUTA':
   bindings += [{'widget':name,'delegate':'OnPressed','function':'AcceptPressed'},{'widget':name,'delegate':'OnReleased','function':'AcceptReleased'}];continue
  assert label in text_actions,(name,label);spec['function']=text_actions[label]
 bindings.append(spec)
assert buttons==159 and len(bindings)==161,(buttons,len(bindings));assert unreal.DeliveryEditorLibrary.bind_widget_delegate_graph(bp,json.dumps(bindings))
# Widget key handling owns navigation while the portrait phone has focus.
keys=[('Tab','ClosePressed'),('Escape','ClosePressed'),('Gamepad_Special_Left','ClosePressed'),('One','OpenMap'),('Two','OpenOrders'),('Three','OpenShop'),('Four','OpenCargo'),('Five','OpenCatalog'),('Six','OpenActiveOrders'),('E','ConfirmPressed'),('Enter','ConfirmPressed'),('Gamepad_FaceButton_Bottom','ConfirmPressed')]+[(key,fn) for fn,names in [('UISelectPrevious',['Up','Left','Gamepad_DPad_Up','Gamepad_DPad_Left']),('UISelectNext',['Down','Right','Gamepad_DPad_Down','Gamepad_DPad_Right'])] for key in names]
for name,actions in [('OnPreviewKeyDown',keys),('OnKeyUp',[(key,'AcceptReleased') for key in ['E','Enter','Gamepad_FaceButton_Bottom']])]:
 g=Graph();g.get('Delivery');g.call('Valid','IsValid',K);g.link('Delivery','Delivery','Valid','Object');g.branch('HasData','Valid');g.exec('entry','HasData');g.call('Unhandled','Unhandled',UI);g.link('Unhandled','ReturnValue','result','ReturnValue');g.exec('HasData','result','else');g.node('Open','getfield',owner=CORE,var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.branch('HasFocus','Open','PhoneOpen');g.exec('HasData','HasFocus');g.exec('HasFocus','result','else');g.call('Key','GetKey',INPUT);g.link('entry','InKeyEvent','Key','Input');g.call('Handled','Handled',UI);g.node('Done','return');g.link('Handled','ReturnValue','Done','ReturnValue');last='HasFocus';edge='then'
 for i,(key,fn) in enumerate(actions):
  tag='Key'+str(i);g.call(tag,'EqualEqual_KeyKey',INPUT,B=key);g.link('Key','ReturnValue',tag,'A');g.branch(tag+'Matches',tag);g.exec(last,tag+'Matches',edge);g.call(tag+'Action',fn);g.exec(tag+'Matches',tag+'Action');g.exec(tag+'Action','Done');last=tag+'Matches';edge='else'
 g.exec(last,'result',edge);g.build(name,override=True)
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert not any(x['native_calls'] for x in audit['graphs']);(r/'work/pure_phone_control_bindings.json').write_text(json.dumps({'status':'STAGING_COMPILED','buttons':buttons,'bindings':bindings,'binding_count':len(bindings),'keyboard_events':True,'pending':['Skill-tree spatial arrow navigation polish','Map click targeting and controller cursor','Garage preview','Runtime interaction/visual verification']},indent=2));unreal.log('PURE_PHONE_CONTROL_BINDINGS_PASS buttons='+str(buttons)+' bindings='+str(len(bindings)))
