from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
CELL='/Game/World/BlueprintWorld/Traffic/BP_TrafficCell.BP_TrafficCell_C';b=use(CELL);addvar(b,'CurrentGap',real);assert E.compile_blueprint(b);g=d.Graph();g.get('Vehicles');g.get('CurrentGap');g.setter('Reset','CurrentGap',value='100000000');g.exec('entry','Reset');g.node('Each','foreach');g.link('Vehicles','Vehicles','Each','Array');g.link('Reset','then','Each','Exec');op(g,'NotSelf','NotEqual_ObjectObject',('Each','Array Element'),('entry','Visitor'));g.branch('Check','NotSelf');g.link('Each','LoopBody','Check','execute');g.call('Gap','ClearanceFromVehicle',V);g.link('entry','Visitor','Gap','self');g.link('Each','Array Element','Gap','Other');op(g,'Minimum','FMin',('CurrentGap','CurrentGap'),('Gap','ReturnValue'));g.setter('Remember','CurrentGap','Minimum');g.exec('Check','Remember');g.link('Each','Completed','result','execute');g.link('CurrentGap','CurrentGap','result','ReturnValue');build(b,g,'ClearanceFor',[dict(name='Visitor',category='object',object=V),dict(name='ReturnValue',category='real',out=True)]);save(b)
exec(compile((root/'work/optimize_traffic_grid_queries.py').read_text(),'RefreshSpatialGrid','exec'),{})
# Refresh dependent call sites after replacing the function graphs.
for path in [TM,V,CELL,'/Game/World/BogotaUrban/BP_BogotaServiceSignals']:
 b=unreal.load_asset(path.split('.')[0])
 if hasattr(E,'refresh_all_nodes'):E.refresh_all_nodes(b)
 assert E.compile_blueprint(b);save(b)
unreal.log('V2_CLEARANCE_CALL_SITES_REBUILT')
