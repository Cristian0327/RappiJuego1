import unreal,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];mel=unreal.MaterialEditingLibrary
tex=unreal.load_asset('/Game/Crowd/T_CrowdPixelAtlas')
t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/Crowd/T_CrowdPixelAtlas.png');t.destination_path='/Game/Crowd';t.automated=True;t.replace_existing=True;t.save=True;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
tex=unreal.load_asset('/Game/Crowd/T_CrowdPixelAtlas');tex.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);tex.set_editor_property('never_stream',True);unreal.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False)
parent=unreal.load_asset('/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB')
node=mel.create_material_expression(parent,unreal.MaterialExpressionScalarParameter,-420,500);node.set_editor_property('parameter_name','Specular');node.set_editor_property('default_value',.08);mel.connect_material_property(node,'',unreal.MaterialProperty.MP_SPECULAR);mel.recompile_material(parent);unreal.EditorAssetLibrary.save_loaded_asset(parent,only_if_is_dirty=False)
mi=unreal.load_asset('/Game/Crowd/MI_Crowd');mel.set_material_instance_scalar_parameter_value(mi,'Roughness',.9);mel.set_material_instance_scalar_parameter_value(mi,'Specular',.08);mel.update_material_instance(mi);unreal.EditorAssetLibrary.save_loaded_asset(mi,only_if_is_dirty=False)
unreal.EditorLevelLibrary.load_level('/Game/Maps/Bogota')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
 if actor.get_actor_label()=='EditorPreview_Ambiente':
  c=actor.get_component_by_class(unreal.SkyLightComponent);c.set_editor_property('sky_distance_threshold',50000);c.set_editor_property('lower_hemisphere_is_black',False);c.recapture_sky()
unreal.EditorLevelLibrary.save_current_level();unreal.log('PALETTE_SKY_SPECULAR_PASS')
