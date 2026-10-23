import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Delivery/BlueprintGameplay';name='BPC_DeliveryDataCore';path=folder+'/'+name;f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.ActorComponent);bp=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else tools.create_asset(name,folder,unreal.Blueprint,f);schema=json.loads((r/'work/blueprint_gameplay_schema.json').read_text());remap={v['source']:v['asset'] for v in schema['enums']+schema['structs']};M=d.M;G=d.G;A='/Script/Engine.KismetArrayLibrary';S='/Script/Engine.KismetSystemLibrary';D='/Script/BogotaVoxel.DeliveryComponent';P=bp.generated_class().get_path_name();reports=[]
types={};integer=E.get_basic_type_by_name('int');real=E.get_basic_type_by_name('real');boolean=E.get_basic_type_by_name('bool');named=E.get_basic_type_by_name('name');byte=E.get_basic_type_by_name('byte');order=E.get_struct_type(unreal.load_object(None,remap['/Script/BogotaVoxel.DeliveryOrder']));active=E.get_struct_type(unreal.load_object(None,remap['/Script/BogotaVoxel.ActiveDelivery']))
for n in ['Balance','BikeColor','MotoColor']:types[n]=integer
for n in ['Energy','Capacity','HoldProgress','BikeBaseSpeed','BikeBoostSpeed','MotoBoostSpeed']:types[n]=real
for n in ['bHolding','BoostActive','DeveloperMode','bValidation']:types[n]=boolean
for n in ['Purchased','OwnedModels']:types[n]=E.get_array_type(named)
for n in ['BikeModel','MotoModel']:types[n]=named
types.update(Vehicle=byte,State=byte,SelectedOffer=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Guid')),Offers=E.get_array_type(order),ActiveOrders=E.get_array_type(active),ModelColors=E.get_map_type(named,integer))
known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in types.items():
 if n not in known:assert E.add_member_variable(bp,n,t),n
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class())
for n,v in {'BikeBaseSpeed':1100.,'BikeBoostSpeed':1450.,'MotoBoostSpeed':2200.,'Capacity':100.,'Energy':100.,'BikeModel':unreal.Name('BikeCity'),'MotoModel':unreal.Name('MotoStreet')}.items():c.set_editor_property(n,v)
class Graph(d.Graph):
 def build(self,name):
  spec={'nodes':self.nodes,'links':self.links,'variables':self.variables,'signature_owner':D,'type_remap':remap}
  for n in spec['nodes']:
   if n.get('kind') in ['break','make']:n['type']=remap.get(n['type'],n['type'])
   if n.get('kind')=='call' and not n.get('owner'):n['owner']=bp.generated_class().get_path_name()
  ok=unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps(spec));assert ok,name;reports.append({'function':name,'nodes':len(self.nodes)+2});return reports[-1]
