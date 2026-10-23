import bpy,math
from pathlib import Path
from mathutils import Quaternion,Vector,Matrix
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Mixamo'
bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/DeliveryArt/People/SK_CustomerStudent.blend'));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear()
for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
for side,sign in [('L',-1),('R',1)]:
 b=rig.pose.bones['upperarm_'+side];axis=b.bone.matrix_local.to_quaternion().inverted()@Vector((0,1,0));b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion(axis,-sign*math.radians(65))
bpy.context.view_layer.update();obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.context.view_layer.objects.active=obj
for m in list(obj.modifiers):
 if m.type=='ARMATURE':bpy.ops.object.modifier_apply(modifier=m.name)
obj.parent=None;obj.vertex_groups.clear();bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'CustomerStudent_AutoRig_Input.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,axis_forward='-Y',axis_up='Z',path_mode='COPY',embed_textures=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'CustomerStudent_AutoRig_Input.blend'))
print('MIXAMO_INPUT_READY')
