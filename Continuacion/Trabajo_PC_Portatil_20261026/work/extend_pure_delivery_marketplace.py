import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};source=(r/'work/build_pure_delivery_data_core.py').read_text(encoding='utf-8-sig');exec(compile(source[:source.index('# Capture')],'PureDeliverySetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'});baseGraph=Graph;P=bp.generated_class().get_path_name();known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in {'ResidentialRoutes':E.get_array_type(order),'CandidateRoutes':E.get_array_type(order),'OfferLifetime':real,'OfferInterval':real,'MarketRefreshRemaining':real}.items():
 if n not in known:assert E.add_member_variable(bp,n,t)
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('OfferLifetime',30.);c.set_editor_property('OfferInterval',12.)
class Graph(baseGraph):
 def build(self,name):
  for node in self.nodes:
   if node.get('kind')=='set' and node.get('var')=='State':
    value=node.get('defaults',{}).get('State');values={'Idle':'0','Offered':'1','Pickup':'2','Dropoff':'3'}
    if value in values:node['defaults']['State']=values[value]
  return super().build(name)
# World routing supplies immutable candidate routes; the marketplace owns offer selection and expiration.
g=Graph();g.get('ResidentialRoutes');g.link('ResidentialRoutes','ResidentialRoutes','result','ReturnValue');g.exec('entry','result');g.build('GetAvailableResidentialRoutes')
g=Graph();g.call('Range','MapRangeClamped',M,InRangeA='100',InRangeB='900',OutRangeA='5000',OutRangeB='50000');g.link('entry','Meters','Range','Value');g.call('Multiply','Multiply_DoubleDouble',M);g.link('Range','ReturnValue','Multiply','A');g.link('entry','Multiplier','Multiply','B');g.call('Clamp','FClamp',M,Min='5000',Max='50000');g.link('Multiply','ReturnValue','Clamp','Value');g.call('Pay','Round',M);g.link('Clamp','ReturnValue','Pay','A');g.link('Pay','ReturnValue','result','ReturnValue');g.exec('entry','result');g.build('RewardForDistance')
def sourcebody(filename):
 s=(r/'work'/filename).read_text(encoding='utf-8-sig');s=s[s.index('g=Graph()'):];end=s.find('assert unreal.EditorAssetLibrary.save_loaded_asset')
 if end<0:end=s.find('unreal.EditorAssetLibrary.save_loaded_asset')
 assert end>0;return s[:end]
class IdleGraph(Graph):
 def build(self,n):return super().build(n) if n=='EnterIdle' else {'skipped':n}
exec(compile(sourcebody('migrate_lifecycle_blueprints.py'),'PureIdle','exec'),{'Graph':IdleGraph,'M':M,'G':G,'T':d.T,'A':A,'reports':[]})
exec(compile(sourcebody('migrate_offer_expiration_blueprint.py'),'PureOfferExpiration','exec'),{'Graph':Graph,'M':M,'G':G,'T':d.T,'A':A,'reports':[]})
exec(compile(sourcebody('migrate_residential_market_blueprint.py'),'PureOfferMarketplace','exec'),{'Graph':Graph,'M':M,'G':G,'T':d.T,'A':A,'reports':[]})
class LifecycleGraph(Graph):
 def build(self,n):return super().build(n) if n in ['UpdateMarketplace','InitializeGameplay'] else {'skipped':n}
exec(compile(sourcebody('migrate_lifecycle_blueprints.py'),'PureDeliveryLifecycle','exec'),{'Graph':LifecycleGraph,'M':M,'G':G,'T':d.T,'A':A,'reports':[]})
exec(compile(sourcebody('migrate_offer_selection_blueprints.py'),'PureOfferSelection','exec'),{'Graph':Graph,'M':M,'G':G,'T':d.T,'A':A,'reports':[]})
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert not any(x['native_calls'] for x in audit['graphs']);(r/'work/pure_delivery_marketplace.json').write_text(json.dumps({'status':'STAGING_NOT_PROMOTED','world_route_assembler_pending':True,'functions':len(audit['graphs']),'graphs':reports,'audit':audit},indent=2));unreal.log('PURE_DELIVERY_MARKETPLACE_BUILD_PASS functions='+str(len(audit['graphs'])))
