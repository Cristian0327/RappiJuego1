import unreal,json,sys,math,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;M=d.M;plan=json.loads((W/'integration_plan.json').read_text());backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_new_map';bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');parent=unreal.load_asset('/Game/World/BlueprintWorld/BP_CityGeometry')
E.reparent_blueprint(bp,parent.generated_class());assert E.compile_blueprint(bp);d.bp=bp;g=d.Graph();g.exec('entry','result');g.build('ReceiveBeginPlay');assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());b=plan['building_footprints'];c.set_editor_property('BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in b]);c.set_editor_property('BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in b]);c.set_editor_property('NorthRoads',[]);c.set_editor_property('EastRoads',[]);EL.save_loaded_asset(bp,only_if_is_dirty=False)
# The phone keeps its original shape and controls; map paint now follows the curved streets.
p='Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.uasset';dst=backup/p;dst.parent.mkdir(parents=True,exist_ok=True)
if not dst.exists():shutil.copy2(r/'RappiJuego1/Content'/p,dst)
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');d.bp=bp;PHONE=bp.generated_class().get_path_name();V='/Script/CoreUObject.Vector';V2='/Script/CoreUObject.Vector2D'
for n in ['CityRoadStarts','CityRoadEnds']:
 if n not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,n,E.get_array_type(E.get_struct_type(unreal.load_object(None,V))))
assert E.compile_blueprint(bp)
# Rebuild the existing cached map paint only, leaving the UI layout and input untouched.
s=(r/'work/build_pure_phone_map.py').read_text(encoding='utf-8-sig');s=s[:s.index('# A single widget')]+s[s.index('# Paint with standard'):];s=s.replace("g.get('MapBuildings')","g.get('MapVisibleBuildings');g.get('MapCacheCenter')").replace("g.link('MapBuildings','MapBuildings','Buildings','Array')","g.link('MapVisibleBuildings','MapVisibleBuildings','Buildings','Array')").replace("g.link('Center','ReturnValue',","g.link('MapCacheCenter','MapCacheCenter',")
old="g.call('HouseNorm','MapNormalizedPoint');g.link('Buildings','Array Element','HouseNorm','Position');g.link('MapCacheCenter','MapCacheCenter','HouseNorm','Center');g.link('Open','PhoneOpen','HouseNorm','FullMap')";new="g.call('CachedHouse','BreakVector2D',M);g.link('Buildings','Array Element','CachedHouse','InVec');g.call('HouseNorm','MakeVector2D',M);g.link('CachedHouse','X','HouseNorm','X');g.link('CachedHouse','Y','HouseNorm','Y')";assert old in s;s=s.replace(old,new)
insert="""
g.get('CityRoadStarts');g.get('CityRoadEnds');g.node('CurvedRoads','foreach');g.link('CityRoadStarts','CityRoadStarts','CurvedRoads','Array');g.links.remove(['EastLoop','Completed','Buildings','Exec']);g.link('EastLoop','Completed','CurvedRoads','Exec');g.link('CurvedRoads','Completed','Buildings','Exec');g.call('CurveEnd','Array_Get','/Script/Engine.KismetArrayLibrary');g.link('CityRoadEnds','CityRoadEnds','CurveEnd','TargetArray');g.link('CurvedRoads','Array Index','CurveEnd','Index')
for tag,src,pin in [('CurveA','CurvedRoads','Array Element'),('CurveB','CurveEnd','Item')]:
 g.call(tag+'Norm','MapNormalizedPoint');g.link(src,pin,tag+'Norm','Position');g.link('MapCacheCenter','MapCacheCenter',tag+'Norm','Center');g.link('Open','PhoneOpen',tag+'Norm','FullMap');g.call(tag+'Axes','BreakVector2D',M);g.link(tag+'Norm','ReturnValue',tag+'Axes','InVec')
 for axis in ['X','Y']:
  g.call(tag+axis+'In','InRange_FloatFloat',M,Min='0',Max='1',InclusiveMin='true',InclusiveMax='true');g.link(tag+'Axes',axis,tag+axis+'In','Value')
 g.call(tag+'In','BooleanAND',M);g.link(tag+'XIn','ReturnValue',tag+'In','A');g.link(tag+'YIn','ReturnValue',tag+'In','B');mapped_point(tag,tag+'Norm')
g.call('CurveVisible','BooleanOR',M);g.link('CurveAIn','ReturnValue','CurveVisible','A');g.link('CurveBIn','ReturnValue','CurveVisible','B');g.branch('CurveClip','CurveVisible');g.link('CurvedRoads','LoopBody','CurveClip','execute');line('CurveDraw','CurveClip','CurveA','CurveB','(R=.38,G=.49,B=.53,A=1)',thickness='5')
"""
s=s.replace("g.build('OnPaint')",insert+"\ng.build('OnPaint')");exec(compile(s,'CurvedPhoneMapPaint','exec'))
# Existing point mapping with full-city spans adjusted to the new bounds.
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');d.bp=bp;g=MapGraph();g.call('P','BreakVector',M);g.link('entry','Position','P','InVec');g.call('C','BreakVector',M);g.link('entry','Center','C','InVec')
for tag,axis,full,small,invert in [('X','Y',100000,11000,False),('Y','X',85000,16000,True)]:
 g.call(tag+'Delta','Subtract_DoubleDouble',M);g.link('P',axis,tag+'Delta','A');g.link('C',axis,tag+'Delta','B');g.call(tag+'Span','SelectFloat',M,A=str(full),B=str(small));g.link('entry','FullMap',tag+'Span','bPickA');g.call(tag+'Ratio','Divide_DoubleDouble',M);g.link(tag+'Delta','ReturnValue',tag+'Ratio','A');g.link(tag+'Span','ReturnValue',tag+'Ratio','B');g.call(tag+'Norm','Subtract_DoubleDouble' if invert else 'Add_DoubleDouble',M,A='.5');g.link(tag+'Ratio','ReturnValue',tag+'Norm','B')
