import unreal,sys,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;bp=unreal.load_asset('/Game/World/BP_BogotaCity');pure=unreal.load_asset('/Game/World/BlueprintWorld/BP_WorldState');assert bp and pure;P=pure.generated_class().get_path_name();backup=r/'Recuperacion_Migracion_Blueprints/2026-10-17_world_core_bridge/BP_BogotaCity.uasset';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(r/'RappiJuego1/Content/World/BP_BogotaCity.uasset',backup)
if 'WorldStateBridge' not in [str(x) for x in E.list_member_variable_names(bp)]:E.add_member_variable(bp,'WorldStateBridge',E.get_object_reference_type(pure.generated_class()))
E.compile_blueprint(bp);M=d.M;Native='/Script/BogotaVoxel.BogotaCity';reports=[]
class BridgeGraph(d.Graph):
 def build(self,name):
  # Retain the original Blueprint path for editor CDO calls and old scene compatibility.
  outgoing=[x for x in self.links if x[0]=='entry' and x[1]=='then'];self.links=[x for x in self.links if x not in outgoing];self.get('WorldStateBridge');self.call('BridgeValid','IsValid','/Script/Engine.KismetSystemLibrary');self.link('WorldStateBridge','WorldStateBridge','BridgeValid','Object');self.branch('UsePureWorld','BridgeValid');self.exec('entry','UsePureWorld')
  for old in outgoing:self.link('UsePureWorld','else',old[2],old[3])
  fields={'TrafficPaintFor':['TrafficPaintPalette'],'TrafficNSGreen':['Elapsed'],'TrafficEWGreen':['Elapsed'],'AdvanceClock':['CycleMinutes','CycleSeconds','GameDay']}.get(name,[]);last='UsePureWorld'
  existing={x['id'] for x in self.nodes}
  for field in fields:
   if field not in existing:self.get(field)
   n='BridgeIn'+field;self.node(n,'setfield',owner=P,var=field);self.link('WorldStateBridge','WorldStateBridge',n,'self');self.link(field,field,n,field);self.exec(last,n);last=n
  self.call('PureWorldFunction',name,P);self.link('WorldStateBridge','WorldStateBridge','PureWorldFunction','self')
  for param in {'TrafficPaintFor':['VehicleIndex'],'HourForCycle':['Seconds'],'DistrictAt':['P'],'AdvanceClock':['Dt']}.get(name,[]):self.link('entry',param,'PureWorldFunction',param)
  if name=='AdvanceClock':
   self.exec(last,'PureWorldFunction');last='PureWorldFunction'
   for field in ['CycleSeconds','GameDay']:
    n='BridgeOut'+field;self.node(n,'getfield',owner=P,var=field);self.link('WorldStateBridge','WorldStateBridge',n,'self');self.setter('Apply'+field,field,n,field);self.exec(last,'Apply'+field);last='Apply'+field
  self.node('PureResult','return')
  if name!='AdvanceClock':self.link('PureWorldFunction','ReturnValue','PureResult','ReturnValue')
  self.exec(last,'PureResult');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps({'nodes':self.nodes,'links':self.links,'variables':self.variables})),name
  return {'function':name,'active_pure_blueprint':P}
Graph=BridgeGraph;s=(r/'work/migrate_world_blueprints.py').read_text(encoding='utf-8-sig');s=s[s.index("reports=[];A="):s.index('colors=')];s=s.replace("[('AdvanceClock',False),('AdvanceTime',True)]","[('AdvanceClock',False)]");exec(compile(s,'WorldCoreBlueprintBridge','exec'))
# The native compatibility shell creates the independent state actor before its own world setup.
d.bp=bp;g=d.Graph();G='/Script/Engine.GameplayStatics';S='/Script/Engine.KismetSystemLibrary';A='/Script/Engine.Actor';g.call('Find','GetActorOfClass',G,ActorClass=P);g.exec('entry','Find');g.call('Found','IsValid',S);g.link('Find','ReturnValue','Found','Object');g.branch('Exists','Found');g.exec('Find','Exists');g.node('Existing','cast',type=P);g.link('Find','ReturnValue','Existing','Object');g.setter('UseExisting','WorldStateBridge','Existing','AsBP World State');g.exec('Exists','UseExisting');g.call('Transform','MakeTransform',M,Scale='(X=1,Y=1,Z=1)');g.call('Spawn','BeginDeferredActorSpawnFromClass',G,ActorClass=P,CollisionHandlingOverride='AlwaysSpawn');g.link('Transform','ReturnValue','Spawn','SpawnTransform');g.exec('Exists','Spawn','else');g.call('Finish','FinishSpawningActor',G);g.link('Spawn','ReturnValue','Finish','Actor');g.link('Transform','ReturnValue','Finish','SpawnTransform');g.exec('Spawn','Finish');g.node('Created','cast',type=P);g.link('Finish','ReturnValue','Created','Object');g.setter('UseNew','WorldStateBridge','Created','AsBP World State');g.exec('Finish','UseNew');g.get('WorldStateBridge');g.call('DisableIndependentTick','SetActorTickEnabled',A,bEnabled='false');g.link('WorldStateBridge','WorldStateBridge','DisableIndependentTick','self');g.exec('UseExisting','DisableIndependentTick');g.exec('UseNew','DisableIndependentTick');g.exec('DisableIndependentTick','result');g.build('ReceiveBeginPlay');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/world_core_bridge_integration.json').write_text(json.dumps({'status':'INTEGRATED_COMPATIBILITY_SHELL_REMAINS','functions':reports},indent=2));unreal.log('WORLD_CORE_PURE_BLUEPRINT_BRIDGE_INTEGRATED_PASS')
