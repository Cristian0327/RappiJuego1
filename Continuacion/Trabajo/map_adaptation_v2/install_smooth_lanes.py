from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');lanes=json.loads((P/'smooth_lanes.json').read_text());sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for i,points in enumerate(lanes):
 b=use('/Game/World/BlueprintWorld/Traffic/BP_TrafficLane_'+str(i));parts={str(lib.get_variable_name(lib.get_data(h))):lib.get_object_for_blueprint(lib.get_data(h),b) for h in sub.k2_gather_subobject_data_for_blueprint(b)};curve=parts['Route'];curve.set_spline_points([unreal.Vector(*p) for p in points],unreal.SplineCoordinateSpace.LOCAL,False)
 for k in range(len(points)):curve.set_spline_point_type(k,unreal.SplinePointType.LINEAR,False)
 curve.set_closed_loop(True,True);assert E.compile_blueprint(b);save(b)
# Service vehicles follow exactly the corrected carriageway, preserving their position and state.
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);signals=next(a for a in aa.get_all_level_actors() if a.get_class().get_name()=='BP_BogotaServiceSignals_C')
for actor,li in zip(signals.get_editor_property('RoadActors'),signals.get_editor_property('ServiceLaneIndices')):
 actor.set_editor_property('Route',[unreal.Vector(*p) for p in lanes[li]]);actor.set_editor_property('RouteIndex',int(actor.get_editor_property('RouteIndex'))%len(lanes[li]))
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_CUSP_FREE_LANES_INSTALLED')
