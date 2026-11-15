import unreal
m=unreal.load_asset('/Game/World/M_Rain')
unreal.MaterialEditingLibrary.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(.45,.62,.8,1));unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
unreal.log('RAIN_MATERIAL_INSTANCING_PASS')
