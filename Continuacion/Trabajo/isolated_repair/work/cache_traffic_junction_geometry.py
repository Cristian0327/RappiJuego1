import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficManager');E=unreal.BlueprintEditorLibrary
known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in [('JunctionForward',E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'))),('JunctionPoint',E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'))),('JunctionX',E.get_basic_type_by_name('int')),('JunctionY',E.get_basic_type_by_name('int')),('JunctionAlongX',E.get_basic_type_by_name('bool'))]:
 if n not in known:assert E.add_member_variable(bp,n,t)
assert E.compile_blueprint(bp)
s=(r/'work/optimize_pure_traffic_junction_lookup.py').read_text(encoding='utf-8-sig')
s=s.replace("['Junctions','BestJunction','BestAhead']","['Junctions','BestJunction','BestAhead','JunctionForward','JunctionPoint','JunctionX','JunctionY','JunctionAlongX']")
s=s.replace("g.exec('ResetDistance','Search')", "g.setter('CacheForward','JunctionForward','Direction');g.setter('CachePoint','JunctionPoint','NextPosition','NextPosition');g.setter('CacheAxis','JunctionAlongX','NS');g.setter('CacheX','JunctionX','XIndex');g.setter('CacheY','JunctionY','YIndex');g.exec('ResetDistance','CacheForward');g.exec('CacheForward','CachePoint');g.exec('CachePoint','CacheAxis');g.exec('CacheAxis','CacheX');g.exec('CacheX','CacheY');g.exec('CacheY','Search')")
s=s.replace("g.link('Direction','ReturnValue','DirAxes'", "g.link('JunctionForward','JunctionForward','DirAxes'")
s=s.replace("('Direction','ReturnValue')","('JunctionForward','JunctionForward')").replace("('NextPosition','NextPosition')","('JunctionPoint','JunctionPoint')")
s=s.replace("('XIndex','ReturnValue')","('JunctionX','JunctionX')").replace("('YIndex','ReturnValue')","('JunctionY','JunctionY')")
s=s.replace("g.link('XIndex','ReturnValue',tag", "g.link('JunctionX','JunctionX',tag").replace("g.link('YIndex','ReturnValue',tag", "g.link('JunctionY','JunctionY',tag").replace("g.link('NS','ReturnValue',tag", "g.link('JunctionAlongX','JunctionAlongX',tag")
exec(compile(s,'CachedThreeCandidateJunctionSearch','exec'))
unreal.log('JUNCTION_QUERY_TRIG_AND_GRID_CACHED_ONCE')
