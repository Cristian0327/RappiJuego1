import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/extend_pure_order_lifecycle.py').read_text();exec(compile(s[:s.index('# Circular order completion')],'PureOrderSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'});guid=E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Guid'));members(core,{'HeldState':basic('byte'),'HeldOrder':guid,'bPickupButton':basic('bool'),'HoldStart':basic('real'),'HoldDuration':basic('real'),'PhoneWidget':obj('/Script/UMG.UserWidget')});unreal.get_default_object(core.generated_class()).set_editor_property('HoldDuration',1.)
# Placement is requested through an engine-independent Blueprint contract.
name='BPI_DeliveryVehiclePlacement';path='/Game/Delivery/Interfaces/'+name;interface=unreal.load_asset(path) or T.create_asset(name,'/Game/Delivery/Interfaces',unreal.Blueprint,unreal.BlueprintInterfaceFactory());assert unreal.DeliveryEditorLibrary.build_logic_graph(interface,'RequestDeliveryVehicle',json.dumps({'parameters':[{'name':'ReturnValue','category':'bool','out':True}],'nodes':[],'links':[['entry','then','result','execute']]}));assert E.compile_blueprint(interface);assert unreal.EditorAssetLibrary.save_loaded_asset(interface,only_if_is_dirty=False);I=interface.generated_class().get_path_name()
# Closing an actual UserWidget restores world input, without a native phone widget class.
g=Graph();g.get('PhoneWidget');g.call('End','EndAction');g.exec('entry','End');g.setter('Closed','PhoneOpen',value='false');g.exec('End','Closed');g.call('Valid','IsValid',K);g.link('PhoneWidget','PhoneWidget','Valid','Object');g.branch('HasWidget','Valid');g.exec('Closed','HasWidget');g.call('Remove','RemoveFromParent','/Script/UMG.Widget');g.link('PhoneWidget','PhoneWidget','Remove','self');g.exec('HasWidget','Remove');g.setter('Clear','PhoneWidget',value='None');g.exec('Remove','Clear');g.exec('HasWidget','Clear','else');g.call('Rider','GetRider');g.call('Controller','GetController','/Script/Engine.Pawn');g.link('Rider','ReturnValue','Controller','self');g.node('PC','cast',type='/Script/Engine.PlayerController');g.link('Controller','ReturnValue','PC','Object');g.call('PCValid','IsValid',K);g.link('PC','AsPlayer Controller','PCValid','Object');g.branch('HasPC','PCValid');g.exec('Clear','HasPC');g.exec('HasPC','result','else');g.call('Mode','SetInputMode_GameOnly','/Script/UMG.WidgetBlueprintLibrary',bFlushInput='true');g.link('PC','AsPlayer Controller','Mode','PlayerController');g.exec('HasPC','Mode');g.node('Cursor','setfield',owner='/Script/Engine.PlayerController',var='bShowMouseCursor',defaults={'bShowMouseCursor':'false'});g.link('PC','AsPlayer Controller','Cursor','self');g.exec('Mode','Cursor');g.exec('Cursor','result');g.build('ClosePhoneForWorld',params=[])
# Declare the interdependent acceptance/hold rules before writing their bodies.
for n in ['AcceptOffer','BeginAction','AdvanceHeldAction']:
 g=Graph();g.exec('entry','result');g.build(n)
source=(r/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig');body=source[source.index('reports=[]')+len('reports=[]'):source.index('unreal.EditorAssetLibrary.save_loaded_asset')]
base=Graph
class Graph(base):
 def build(self,n):
  if n not in ['AcceptOffer','BeginAction','AdvanceHeldAction']:return {'skipped':n}
  if n=='AcceptOffer':
   for x in self.nodes:
    if x.get('id')=='PlaceVehicle':x.clear();x.update(id='PlaceVehicle',kind='message',owner=I,fn='RequestDeliveryVehicle')
    if x.get('id')=='Phone':x['fn']='ClosePhoneForWorld'
    if x.get('kind')=='make' and x.get('type')=='/Script/BogotaVoxel.ActiveDelivery':x.get('defaults',{}).pop('State',None);self.call('PickupValue','MakeLiteralByte',K,Value='2');self.link('PickupValue','ReturnValue',x['id'],'State')
   self.get('SelectedOffer') if not any(x.get('id')=='SelectedOffer' for x in self.nodes) else None
   self.call('ExplicitSelection','EqualEqual_GuidGuid',d.G);self.link('entry','ExpectedID','ExplicitSelection','A');self.link('SelectedOffer','SelectedOffer','ExplicitSelection','B');self.call('SelectedAndAvailable','BooleanAND',M);self.link('ExplicitSelection','ReturnValue','SelectedAndAvailable','A');self.link('Available','ReturnValue','SelectedAndAvailable','B')
   self.links=[x for x in self.links if x!=['Available','ReturnValue','ValidateOffer','Condition']];self.link('SelectedAndAvailable','ReturnValue','ValidateOffer','Condition')
  return super().build(n)
exec(compile(body,'PureAcceptanceAndHeldInput','exec'),{'Graph':Graph,'M':M,'G':d.G,'T':TXT,'A':AL,'bp':core,'reports':[]})
assert E.compile_blueprint(core);assert unreal.EditorAssetLibrary.save_loaded_asset(core,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(core));assert not any(g['native_calls'] for g in audit['graphs']);(r/'work/pure_order_acceptance_migration.json').write_text(json.dumps({'status':'STAGING_NOT_PROMOTED','interface':I,'functions':['AcceptOffer','BeginAction','AdvanceHeldAction','ClosePhoneForWorld'],'explicit_selection_required':True,'main_rider_placement_integration_pending':True},indent=2));unreal.log('PURE_ORDER_ACCEPTANCE_BUILD_PASS')
