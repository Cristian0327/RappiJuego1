import bpy
from pathlib import Path
O=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs/unreal_v2')
bpy.ops.wm.open_mainfile(filepath=str(O/'VoxelExplorer_GameRig.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
rig.animation_data.action=bpy.data.actions['Idle'];bpy.context.scene.frame_set(1);rig.animation_data.action=None
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.pack()
  except Exception:pass
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='POSE')
rig.pose.bones['pelvis'].select=True;rig.data.bones.active=rig.data.bones['pelvis'];rig.show_in_front=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'VoxelExplorer_GameRig.blend'),compress=True)
print('FINAL_RIG_READY')
