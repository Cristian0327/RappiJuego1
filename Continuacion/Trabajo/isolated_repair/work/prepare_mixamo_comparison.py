import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/RigComparison';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(out/'Mixamo_AutoRig_Walk.fbx'))
mat=bpy.data.materials.new('NPC_Atlas');mat.use_nodes=True;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(root/'outputs/DeliveryArt/People/NPCPalette.png'));tex.interpolation='Closest';mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(mat)
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');print('MIXAMO_SCALE',arm.scale,'RANGE',arm.animation_data.action.frame_range)
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
from mathutils import Vector
pts=[o.matrix_world@Vector(c) for o in bpy.context.scene.objects if o.type=='MESH' for c in o.bound_box]
height=max(v.z for v in pts)-min(v.z for v in pts);factor=1.7/height
for o in bpy.context.scene.objects:
 if o.parent is None:o.scale*=factor;o.location*=factor
bpy.context.view_layer.update()
print('NORMALIZED_HEIGHT',height,'FACTOR',factor)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Mixamo_AutoRig.blend'))
