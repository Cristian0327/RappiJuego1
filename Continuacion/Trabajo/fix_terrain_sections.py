import unreal,json,sys,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;mat=unreal.load_asset('/Game/Maps/MapaCompleto/M_AndenesBogota');mesh=unreal.load_asset('/Game/Maps/MapaCompleto/Geometry/SM_Mapa_081')
for i in range(len(mesh.static_materials)):mesh.set_material(i,mat)
assert EL.save_loaded_asset(mesh,only_if_is_dirty=False)
bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp)
 if str(lib.get_variable_name(lib.get_data(h)))=='Part081':
  for i in range(len(mesh.static_materials)):o.set_material(i,mat)
assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_MapaCompletoGeometry_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
plan=json.loads((W/'integration_plan.json').read_text());route=plan['walk_routes'][0];point=route[5]
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.PlayerStart):a.set_actor_location(unreal.Vector(point[0]+320,point[1]+180,108),False,True)
 if a.get_class().get_name()=='BP_PoliceOfficer_C':
  points=a.get_editor_property('PatrolPoints')
  if points and math.dist([points[0].x,points[0].y],route[0][:2])<100:
   rr=plan['walk_routes'][2];a.set_editor_property('PatrolPoints',[unreal.Vector(*v) for v in rr]);a.set_actor_location(unreal.Vector(rr[7][0],rr[7][1],108),False,True);a.set_editor_property('PatrolIndex',8)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_new_map_runtime_probe.py').read_text());exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_new_map_transit_qa.py').read_text());unreal.log('ALL_TERRAIN_SECTIONS_PAVED_GREEN_MOUNTAINS')
