import bpy
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Crowd'
for f in sorted(out.glob('SK_*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(f))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.animation_data.action=bpy.data.actions['Walk_InPlace'];bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=61;bpy.context.scene.frame_set(1)
 bpy.ops.wm.save_as_mainfile(filepath=str(f))
print('CROWD_BLENDER_WALK_READY')
