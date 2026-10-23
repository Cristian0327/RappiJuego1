import unreal

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
path = '/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB'
mat = unreal.load_asset(path)
if not mat:
    mat = asset_tools.create_asset('M_VoxelExplorerRuntimeRGB', '/Game/VoxelExplorer', unreal.Material, unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(mat)
texture = unreal.load_asset('/Game/VoxelExplorer/T_VoxelExplorer_BaseColor')
texture.set_editor_property('filter', unreal.TextureFilter.TF_NEAREST)
texture.set_editor_property('srgb', True)
sample = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -420, 0)
sample.set_editor_property('parameter_name', 'BaseColorTexture')
sample.set_editor_property('texture', texture)
rough = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -420, 180)
rough.set_editor_property('parameter_name', 'Roughness')
rough.set_editor_property('default_value', .82)
emit = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -420, 340)
emit.set_editor_property('parameter_name', 'VoxelEmission')
emit.set_editor_property('default_value', .06)
emission = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -80, 120)
mel.connect_material_expressions(sample, 'RGB', emission, 'A')
mel.connect_material_expressions(emit, '', emission, 'B')
mel.connect_material_property(sample, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
spec = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -420, 500)
spec.set_editor_property('parameter_name', 'Specular')
spec.set_editor_property('default_value', .08)
mel.connect_material_property(spec, '', unreal.MaterialProperty.MP_SPECULAR)
mel.connect_material_property(emission, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)

mesh = unreal.load_asset('/Game/VoxelExplorer/SK_VoxelExplorer')
mesh.modify()
slots = mesh.get_editor_property('materials')
slots[0].material_interface = mat
mesh.set_editor_property('materials', slots)
if hasattr(mesh, 'set_material'):
    mesh.set_material(0, mat)
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
unreal.EditorAssetLibrary.save_asset('/Game/VoxelExplorer/SK_VoxelExplorer', only_if_is_dirty=False)
unreal.log('CHARACTER_MATERIAL_FIXED texture=' + str(texture) + ' material=' + str(mat))
