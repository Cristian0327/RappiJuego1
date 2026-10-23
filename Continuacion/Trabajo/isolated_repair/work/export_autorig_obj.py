import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'outputs/DeliveryArt/Mixamo/CustomerStudent_AutoRig_Input.blend';bpy.ops.wm.open_mainfile(filepath=str(p));o=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
bpy.ops.wm.obj_export(filepath=str(p.with_suffix('.obj')),export_selected_objects=True,export_materials=False,forward_axis='NEGATIVE_Z',up_axis='Y')
