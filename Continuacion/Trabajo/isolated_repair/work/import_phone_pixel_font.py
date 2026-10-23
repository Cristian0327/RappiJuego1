import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
factory=unreal.FontFileImportFactory();factory.set_editor_property('batch_create_font_asset',unreal.BatchCreateFontAsset.YES)
for style in ['Regular','Bold']:
 task=unreal.AssetImportTask();task.filename=str(root/'outputs/DeliveryArt/UI/Fonts'/('RutaPixel-'+style+'.ttf'));task.destination_path='/Game/Delivery/UI/Fonts';task.destination_name='RutaPixel_'+style;task.automated=True;task.replace_existing=True;task.save=True;task.factory=factory
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
fonts=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/Delivery/UI/Fonts'):
 asset=unreal.load_asset(path)
 if isinstance(asset,unreal.Font):
  assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False)
  fonts.append(asset)
font=next((f for f in fonts if 'Bold' in f.get_name()),None);assert font,[f.get_path_name() for f in fonts]
assert (Path(unreal.Paths.project_content_dir())/'Delivery/UI/Fonts/RutaPixel_Bold_Font.uasset').is_file()
phone=unreal.load_asset('/Game/Delivery/UI/WBP_VoxelPhone');assert unreal.DeliveryEditorLibrary.style_phone_typography(phone,font)
assert unreal.EditorAssetLibrary.save_loaded_asset(phone,only_if_is_dirty=False)
(root/'work/phone_pixel_font.json').write_text(json.dumps({'font':font.get_path_name(),'phone':phone.get_path_name()},indent=2))
unreal.SystemLibrary.quit_editor()
