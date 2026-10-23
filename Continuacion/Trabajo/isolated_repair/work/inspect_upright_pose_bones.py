import bpy
from pathlib import Path
p=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs/DeliveryArt/AnimationRebuild/Upright/AN_HeroWalk_Rebuilt.blend');bpy.ops.wm.open_mainfile(filepath=str(p));rig=next(x for x in bpy.data.objects if x.type=='ARMATURE');print('POSE_BONE_NAMES '+str([b.name for b in rig.pose.bones]),flush=True)
