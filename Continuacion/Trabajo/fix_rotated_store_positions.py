import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
import shutil
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_new_map/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore.uasset';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(r/'RappiJuego1/Content/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore.uasset',backup)
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/Stores/BP_DeliveryStore');d.bp=bp;M=d.M;A='/Script/Engine.Actor';V='/Script/CoreUObject.Vector';rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(unreal.load_asset('/Game/Delivery/BlueprintSchema/Tables/DT_StoreThemes')));Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/store_themes.json').write_text(json.dumps(rows,indent=2))
def build(g,n,params):
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,n,json.dumps({'nodes':g.nodes,'links':g.links,'parameters':params,'pure':True,'const':True}));assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
vecout={'name':'ReturnValue','category':'struct','object':V,'out':True}
g=d.Graph();g.get('HalfDepth');g.call('Origin','GetTransform',A);g.call('Offset','MakeVector',M);g.link('HalfDepth','HalfDepth','Offset','Y');g.call('Relative','Add_VectorVector',M);g.link('Offset','ReturnValue','Relative','A');g.link('entry','Local','Relative','B');g.call('World','TransformLocation',M);g.link('Origin','ReturnValue','World','T');g.link('Relative','ReturnValue','World','Location');g.link('World','ReturnValue','result','ReturnValue');g.exec('entry','result');build(g,'InteriorPosition',[{'name':'Local','category':'struct','object':V},vecout])
g=d.Graph();g.get('CounterDistanceMeters');g.call('Cm','Multiply_DoubleDouble',M,B='100');g.link('CounterDistanceMeters','CounterDistanceMeters','Cm','A');g.call('Behind','Subtract_DoubleDouble',M,B='105');g.link('Cm','ReturnValue','Behind','A');g.call('Local','MakeVector',M,X='150',Z='5');g.link('Behind','ReturnValue','Local','Y');g.call('Transform','GetTransform',A);g.call('World','TransformLocation',M);g.link('Transform','ReturnValue','World','T');g.link('Local','ReturnValue','World','Location');g.link('World','ReturnValue','result','ReturnValue');g.exec('entry','result');build(g,'CheckoutPosition',[vecout])
g=d.Graph();g.get('HalfWidth');g.get('HalfDepth');g.call('Transform','GetTransform',A);g.call('Local','InverseTransformLocation',M);g.link('Transform','ReturnValue','Local','T');g.link('entry','Position','Local','Location');g.call('Axes','BreakVector',M);g.link('Local','ReturnValue','Axes','InVec');g.call('AbsX','Abs',M);g.link('Axes','X','AbsX','A');g.call('Width','Subtract_DoubleDouble',M,B='15');g.link('HalfWidth','HalfWidth','Width','A');g.call('MaxY','Multiply_DoubleDouble',M,B='2');g.link('HalfDepth','HalfDepth','MaxY','A');g.call('Back','Subtract_DoubleDouble',M,B='10');g.link('MaxY','ReturnValue','Back','A');checks=[]
for n,axis,fn,val,node in [('InsideX','X','Less_DoubleDouble',None,'Width'),('Front','Y','Greater_DoubleDouble','20',None),('Rear','Y','Less_DoubleDouble',None,'Back'),('Floor','Z','Greater_DoubleDouble','0',None),('Ceiling','Z','Less_DoubleDouble','470',None)]:
 g.call(n,fn,M,**({'B':val} if val else {}));g.link('AbsX' if axis=='X' else 'Axes','ReturnValue' if axis=='X' else axis,n,'A')
 if node:g.link(node,'ReturnValue',n,'B')
 checks.append(n)
last=checks[0]
for i,n in enumerate(checks[1:]):g.call('And'+str(i),'BooleanAND',M);g.link(last,'ReturnValue','And'+str(i),'A');g.link(n,'ReturnValue','And'+str(i),'B');last='And'+str(i)
g.link(last,'ReturnValue','result','ReturnValue');g.exec('entry','result');build(g,'ContainsVisitor',[{'name':'Position','category':'struct','object':V},{'name':'ReturnValue','category':'bool','out':True}]);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('NEW_MAP_ROTATED_STORES_READY')

f=r/'work/pure_store_graph_specs/UpdateCustomer.json'
if f.exists():
 spec=json.loads(f.read_text());spec['nodes'].append({'id':'StoreTransform','kind':'call','fn':'GetTransform','owner':A,'defaults':{}})
 for n in spec['nodes']:
  if n['id'] in ['WorldNext','StartWorld']:n['fn']='TransformLocation';n['defaults']={}
 for l in spec['links']:
  if l[2] in ['WorldNext','StartWorld']:
   if l[3]=='A':l[0]='StoreTransform';l[1]='ReturnValue';l[3]='T'
   elif l[3]=='B':l[3]='Location'
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'UpdateCustomer',json.dumps(spec));assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('NEW_MAP_ROTATED_STORE_CUSTOMERS_READY')
