import bpy,json
from pathlib import Path
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Mixamo/Walk.fbx'))
a=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');print('BONES',[(b.name,list(b.head_local)) for b in a.data.bones]);print('FRAMES',bpy.context.scene.frame_start,bpy.context.scene.frame_end,a.animation_data.action.frame_range)
