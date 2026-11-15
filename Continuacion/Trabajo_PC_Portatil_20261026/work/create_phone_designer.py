import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
phone=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone')
assert phone
assert unreal.DeliveryEditorLibrary.build_phone_designer(phone),'Designer compilation failed'
unreal.EditorAssetLibrary.save_loaded_asset(phone)
(root/'work/phone_designer_result.json').write_text(json.dumps({'asset':phone.get_path_name(),'type':phone.get_class().get_name(),'saved':True},indent=2))
