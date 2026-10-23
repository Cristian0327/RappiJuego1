import unreal

mel = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
master = unreal.load_asset('/Game/World/M_ColorMasterRuntime')
if not master:
    master = tools.create_asset('M_ColorMasterRuntime', '/Game/World', unreal.Material, unreal.MaterialFactoryNew())
if not master:
    raise RuntimeError('No se pudo crear /Game/World/M_ColorMasterRuntime')
mel.delete_all_material_expressions(master)
col = mel.create_material_expression(master, unreal.MaterialExpressionVectorParameter, -420, 0)
col.set_editor_property('parameter_name', 'Color')
col.set_editor_property('default_value', unreal.LinearColor(.5, .5, .5, 1))
rough = mel.create_material_expression(master, unreal.MaterialExpressionScalarParameter, -420, 170)
rough.set_editor_property('parameter_name', 'Roughness')
rough.set_editor_property('default_value', .85)
power = mel.create_material_expression(master, unreal.MaterialExpressionScalarParameter, -420, 320)
power.set_editor_property('parameter_name', 'GlowStrength')
power.set_editor_property('default_value', 0)
base = mel.create_material_expression(master, unreal.MaterialExpressionScalarParameter, -420, 470)
base.set_editor_property('parameter_name', 'BaseEmission')
base.set_editor_property('default_value', .18)
add = mel.create_material_expression(master, unreal.MaterialExpressionAdd, -170, 420)
mel.connect_material_expressions(base, '', add, 'A')
mel.connect_material_expressions(power, '', add, 'B')
mult = mel.create_material_expression(master, unreal.MaterialExpressionMultiply, 60, 300)
mel.connect_material_expressions(col, '', mult, 'A')
mel.connect_material_expressions(add, '', mult, 'B')
mel.connect_material_property(col, '', unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(mult, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.set_material_usage(master, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
mel.recompile_material(master)
unreal.EditorAssetLibrary.save_asset('/Game/World/M_ColorMasterRuntime', only_if_is_dirty=False)
for asset_name in unreal.EditorAssetLibrary.list_assets('/Game/World', recursive=False, include_folder=False):
    short_name = asset_name.rsplit('/', 1)[-1]
    if short_name.startswith('M_') and short_name not in ('M_ColorMasterRuntime', 'M_Sky'):
        material_instance = unreal.load_asset(asset_name)
        if material_instance and isinstance(material_instance, unreal.MaterialInstanceConstant):
            mel.set_material_instance_parent(material_instance, master)
            unreal.EditorAssetLibrary.save_asset(asset_name, only_if_is_dirty=False)
unreal.log('COLOR_MATERIAL_FIXED')
