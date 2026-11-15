import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_customer_motion.py').read_text(encoding='utf-8-sig'))
mesh=unreal.load_asset('/Game/Delivery/Stores/SM_PharmacyInterior')
rows=[]
for slot in mesh.get_editor_property('static_materials'):
 mat=slot.material_interface
 node=unreal.MaterialEditingLibrary.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR) if isinstance(mat,unreal.Material) else None
 rows.append({'slot':str(slot.material_slot_name),'material':mat.get_path_name() if mat else None,'color':str(node.get_editor_property('constant')) if isinstance(node,unreal.MaterialExpressionConstant3Vector) else str(node)})
(root/'work/pharmacy_unreal_material_audit.json').write_text(json.dumps(rows,indent=2))
