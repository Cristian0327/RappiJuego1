import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;report={}
for path in ['/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/Delivery/Vehicles/BP_DeliveryRider']:
 bp=unreal.load_asset(path);mesh=unreal.get_default_object(bp.generated_class()).get_editor_property('mesh');before=mesh.get_editor_property('relative_rotation');row={'before':{'pitch':before.pitch,'yaw':before.yaw,'roll':before.roll}}
 if 'BlueprintGameplay' in path:
  mesh.set_editor_property('relative_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0));assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);row['corrected']=True
 report[path]=row
bp=unreal.load_asset('/Game/World/BlueprintWorld/BP_WorldPresentation');sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
 if str(lib.get_variable_name(lib.get_data(h)))=='StormLightning':lib.get_object_for_blueprint(lib.get_data(h),bp).set_editor_property('relative_rotation',unreal.Rotator(pitch=-65,yaw=35,roll=0))
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/pure_component_rotation_correction.json').write_text(json.dumps(report,indent=2));unreal.log('PURE_DEFAULT_MESH_LIGHT_ROTATION_CORRECTED')
