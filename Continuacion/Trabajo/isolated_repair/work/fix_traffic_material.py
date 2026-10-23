import unreal,json
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/TrafficDetailed'
t=unreal.AssetImportTask();t.filename=str(out/'T_TrafficPixelAtlas.png');t.destination_path='/Game/Traffic/Detailed';t.destination_name='T_TrafficPixelAtlas';t.automated=True;t.replace_existing=True;t.save=True;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
texture=unreal.load_asset('/Game/Traffic/Detailed/T_TrafficPixelAtlas');texture.modify();texture.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);texture.set_editor_property('srgb',True);texture.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);unreal.EditorAssetLibrary.save_loaded_asset(texture,only_if_is_dirty=False)
m=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficVoxelVertex');m.modify();mel=unreal.MaterialEditingLibrary
mel.delete_all_material_expressions(m)
v=mel.create_material_expression(m,unreal.MaterialExpressionVertexColor,-700,0)
sample=mel.create_material_expression(m,unreal.MaterialExpressionTextureSample,-700,-200);sample.set_editor_property('texture',texture)
assert mel.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
assert mel.connect_material_property(v,'A',unreal.MaterialProperty.MP_ROUGHNESS)
night=mel.create_material_expression(m,unreal.MaterialExpressionScalarParameter,-700,300);night.set_editor_property('parameter_name','NightLights');night.set_editor_property('default_value',0)
strength=mel.create_material_expression(m,unreal.MaterialExpressionMultiply,-470,300);strength.set_editor_property('const_b',6);assert mel.connect_material_expressions(night,'',strength,'A')
mask=mel.create_material_expression(m,unreal.MaterialExpressionIf,-250,200);mask.set_editor_property('const_b',.08);assert mel.connect_material_expressions(v,'A',mask,'A');assert any(mel.connect_material_expressions(strength,'',mask,n) for n in ['ALessThanB','A < B','A<B'])
zero=mel.create_material_expression(m,unreal.MaterialExpressionConstant,-470,500);zero.set_editor_property('r',0)
assert any(mel.connect_material_expressions(zero,'',mask,n) for n in ['AGreaterThanB','A > B','A>B']);assert any(mel.connect_material_expressions(zero,'',mask,n) for n in ['AEqualsB','A == B','A==B'])
ambient=mel.create_material_expression(m,unreal.MaterialExpressionAdd,-50,200);ambient.set_editor_property('const_b',.06);assert mel.connect_material_expressions(mask,'',ambient,'A')
emit=mel.create_material_expression(m,unreal.MaterialExpressionMultiply,150,200);assert mel.connect_material_expressions(sample,'RGB',emit,'A');assert mel.connect_material_expressions(ambient,'',emit,'B');assert mel.connect_material_property(emit,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);mel.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
