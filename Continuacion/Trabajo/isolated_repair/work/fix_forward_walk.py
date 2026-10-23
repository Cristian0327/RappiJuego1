import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'outputs/DeliveryArt/Animation/AN_MixamoWalk.blend';bpy.ops.wm.open_mainfile(filepath=str(p));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');a=rig.animation_data.action;lo,hi=a.frame_range
curves=[]
for layer in a.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:curves.extend(bag.fcurves)
for curve in curves:
 for key in curve.keyframe_points:
  left=key.handle_left.copy();right=key.handle_right.copy();key.co.x=lo+hi-key.co.x;key.handle_left=(lo+hi-right.x,right.y);key.handle_right=(lo+hi-left.x,left.y)
 curve.update()
bpy.context.scene.frame_start=int(lo);bpy.context.scene.frame_end=int(hi);bpy.context.scene['walk_fix']='Timeline reversed: toe forward -Y; planted foot must travel +Y. Jump unaffected.'
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(p))
bpy.ops.export_scene.fbx(filepath=str(p.with_suffix('.fbx')),use_selection=True,object_types={'ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',use_armature_deform_only=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,axis_forward='-Y',axis_up='Z')
