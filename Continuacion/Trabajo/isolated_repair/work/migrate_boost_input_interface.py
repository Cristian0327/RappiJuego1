import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Delivery/Interfaces';name='BPI_DeliveryRiderInput';path=folder+'/'+name;interface=unreal.load_asset(path) or T.create_asset(name,folder,unreal.Blueprint,unreal.BlueprintInterfaceFactory());spec={'parameters':[{'name':n,'category':'bool','out':True} for n in ['Mounted','WantsBoost','HasThrottle']],'nodes':[],'links':[['entry','then','result','execute']]};assert unreal.DeliveryEditorLibrary.build_logic_graph(interface,'QueryDeliveryInputState',json.dumps(spec));assert E.compile_blueprint(interface);assert unreal.EditorAssetLibrary.save_loaded_asset(interface,only_if_is_dirty=False);I=interface.generated_class().get_path_name();backup=r/'Recuperacion_Migracion_Blueprints/2026-10-17_boost_interface';backup.mkdir(exist_ok=True)
for rel in ['Delivery/Vehicles/BP_DeliveryRider.uasset','Delivery/Core/BPC_DeliveryGameplay.uasset']:
 p=r/'RappiJuego1/Content'/rel;b=backup/p.name
 if not b.exists():shutil.copy2(p,b)
rider=unreal.load_asset('/Game/Delivery/Vehicles/BP_DeliveryRider');g=d.Graph();g.get('Riding');g.get('Sprint');g.get('ForwardInput');g.call('AbsThrottle','Abs',d.M);g.link('ForwardInput','ForwardInput','AbsThrottle','A');g.call('Throttle','Greater_DoubleDouble',d.M,B='.1');g.link('AbsThrottle','ReturnValue','Throttle','A');g.link('Riding','Riding','result','Mounted');g.link('Sprint','Sprint','result','WantsBoost');g.link('Throttle','ReturnValue','result','HasThrottle');g.exec('entry','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(rider,'QueryDeliveryInputState',json.dumps({'interface_owner':I,'nodes':g.nodes,'links':g.links}));assert E.compile_blueprint(rider);assert unreal.EditorAssetLibrary.save_loaded_asset(rider,only_if_is_dirty=False)
source=(r/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig');a=source.index("g=Graph();g.variables=[{'name':'BoostUsedFrame'");b=source.index("reports.append(g.build('UpdateBoost'))",a)+len("reports.append(g.build('UpdateBoost'))");body=source[a:b];body=body.replace("g.call('Rider','GetRider')","g.call('Rider','GetOwner','/Script/Engine.ActorComponent')");old="for id,fn in [('Riding','IsRiding'),('Wants','WantsBoost'),('Throttle','HasThrottle')]:g.call(id,fn,'/Script/BogotaVoxel.BogotaPlayer');g.link('Rider','ReturnValue',id,'self')";new="g.node('InputState','message',owner=I,fn='QueryDeliveryInputState');g.link('Rider','ReturnValue','InputState','self');g.exec('Valid','InputState')\nfor id,pin in [('Riding','Mounted'),('Wants','WantsBoost'),('Throttle','HasThrottle')]:g.call(id,'EqualEqual_BoolBool',M,B='true');g.link('InputState',pin,id,'A')";assert old in body;body=body.replace(old,new).replace("g.exec('Valid','Activate')","g.exec('InputState','Activate')")
for asset,pure in [('/Game/Delivery/Core/BPC_DeliveryGameplay',False),('/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore',True)]:
 bp=unreal.load_asset(asset)
 if pure:
  known=[str(x) for x in E.list_member_variable_names(bp)]
  for n,t in {**{n:E.get_basic_type_by_name('bool') for n in ['bExhausted','bHadBoost','BoostUsedFrame']},'RegenDelayRemaining':E.get_basic_type_by_name('real')}.items():
   if n not in known:assert E.add_member_variable(bp,n,t)
   E.set_blueprint_variable_instance_editable(bp,n,True)
  assert E.compile_blueprint(bp)
 class Graph(d.Graph):
  def build(self,name):
   # Delta is sanitized once; all calculations use the same frame duration.
   links=[x[:] for x in self.links];self.call('SafeDelta','FMax',d.M,B='0');self.link('entry','Dt','SafeDelta','A')
   for x in links:
    if x[0]=='entry' and x[1]=='Dt':self.links.remove(x);self.link('SafeDelta','ReturnValue',x[2],x[3])
   self.call('SupportsInput','DoesImplementInterface','/Script/Engine.KismetSystemLibrary',Interface=I);self.link('Rider','ReturnValue','SupportsInput','TestObject');self.call('ValidInput','BooleanAND',d.M);self.link('ValidRider','ReturnValue','ValidInput','A');self.link('SupportsInput','ReturnValue','ValidInput','B');self.links.remove(['ValidRider','ReturnValue','Valid','Condition']);self.link('ValidInput','ReturnValue','Valid','Condition')
   for node in self.nodes:
    if node.get('kind')=='call' and not node.get('owner'):node['owner']=bp.generated_class().get_path_name()
   s={'nodes':self.nodes,'links':self.links,'variables':self.variables}
   if pure:s['signature_owner']='/Script/BogotaVoxel.DeliveryComponent'
   assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps(s));(r/('work/pure_boost_graph.json' if pure else 'work/main_boost_graph.json')).write_text(json.dumps(s,indent=2));return {'function':name,'nodes':len(self.nodes)}
 exec(compile(body,'InterfaceBoostBlueprint','exec'),{'Graph':Graph,'M':d.M,'G':d.G,'T':d.T,'A':'/Script/Engine.KismetArrayLibrary','I':I,'reports':[]});assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
 audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));boost=next(x for x in audit['graphs'] if x['name']=='UpdateBoost');assert not boost['native_calls'],boost
(r/'work/boost_interface_migration.json').write_text(json.dumps({'status':'INTEGRATED_AND_PURE_CORE_IMPLEMENTED','interface':I,'delta_clamped_nonnegative':True,'native_input_calls_removed':4,'main_native_base_still_pending':True},indent=2));unreal.log('BOOST_INPUT_INTERFACE_BLUEPRINT_BUILD_PASS')
