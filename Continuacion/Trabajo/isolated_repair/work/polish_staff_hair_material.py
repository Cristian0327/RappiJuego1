import unreal
mel=unreal.MaterialEditingLibrary
mat=unreal.load_asset('/Game/Delivery/People/NPC_Atlas')
if isinstance(mat,unreal.Material):
 for prop,val,y in [(unreal.MaterialProperty.MP_SPECULAR,.08,500),(unreal.MaterialProperty.MP_ROUGHNESS,.9,650)]:
  n=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,y);n.r=val;mel.connect_material_property(n,'',prop)
 mel.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat,only_if_is_dirty=False)
unreal.log('STAFF_HAIR_MATTE_PASS')