# Capture and rebuild the already-reviewed pure algorithms without touching the original component.
source=(r/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig');body=source[source.index('reports=[]')+len('reports=[]'):];body=body[:body.index('unreal.EditorAssetLibrary.save_loaded_asset')]
class SelectGraph(Graph):
 def build(self,name):
  if name in ['EndAction','Owns','GetTopSpeed','CargoCapacity','OwnsVehicle','VisualStage']:return super().build(name)
  return {'skipped':name}
ns={'Graph':SelectGraph,'bp':bp,'M':M,'G':G,'T':d.T,'A':A,'reports':[]};exec(compile(body,'ReviewedDeliveryCoreAlgorithms','exec'),ns)
# Typed table lookup nodes use Blueprint-authored rows.
for function,table in [('GetUpgradeSpec','DT_Upgrades'),('GetVehicleSpec','DT_Vehicles')]:
 g=Graph();g.node('Read','datatable',defaults={'DataTable':'/Game/Delivery/BlueprintSchema/Tables/'+table+'.'+table});g.link('entry','ID','Read','RowName');g.exec('entry','Read');g.node('Found','return',defaults={'Found':'true'});g.node('Missing','return',defaults={'Found':'false'});g.exec('Read','Found','then');g.exec('Read','Missing','RowNotFound');g.link('Read','OutRow','Found','ReturnValue');g.build(function)
for function in ['FindOffer','GetSelectedOffer','FindActiveOrderIndex']:
 g=Graph();activeLookup=function=='FindActiveOrderIndex';array='ActiveOrders' if activeLookup else 'Offers';g.get(array);g.node('Loop','foreach');g.link(array,array,'Loop','Array');g.link('entry','then','Loop','Exec');g.node('Fields','break',type='/Script/BogotaVoxel.ActiveDelivery' if activeLookup else '/Script/BogotaVoxel.DeliveryOrder');g.link('Loop','Array Element','Fields','ActiveDelivery' if activeLookup else 'DeliveryOrder');idnode='Fields'
 if activeLookup:g.node('OrderFields','break',type='/Script/BogotaVoxel.DeliveryOrder');g.link('Fields','Order','OrderFields','DeliveryOrder');idnode='OrderFields'
 g.call('Same','EqualEqual_GuidGuid',G);g.link(idnode,'ID','Same','A')
 if function=='GetSelectedOffer':g.get('SelectedOffer');g.link('SelectedOffer','SelectedOffer','Same','B')
 else:g.link('entry','ID','Same','B')
 g.branch('Matches','Same');g.link('Loop','LoopBody','Matches','execute');g.node('Found','return',defaults={'Found':'true'} if function=='GetSelectedOffer' else {});g.exec('Matches','Found');g.link('Loop','Array Index','Found','ReturnValue' if activeLookup else 'Index') if function!='GetSelectedOffer' else None
 if not activeLookup:g.link('Loop','Array Element','Found','ReturnValue')
 g.node('Missing','return',defaults={'ReturnValue':'-1'} if activeLookup else {'Found':'false'} if function=='GetSelectedOffer' else {'Index':'-1'});g.link('Loop','Completed','Missing','execute');g.build(function)
g=Graph();g.get('ModelColors');g.call('Color','Map_Find','/Script/Engine.BlueprintMapLibrary');g.link('ModelColors','ModelColors','Color','TargetMap');g.link('entry','ID','Color','Key');g.call('Clamp','Clamp',M,Min='0',Max='5');g.link('Color','Value','Clamp','Value');g.link('Clamp','ReturnValue','result','ReturnValue');g.exec('entry','result');g.build('GetModelColor')
g=Graph();g.get('bValidation');g.call('Slot','SelectString',M,A='VoxelDelivery_Blueprint_Automation_v2',B='VoxelDelivery_Blueprint_Profile_v2');g.link('bValidation','bValidation','Slot','bPickA');g.link('Slot','ReturnValue','result','ReturnValue');g.exec('entry','result');g.build('ProfileSlot')
# Duplicate-route checks include both incoming and accepted orders.
g=Graph();last='entry';lastpin='then'
for prefix,array,activeLookup in [('Offer','Offers',False),('Active','ActiveOrders',True)]:
 g.get(array);g.node(prefix+'Loop','foreach');g.link(array,array,prefix+'Loop','Array');g.link(last,lastpin,prefix+'Loop','Exec');g.node(prefix+'Fields','break',type='/Script/BogotaVoxel.ActiveDelivery' if activeLookup else '/Script/BogotaVoxel.DeliveryOrder');g.link(prefix+'Loop','Array Element',prefix+'Fields','ActiveDelivery' if activeLookup else 'DeliveryOrder');fields=prefix+'Fields'
 if activeLookup:g.node('ActiveOrder','break',type='/Script/BogotaVoxel.DeliveryOrder');g.link(fields,'Order','ActiveOrder','DeliveryOrder');fields='ActiveOrder'
 for pin in ['Pickup','Dropoff']:g.call(prefix+pin,'EqualEqual_VectorVector',M,ErrorTolerance='1');g.link('entry',pin,prefix+pin,'A');g.link(fields,pin,prefix+pin,'B')
 g.call(prefix+'Both','BooleanAND',M);g.link(prefix+'Pickup','ReturnValue',prefix+'Both','A');g.link(prefix+'Dropoff','ReturnValue',prefix+'Both','B');g.branch(prefix+'Match',prefix+'Both');g.link(prefix+'Loop','LoopBody',prefix+'Match','execute');g.returner(prefix+'Found',True);g.exec(prefix+'Match',prefix+'Found');last=prefix+'Loop';lastpin='Completed'
g.returner('Unique',False);g.link(last,lastpin,'Unique','execute');g.build('RouteAlreadyOffered')
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['parent']=='/Script/Engine.ActorComponent' and not any(g['native_calls'] for g in audit['graphs']);(r/'work/pure_delivery_data_core.json').write_text(json.dumps({'status':'STAGING_NOT_PROMOTED','asset':path,'graphs':reports,'audit':audit},indent=2));unreal.log('PURE_DELIVERY_DATA_CORE_BUILD_PASS functions='+str(len(audit['graphs'])))