g.call('NormalizedVector','MakeVector2D',M);g.link('XNorm','ReturnValue','NormalizedVector','X');g.link('YNorm','ReturnValue','NormalizedVector','Y');g.link('NormalizedVector','ReturnValue','result','ReturnValue');g.exec('entry','result');g.build('MapNormalizedPoint',[{'name':'Position','category':'struct','object':V},{'name':'Center','category':'struct','object':V},{'name':'FullMap','category':'bool'},{'name':'ReturnValue','category':'struct','object':V2,'out':True}],pure=True);assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('MapBuildings',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in b]);c.set_editor_property('MapNorthRoads',[]);c.set_editor_property('MapEastRoads',[]);starts=[];ends=[]
manifest=json.loads(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/manifest.json').read_text())
for road in manifest['roads']:
 points=road['center']
 for i in range(0,len(points)-5,5):starts.append(unreal.Vector(points[i][0]*100,-points[i][1]*100,0));ends.append(unreal.Vector(points[i+5][0]*100,-points[i+5][1]*100,0))
c.set_editor_property('CityRoadStarts',starts);c.set_editor_property('CityRoadEnds',ends);EL.save_loaded_asset(bp,only_if_is_dirty=False)
s=(r/'work/extend_pure_phone_map_input.py').read_text(encoding='utf-8-sig').replace("B='90000'","B='85000'").replace("B='60000'","B='100000'");exec(compile(s,'MatchingMapClickCoordinates','exec'))
# Restrict navigation to the street layer; imported roof geometry cannot become a pedestrian route.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);report={}
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.NavMeshBoundsVolume):
  a.set_actor_location(unreal.Vector(0,0,120),False,True);origin,ext=a.get_actor_bounds(False);sc=a.get_actor_scale3d();a.set_actor_scale3d(unreal.Vector(sc.x*40000/max(ext.x,1),sc.y*50000/max(ext.y,1),sc.z*250/max(ext.z,1)));o,e=a.get_actor_bounds(False);report['nav_bounds']={'center':[o.x,o.y,o.z],'extent':[e.x,e.y,e.z]}
 if isinstance(a,unreal.RecastNavMesh):
  a.set_editor_property('runtime_generation',unreal.RuntimeGenerationType.DYNAMIC);a.set_editor_property('force_rebuild_on_load',True);a.set_editor_property('tile_pool_size',4096);a.set_editor_property('max_simultaneous_tile_generation_jobs_count',2)
 if a.get_class().get_name()=='BP_ResidentialRouteAssembler_C':
  # A bounded set of real house entrances keeps the offer catalog small and distributed.
  houses=plan['building_footprints'];selected=[v for i,v in enumerate(houses) if i%max(1,len(houses)//160)==0][:160];a.set_editor_property('BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in selected]);a.set_editor_property('BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in selected]);report['order_buildings']=len(selected)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();(r/'outputs/MapRebuild/map_metadata_navigation.json').write_text(json.dumps(report,indent=2));unreal.log('NEW_MAP_METADATA_AND_PHONE_READY')
