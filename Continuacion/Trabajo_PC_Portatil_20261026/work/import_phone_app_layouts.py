import unreal,json
from pathlib import Path
phone=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone')
assert unreal.DeliveryEditorLibrary.build_phone_app_layouts(phone)
assert unreal.EditorAssetLibrary.save_loaded_asset(phone,only_if_is_dirty=False)
tree=unreal.find_object(phone,'WidgetTree')
names=['App%d_%s_00'%(page,mode) for page in range(1,7) for mode in ['Bike','Moto']]
assert all(unreal.find_object(tree,name) for name in names),names
(Path(unreal.Paths.project_dir()).parents[1]/'work/app_layouts_saved.json').write_text(json.dumps(names,indent=2))
unreal.SystemLibrary.quit_editor()
