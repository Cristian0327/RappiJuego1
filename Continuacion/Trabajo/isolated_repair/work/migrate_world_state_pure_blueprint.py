import unreal,sys,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BlueprintWorld';name='BP_WorldState';path=folder+'/'+name;f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else T.create_asset(name,folder,unreal.Blueprint,f);known=[str(x) for x in E.list_member_variable_names(bp)]
for n in ['Elapsed','CycleMinutes','Hour','CycleSeconds']:
 if n not in known:E.add_member_variable(bp,n,E.get_basic_type_by_name('real'))
if 'GameDay' not in known:E.add_member_variable(bp,'GameDay',E.get_basic_type_by_name('int'))
if 'TrafficPaintPalette' not in known:E.add_member_variable(bp,'TrafficPaintPalette',E.get_array_type(E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.LinearColor'))))
E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class())
for n,v in {'Elapsed':0,'CycleMinutes':24,'Hour':9,'CycleSeconds':180,'GameDay':1}.items():c.set_editor_property(n,v)
M=d.M;Graph=d.Graph
class PureGraph(Graph):
 def build(self,name):
  spec={'nodes':self.nodes,'links':self.links,'variables':self.variables,'signature_owner':'/Script/BogotaVoxel.BogotaCity'}
  ok=unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps(spec))
  if not ok:(r/'work/failed_pure_world_signature.json').write_text(unreal.DeliveryEditorLibrary.audit_blueprint(bp))
  assert ok,name
  return {'function':name,'nodes':len(self.nodes)+2}
Graph=PureGraph
s=(r/'work/migrate_world_blueprints.py').read_text(encoding='utf-8-sig');s=s[s.index("reports=[];A="):s.index('colors=')];s=s.replace("[('AdvanceClock',False),('AdvanceTime',True)]","[('AdvanceClock',False)]");exec(compile(s,'PureWorldStateNodes','exec'))
colors=[(.82,.84,.86),(.012,.018,.026),(.14,.17,.20),(.56,.60,.65),(.66,.025,.035),(.025,.15,.55),(.025,.31,.20),(.52,.32,.12),(.96,.58,.025),(.26,.08,.34),(.08,.48,.52),(.65,.70,.58)];c=unreal.get_default_object(bp.generated_class());c.set_editor_property('TrafficPaintPalette',[unreal.LinearColor(*x,1) for x in colors]);d.bp=bp;g=d.Graph();g.get('Elapsed');g.get('CycleSeconds');g.call('NextElapsed','Add_DoubleDouble',M);g.link('Elapsed','Elapsed','NextElapsed','A');g.link('entry','DeltaSeconds','NextElapsed','B');g.setter('ElapsedNow','Elapsed','NextElapsed');g.exec('entry','ElapsedNow');g.call('Clock','AdvanceClock',bp.generated_class().get_path_name());g.link('entry','DeltaSeconds','Clock','Dt');g.exec('ElapsedNow','Clock');g.call('ReadHour','HourForCycle',bp.generated_class().get_path_name());g.link('CycleSeconds','CycleSeconds','ReadHour','Seconds');g.setter('SetHour','Hour','ReadHour');g.exec('Clock','SetHour');g.exec('SetHour','result');g.build('ReceiveTick');assert E.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(bp));assert audit['parent']=='/Script/Engine.Actor' and not any(x['native_calls'] for x in audit['graphs']);(r/'work/pure_world_state_audit.json').write_text(json.dumps(audit,indent=2));unreal.log('PURE_WORLD_STATE_CLOCK_DISTRICTS_SIGNALS_PAINT_PASS')
