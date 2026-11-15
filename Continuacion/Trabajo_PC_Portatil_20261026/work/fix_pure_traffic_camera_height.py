import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
 if str(lib.get_variable_name(lib.get_data(h))) in ['HeadlightLeft','HeadlightRight']:lib.get_object_for_blueprint(lib.get_data(h),bp).set_editor_property('relative_rotation',unreal.Rotator(pitch=-10,yaw=0,roll=0))
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
for name in ['extend_pure_traffic_road_height.py','build_pure_traffic_runtime_test.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
unreal.log('PURE_TRAFFIC_ROAD_CAMERA_FIX_PASS')
