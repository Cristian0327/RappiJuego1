import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
phone=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone')
if not phone:
 factory=unreal.WidgetBlueprintFactory();factory.set_editor_property('parent_class',unreal.load_class(None,'/Script/BogotaVoxel.DeliveryPhoneWidget'))
 phone=unreal.AssetToolsHelpers.get_asset_tools().create_asset('WBP_VoxelPhone','/Game/Delivery/UI',unreal.WidgetBlueprint,factory)
assert phone
assert unreal.DeliveryEditorLibrary.build_phone_designer(phone),'Designer compilation failed'
unreal.EditorAssetLibrary.save_loaded_asset(phone)
(root/'work/phone_designer_result.json').write_text(json.dumps({'asset':phone.get_path_name(),'type':phone.get_class().get_name(),'saved':True},indent=2))
unreal.SystemLibrary.quit_editor()
