import bpy,bmesh
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Shops'
for file in out.glob('SM_*Front.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(file));obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');bm=bmesh.new();bm.from_mesh(obj.data);faces=[f for f in bm.faces if 4.95<abs(f.calc_center_median().x)<5.21 and .20<f.calc_center_median().y<8.1];bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(obj.data);bm.free();bpy.context.scene['old_side_partitions_removed']=True
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.wm.save_as_mainfile(filepath=str(file));bpy.ops.export_scene.fbx(filepath=str(file.with_suffix('.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE',axis_forward='-Y',axis_up='Z');print('OLD_SIDE_PARTITIONS_REMOVED',file.stem,len(faces),flush=True)
