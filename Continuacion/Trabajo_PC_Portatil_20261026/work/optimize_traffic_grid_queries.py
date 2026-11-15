import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;s=(r/'work/integrate_pure_traffic_spatial_neighbors.py').read_text(encoding='utf-8-sig');s=s[:s.index('# Integrate via the signal step source')];s=s.replace('range(140)','range(560)').replace("B='140'","B='560'").replace("B='6000'","B='3000'").replace("('X',42000,13)","('X',42000,27)").replace("('Y',30000,9)","('Y',30000,19)").replace("[('X',14),('Y',10)]","[('X',28),('Y',20)]").replace("B='10'","B='20'")
needle="assert E.compile_blueprint(bp);cdo="
replacement="""if 'UsedCells' not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,'UsedCells',E.get_array_type(E.get_object_reference_type(unreal.load_class(None,C))))
for name in ['QueryX','QueryY']:
 if name not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,name,E.get_basic_type_by_name('int'))
assert E.compile_blueprint(bp);cdo="""
assert needle in s;s=s.replace(needle,replacement)
s=s.replace("g=d.Graph();g.get('TrafficCells');g.get('Vehicles');g.call('Count'","g=d.Graph();g.get('UsedCells');g.get('TrafficCells');g.get('Vehicles');g.call('Count'")
s=s.replace("g.link('TrafficCells','TrafficCells','EachCell','Array')","g.link('UsedCells','UsedCells','EachCell','Array')")
s=s.replace("g.link('EachCell','Completed','EachVehicle','Exec')","g.call('ClearUsed','Array_Clear',AL);g.link('UsedCells','UsedCells','ClearUsed','TargetArray');g.link('EachCell','Completed','ClearUsed','execute');g.link('ClearUsed','then','EachVehicle','Exec')")
s=s.replace("g.exec(last,'Register');g.link('EachVehicle','Completed','result','execute')","g.exec(last,'Register');g.call('RememberUsed','Array_AddUnique',AL);g.link('UsedCells','UsedCells','RememberUsed','TargetArray');g.link('Cell','Item','RememberUsed','NewItem');g.exec('Register','RememberUsed');g.link('EachVehicle','Completed','result','execute')")
needle="build(g,'NearbyTrafficClearance',[{'name':'Visitor'"
replacement="""g.links.remove(['Each','LoopBody','InsideGrid','execute'])
for axis in ['X','Y']:
 g.get('Query'+axis);g.setter('StoreQuery'+axis,'Query'+axis,axis+'Candidate')
 for link in g.links:
  if link[0]==axis+'Candidate' and link[1]=='ReturnValue' and link[2]!='StoreQuery'+axis:link[0]='Query'+axis;link[1]='Query'+axis
g.link('Each','LoopBody','StoreQueryX','execute');g.exec('StoreQueryX','StoreQueryY');g.exec('StoreQueryY','InsideGrid');build(g,'NearbyTrafficClearance',[{'name':'Visitor'"""
assert needle in s;s=s.replace(needle,replacement);exec(compile(s,'CachedThreeMeterTrafficGrid','exec'));assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('TRAFFIC_30M_GRID_OCCUPIED_ONLY_AND_CACHED_QUERIES_READY')
