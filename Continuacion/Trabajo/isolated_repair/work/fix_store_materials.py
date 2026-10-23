import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
import json
colors=json.loads((root/'outputs/DeliveryArt/Stores/materials.json').read_text())
colors.update({'ENV_'+k:v for k,v in {'ink':(.035,.055,.075,1),'oak':(.32,.15,.065,1),'honey':(.65,.36,.12,1),'sage':(.20,.37,.24,1),'cream':(.84,.78,.61,1),'ivory':(.91,.90,.79,1),'red':(.63,.09,.05,1),'blue':(.045,.29,.38,1),'steel':(.4,.45,.46,1),'leaf':(.14,.34,.07,1),'pink':(.75,.20,.36,1),'gold':(.94,.58,.08,1)}.items()})
colors.update({'ENV_'+k:v for k,v in {'cobalt':(.015,.12,.60,1),'cyan':(.01,.64,.83,1),'brick':(.47,.19,.105,1),'bricklight':(.62,.26,.14,1),'graphite':(.11,.13,.15,1),'mortar':(.24,.22,.20,1),'tile':(.84,.84,.80,1),'glass':(.73,.88,.94,.12),'warm':(1,.65,.17,1)}.items()})
for name,c in colors.items():
 path='/Game/Delivery/Stores/'+name
 mat=unreal.load_asset(path)
 if not isinstance(mat,unreal.Material):mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Delivery/Stores',unreal.Material,unreal.MaterialFactoryNew())
 unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
 color=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0);color.set_editor_property('constant',unreal.LinearColor(*c));unreal.MaterialEditingLibrary.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
 glow=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,150);glow.set_editor_property('constant',unreal.LinearColor(c[0]*.45,c[1]*.45,c[2]*.45,1));unreal.MaterialEditingLibrary.connect_material_property(glow,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if name=='ENV_glass':
  mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
  opacity=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,300);opacity.set_editor_property('r',.09);unreal.MaterialEditingLibrary.connect_material_property(opacity,'',unreal.MaterialProperty.MP_OPACITY)
 unreal.MaterialEditingLibrary.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
for data in unreal.EditorAssetLibrary.list_assets('/Game/Delivery/Stores',recursive=False):
 mesh=unreal.load_asset(data)
 if isinstance(mesh,unreal.StaticMesh):
  slots=mesh.get_editor_property('static_materials');changed=False
  for index,slot in enumerate(slots):
   name=str(slot.get_editor_property('material_slot_name'))
   canonical=next((n for n in colors if name==n or name.startswith(n+'_')),None)
   if canonical:
    material=unreal.load_asset('/Game/Delivery/Stores/'+canonical)
    if slot.get_editor_property('material_interface')!=material:mesh.set_material(index,material);changed=True
  if changed:
   unreal.EditorAssetLibrary.save_loaded_asset(mesh)
unreal.log('STORE_COLORS_FIXED')
