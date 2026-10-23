import unreal
from pathlib import Path
root=Path(__file__).resolve().parents[1]
t=unreal.AssetImportTask();t.filename=str(root/'outputs/DeliveryArt/Crowd/T_CrowdPixelAtlas.png');t.destination_path='/Game/Crowd';t.automated=True;t.replace_existing=True;t.save=True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
tex=unreal.load_asset('/Game/Crowd/T_CrowdPixelAtlas')
tex.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);tex.set_editor_property('never_stream',True)
unreal.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False)
