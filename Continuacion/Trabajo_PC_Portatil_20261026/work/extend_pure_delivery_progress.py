import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};src=(r/'work/build_pure_delivery_data_core.py').read_text(encoding='utf-8-sig');exec(compile(src[:src.index('# Capture')],'PureDeliverySetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k not in ['__builtins__']});baseGraph=Graph
remap['/Script/BogotaVoxel.BogotaPlayer']='/Script/Engine.Character'
known=[str(x) for x in E.list_member_variable_names(bp)];extra={n:real for n in ['Drain','Regen','BikeEnergy','MotoEnergy']};extra.update({n:boolean for n in ['InfiniteBoost','PhoneOpen','HasWaypoint']});extra['StateRevision']=integer;extra['Waypoint']=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'));extra['StatusMessage']=E.get_basic_type_by_name('text')
for n,t in extra.items():
 if n not in known:assert E.add_member_variable(bp,n,t)
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class())
for n,v in [('Drain',20.),('Regen',15.),('BikeEnergy',100.),('MotoEnergy',100.)]:c.set_editor_property(n,v)
class Graph(baseGraph):
 def build(self,name):
  for node in self.nodes:
   if node.get('kind')=='set':
    val=node.get('defaults',{}).get(node.get('var'));mapping={'Bicycle':'0','Motorcycle':'1'} if node.get('var')=='Vehicle' else {'Idle':'0','Offered':'1','Pickup':'2','Dropoff':'3'} if node.get('var')=='State' else {}
    if val in mapping:node['defaults'][node['var']]=mapping[val]
  return super().build(name)
# Own Blueprint dispatcher preserves UI event notifications without a native delegate signature.
if 'OnChanged' not in [str(x) for x in E.list_event_dispatchers(bp)]:assert E.add_event_dispatcher(bp,'OnChanged')
assert E.compile_blueprint(bp)
g=Graph();g.get('StateRevision');g.call('Next','Add_IntInt',M,B='1');g.link('StateRevision','StateRevision','Next','A');g.setter('Revision','StateRevision','Next');g.exec('entry','Revision');g.node('Notify','delegate',var='OnChanged');g.exec('Revision','Notify');g.exec('Notify','result');g.build('Changed')
g=Graph();g.call('Owner','GetOwner','/Script/Engine.ActorComponent');g.node('Character','cast',type='/Script/Engine.Character');g.link('Owner','ReturnValue','Character','Object');g.link('Character','AsCharacter','result','ReturnValue');g.exec('entry','result');g.build('GetRider')
# Serialize only the new engine SaveGame Blueprint. Legacy profile conversion is deferred until promotion.
source=(r/'work/migrate_profile_blueprints.py').read_text(encoding='utf-8-sig');body=source[source.index('def field'):source.index('unreal.EditorAssetLibrary.save_loaded_asset')];body=body.replace('AsDelivery Save','AsBP Delivery Profile').replace("B='1');g.link(version,'Version','Supported'","B='2');g.link(version,'Version','Supported'")
ns={'Graph':Graph,'SAVE':'/Game/Delivery/BlueprintSchema/BP_DeliveryProfile.BP_DeliveryProfile_C','U':'/Script/Engine.GameplayStatics','A':A,'SYS':S,'M':M,'T':d.T,'G':G,'reports':[]};exec(compile(body,'PureBlueprintProfileAlgorithms','exec'),ns)
class SelectGraph(Graph):
 def build(self,name):
  if name in ['RebuildStats','PurchaseUpgrade','ClearWaypoint']:return super().build(name)
  return {'skipped':name}
source=(r/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig');body=source[source.index('reports=[]')+len('reports=[]'):source.index('unreal.EditorAssetLibrary.save_loaded_asset')];ns={'Graph':SelectGraph,'M':M,'G':G,'T':d.T,'A':A,'reports':[]};exec(compile(body,'PureProgressionAlgorithms','exec'),ns)
# Vehicle purchasing, equipping and repainting retain the current rules, with plain byte vehicle IDs.
class SelectVehicleGraph(Graph):
 def build(self,name):
  if name in ['BuyVehicle','EquipVehicle','PaintVehicle']:return super().build(name)
  return {'skipped':name}
source=(r/'work/migrate_vehicle_shop_phone_blueprints.py').read_text(encoding='utf-8-sig');body=source[source.index('def vehicle_row'):source.index('unreal.EditorAssetLibrary.save_loaded_asset')];ns={'Graph':SelectVehicleGraph,'M':M,'G':G,'T':d.T,'A':A,'MAP':'/Script/Engine.BlueprintMapLibrary','SYS':S,'reports':[]};exec(compile(body,'PureVehicleOwnershipAlgorithms','exec'),ns)
source=(r/'work/migrate_vehicle_waypoint_blueprints.py').read_text(encoding='utf-8-sig');body=source[source.index('g=Graph()'):source.index('unreal.EditorAssetLibrary.save_loaded_asset')]
class SelectWaypointGraph(Graph):
 def build(self,name):
  if name in ['SwitchVehicle','SetWaypoint']:return super().build(name)
  return {'skipped':name}
ns={'Graph':SelectWaypointGraph,'M':M,'G':G,'T':d.T,'A':A,'reports':[]};exec(compile(body,'PureVehicleAndWaypointAlgorithms','exec'),ns)
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert not any(x['native_calls'] for x in audit['graphs']);(r/'work/pure_delivery_progress_core.json').write_text(json.dumps({'status':'STAGING_NOT_PROMOTED','asset':bp.get_path_name(),'graphs':reports,'audit':audit},indent=2));unreal.log('PURE_DELIVERY_PROGRESS_CORE_BUILD_PASS functions='+str(len(audit['graphs'])))
