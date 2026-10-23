import unreal,json,math,sys,collections,shutil
from pathlib import Path
C=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/compact_city');R=C.parent;O=R/'urban_refresh';U=R/'urban_corrections';W=R/'new_map_audit';root=Path(unreal.Paths.project_dir()).parent;assert len(json.loads((C/'asset_backup/inventory.json').read_text(encoding='utf-8-sig')))>150
sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);plan=json.loads((W/'integration_plan.json').read_text());manifest=json.loads((W/'manifest.json').read_text());assert manifest['spacing_expansion']==1.
# The old city's parent remains only as a metadata/API provider; it cannot build or render the square city.
bp=unreal.load_asset('/Game/World/BlueprintWorld/BP_CityGeometry');d.bp=bp
for fun in ['UserConstructionScript','ReceiveBeginPlay','ReceiveTick']:
 g=d.Graph();g.exec('entry','result');g.build(fun)
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 obj=lib.get_object_for_blueprint(lib.get_data(h),bp)
 if isinstance(obj,unreal.InstancedStaticMeshComponent):obj.clear_instances();obj.set_static_mesh(None);obj.set_collision_profile_name('NoCollision');obj.set_editor_property('can_ever_affect_navigation',False)
assert E.compile_blueprint(bp);cdo=unreal.get_default_object(bp.generated_class())
for var in ['NorthRoads','EastRoads']:
 if var in [str(v) for v in E.list_member_variable_names(bp)]:cdo.set_editor_property(var,[])
assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
# Update actual traffic lane splines, keeping all existing traffic behavior and vehicle materials.
s=(R/'integrate_new_map_routes.py').read_text();s=s[:s.index('# Rebuild the occupied-cell grid')];exec(compile(s,'CompactTrafficLanes','exec'),{})
exec(compile((R/'finish_new_map_crowd.py').read_text(),'CompactSidewalkCrowd','exec'),{})
# Re-place the existing gameplay actors in the same neighborhoods of the compact map.
walk=plan['walk_routes'];lanes=plan['lanes'];counts=collections.Counter()
def prop(a,n,v):
 try:a.set_editor_property(n,v)
 except Exception:pass
stores=sorted([a for a in A.get_all_level_actors() if a.get_class().get_name()=='BP_DeliveryStore_C'],key=lambda a:int(a.get_name().rsplit('_',1)[1]));assert len(stores)==len(plan['shops'])==20
for a,row in zip(stores,plan['shops']):a.set_actor_location(unreal.Vector(*row['entrance']),False,True);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=row['store_yaw'],roll=0),True);a.set_editor_property('Built',False)
for a in list(A.get_all_level_actors()):
 cl=a.get_class().get_name();i=counts[cl];counts[cl]+=1
 if cl=='BP_PoliceOfficer_C':
  route=walk[(i*7)%len(walk)];a.set_actor_location(unreal.Vector(route[0][0],route[0][1],108),False,True);prop(a,'PatrolPoints',[unreal.Vector(*p) for p in route]);prop(a,'PatrolIndex',1)
 elif cl in ['BP_CivilMotorcycle_C','BP_PoliceMotorcycle_C','BP_PoliceRoadPatrol_C','BP_TwoWheelerCitizen_C']:
  route=lanes[(i+2)%6];j=(i*137+99)%len(route);a.set_actor_location(unreal.Vector(route[j][0],route[j][1],154 if cl=='BP_PoliceRoadPatrol_C' else 102 if cl=='BP_TwoWheelerCitizen_C' else 134),False,True);prop(a,'Route',[unreal.Vector(v[0],v[1],14) for v in route]);prop(a,'RouteIndex',(j+1)%len(route));prop(a,'RoadMode',True)
 elif cl.startswith('BP_TaxiPassenger') or (cl.startswith('BP_CrosswalkCitizen') and cl!='BP_CrosswalkCitizen_C'):
  route=walk[(i*7+counts['service walkers']*5)%len(walk)];counts['service walkers']+=1;a.set_actor_location(unreal.Vector(route[0][0],route[0][1],108),False,True);prop(a,'Route',[unreal.Vector(*p) for p in route]);prop(a,'RouteIndex',1);prop(a,'CrossSegments',[False]*len(route))
 elif isinstance(a,unreal.PlayerStart):a.set_actor_location(unreal.Vector(*plan['player_start']),False,True)
 elif cl=='BP_ResidentialRouteAssembler_C':
  boxes=plan['building_footprints'];prop(a,'BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in boxes]);prop(a,'BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in boxes])
 elif isinstance(a,unreal.NavMeshBoundsVolume):
  a.set_actor_location(unreal.Vector(0,0,120),False,True);o,ex=a.get_actor_bounds(False);sc=a.get_actor_scale3d();a.set_actor_scale3d(unreal.Vector(sc.x*40000/max(ex.x,1),sc.y*50000/max(ex.y,1),sc.z*250/max(ex.z,1)))
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
# Import the compact, connected ribbons and re-place station access, furniture and synchronized signals.
s=(U/'integrate_corrections.py').read_text();s=s[:s.index("assert unreal.EditorLoadingAndSavingUtils.save_current_level();exec(compile((O/'build_urban_qa.py')")];exec(compile(s,'CompactRoadStationIntegration','exec'),{})
# Clear the unused old instanced shop-link component so no obsolete grid can survive.
bp=unreal.load_asset('/Game/World/BogotaUrban/BP_BogotaUrbanDressing')
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 obj=lib.get_object_for_blueprint(lib.get_data(h),bp);name=str(lib.get_variable_name(lib.get_data(h)))
 if name=='UrbanPart6' and isinstance(obj,unreal.InstancedStaticMeshComponent):obj.clear_instances();obj.set_static_mesh(None);obj.set_collision_profile_name('NoCollision');obj.set_editor_property('can_ever_affect_navigation',False)
assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
for actor in list(A.get_all_level_actors()):
 if actor.get_class().get_name()=='BP_BogotaUrbanDressing_C':A.destroy_actor(actor)
A.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
# Parent construction is disabled and inherited meshes are empty; refresh the compact child once more.
bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');cdo=unreal.get_default_object(bp.generated_class())
for name in ['NorthRoads','EastRoads']:
 try:cdo.set_editor_property(name,[])
 except Exception:pass
boxes=plan['building_footprints'];cdo.set_editor_property('BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in boxes]);cdo.set_editor_property('BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in boxes]);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
for a in list(A.get_all_level_actors()):
 if a.get_class().get_name() in ['BP_MapaCompletoGeometry_C','BP_CrowdManager_C']:A.destroy_actor(a)
for path in ['/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry','/Game/World/BlueprintWorld/Crowd/BP_CrowdManager']:A.spawn_actor_from_class(unreal.load_asset(path).generated_class(),unreal.Vector())
# Use the original city spans and clear both legacy rectangular minimap arrays.
r=root;backup=root/'Recuperacion_Migracion_Blueprints/2026-10-20_new_map';M=d.M;b=boxes;s=(R/'finalize_new_map_metadata.py').read_text();s=s[s.index('# The phone keeps'):s.index('# Restrict navigation')];phone_namespace=dict(globals());exec(compile(s,'CompactPhoneMap','exec'),phone_namespace)
# Include secondary streets in the phone's genuine map, rather than a square cached grid.
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone');cdo=unreal.get_default_object(bp.generated_class());starts=list(cdo.get_editor_property('CityRoadStarts'));ends=list(cdo.get_editor_property('CityRoadEnds'))
for points in json.loads((U/'unique_centerlines.json').read_text()):
 for a,b in zip(points[::5],points[5::5]):starts.append(unreal.Vector(a[0],a[1],0));ends.append(unreal.Vector(b[0],b[1],0))
cdo.set_editor_property('CityRoadStarts',starts);cdo.set_editor_property('CityRoadEnds',ends);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
# Fresh probes are made from this actual map after all actor routes and positions are updated.
exec(compile((O/'build_urban_qa.py').read_text(),'CompactMapRegressionMaps','exec'),{});exec(compile((O/'add_crossing_completion_probe.py').read_text(),'CompactCrossingProbe','exec'),{})
for source in [W/'manifest.json',W/'integration_plan.json',O/'Mapa_Bogota_Ambientado.blend',C/'local_building_adjustments.json']:shutil.copy2(source,root/'outputs/BogotaUrban'/source.name)
unreal.log('COMPACT_ORIGINAL_DENSITY_AND_NO_LEGACY_GRID_SAVED')
