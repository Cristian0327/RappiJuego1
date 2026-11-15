import unreal,sys,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;CORE='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';R='/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider.BP_BlueprintRider_C';M=d.M;K='/Script/Engine.KismetSystemLibrary'
def basic(n):return E.get_basic_type_by_name(n)
bp=unreal.load_asset(R.rsplit('.',1)[0]);known=[str(x) for x in E.list_member_variable_names(bp)]
for name in ['SceneQueryAge']:
 if name not in known:assert E.add_member_variable(bp,name,basic('real'))
assert E.compile_blueprint(bp)
# Rebuild only the existing player frame, preserving all mounting and motion functions.
s=(r/'work/enable_pure_rider_frame.py').read_text(encoding='utf-8-sig');s=s[s.index('# Character frame'):];s=s.replace("[('Store','UpdateInsideStore'),('Market','UpdateMarketplace'),('Boost','UpdateBoost'),('Hold','AdvanceHeldAction')]","[('Boost','UpdateBoost'),('Hold','AdvanceHeldAction')]")
s=s.replace("g.exec('Ready','Store');", "g.exec('Ready','Boost');")
s=s.replace("g.exec('VehicleArt','result');g.build('ReceiveTick')", """
g.exec('VehicleArt','result')
# Spatial shop queries and marketplace accounting need not run at display frequency.
g.get('SceneQueryAge');g.call('SlowAge','Add_DoubleDouble',M);g.link('SceneQueryAge','SceneQueryAge','SlowAge','A');g.link('entry','DeltaSeconds','SlowAge','B');g.setter('KeepSlowAge','SceneQueryAge','SlowAge');g.call('SlowDue','GreaterEqual_DoubleDouble',M,B='.15');g.link('SceneQueryAge','SceneQueryAge','SlowDue','A');g.branch('SlowQueries','SlowDue');g.exec('KeepSlowAge','SlowQueries');g.exec('SlowQueries','Boost','else');g.call('Store','UpdateInsideStore',CORE);g.link('Delivery','Delivery','Store','self');g.exec('SlowQueries','Store');g.call('Market','UpdateMarketplace',CORE);g.link('Delivery','Delivery','Market','self');g.link('SceneQueryAge','SceneQueryAge','Market','Dt');g.exec('Store','Market');g.setter('ResetSlowAge','SceneQueryAge',value='0');g.exec('Market','ResetSlowAge');g.exec('ResetSlowAge','Boost')
g.links=[x for x in g.links if x not in [['HUD','then','Boost','execute'],['Ready','then','Boost','execute']]];g.exec('HUD','KeepSlowAge');g.exec('Ready','KeepSlowAge')
g.build('ReceiveTick')""")
# Imported Graph helper has the same API as the frame builder, including native override inference.
class Graph(d.Graph):
 def build(self,name,**kwargs):return super().build(name)
exec(compile(s,'BudgetRiderSpatialQueries','exec'));unreal.log('PURE_RIDER_SPATIAL_QUERY_BUDGET_PASS')
