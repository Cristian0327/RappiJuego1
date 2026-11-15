import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['VoxelExplorer_GameRig.blend','VoxelExplorer_GameRig_Unreal.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(root/'outputs/unreal_v2'/name));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');print('RIG',name,rig.scale,bpy.context.scene.unit_settings.scale_length)
 for n in ['root','pelvis','spine_03']:print(n,rig.data.bones[n].head_local,rig.pose.bones[n].scale)
