import unreal,json,sys,math,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');plan=json.loads((W/'integration_plan.json').read_text());factor=json.loads((W/'manifest.json').read_text())['spacing_expansion'];E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_new_map'
assert len(plan['shops'])==20 and all(s['walk_link'] for s in plan['shops'])
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/integrate_new_map_services.py').read_text().replace("'HalfWidth',500.","'HalfWidth',1200.").replace("'HalfDepth',450.","'HalfDepth',1600.");exec(compile(s,'ExpandedCityServices','exec'))
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/prioritize_transit_exit.py').read_text())
# Rebuild only phone map paint/mapping, retaining the cleared geometry inheritance.
b=plan['building_footprints'];s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/finalize_new_map_metadata.py').read_text();s=s[s.index('# The phone keeps'):s.index('# Restrict navigation')];s=s.replace('100000,11000',str(100000*factor)+',11000').replace('85000,16000',str(85000*factor)+',16000').replace("\"B='85000'\"",'"B=\''+str(85000*factor)+'\'"').replace("\"B='100000'\"",'"B=\''+str(100000*factor)+'\'"');exec(compile(s,'ExpandedCityPhoneMap','exec'))
# Resolve map panels by their designer names, independent of cached legacy bindings.
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');d.bp=bp;g=d.Graph();g.get('Delivery');g.get('Page');g.get('PreviewMoto');g.call('Valid','IsValid','/Script/Engine.KismetSystemLibrary');g.link('Delivery','Delivery','Valid','Object');g.branch('Ready','Valid');g.exec('entry','Ready');g.exec('Ready','result','else');core='/Game/Delivery/BlueprintGameplay/BPC_DeliveryDataCore.BPC_DeliveryDataCore_C';g.node('Open','getfield',owner=core,var='PhoneOpen');g.link('Delivery','Delivery','Open','self');g.branch('Phone','Open','PhoneOpen');g.exec('Ready','Phone')
for tag,name in [('Mini','MiniMap'),('Bike','App1_Bike_01'),('Moto','App1_Moto_01')]:g.call(tag,'GetWidgetFromName','/Script/UMG.UserWidget',Name=name);g.node(tag+'Return','return');g.link(tag,'ReturnValue',tag+'Return','ReturnValue')
g.exec('Phone','MiniReturn','else');g.call('MapPage','EqualEqual_IntInt',d.M,B='1');g.link('Page','Page','MapPage','A');g.branch('IsMap','MapPage');g.exec('Phone','IsMap');g.exec('IsMap','result','else');g.branch('Mode','PreviewMoto','PreviewMoto');g.exec('IsMap','Mode');g.exec('Mode','MotoReturn');g.exec('Mode','BikeReturn','else');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'GetActiveMapPanel',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[{'name':'ReturnValue','category':'object','object':'/Script/UMG.Widget','out':True}],'pure':True,'const':True}));assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);houses=plan['building_footprints'];selected=[v for i,v in enumerate(houses) if i%max(1,len(houses)//160)==0][:160]
for a in actors.get_all_level_actors():
 if a.get_class().get_name()=='BP_ResidentialRouteAssembler_C':a.set_editor_property('BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in selected]);a.set_editor_property('BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in selected])
 if isinstance(a,unreal.NavMeshBoundsVolume):
  a.set_actor_location(unreal.Vector(0,0,120),False,True);o,ex=a.get_actor_bounds(False);sc=a.get_actor_scale3d();a.set_actor_scale3d(unreal.Vector(sc.x*40000*factor/max(ex.x,1),sc.y*50000*factor/max(ex.y,1),sc.z*250/max(ex.z,1)))
 if isinstance(a,unreal.RecastNavMesh):a.set_editor_property('tile_pool_size',16384);a.set_editor_property('max_simultaneous_tile_generation_jobs_count',4)
 if isinstance(a,unreal.PlayerStart):a.set_actor_location(unreal.Vector(*plan['player_start']),False,True)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_new_map_runtime_probe.py').read_text())
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_new_map_transit_qa.py').read_text())
(r/'outputs/MapRebuild/spacing_expansion_report.json').write_text(json.dumps({'spacing_factor':factor,'same_building_models':True,'same_relative_layout':True,'shops':20,'all_shop_links':True,'walking_routes':len(plan['walk_routes']),'crowd':len(plan['pedestrians']),'traffic':100,'stations':4},indent=2));unreal.log('SAME_MAP_EXPANSION_STAGE_B_READY')
