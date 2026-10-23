import bpy,json
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');o=[]
for n in ['EnterCar','Sitting']:
 bpy.ops.wm.open_mainfile(filepath=str(r/('outputs/DeliveryArt/AnimationRebuild/AN_Hero'+n+'_Rebuilt.blend')));s=bpy.context.scene;rig=next(x for x in bpy.data.objects if x.type=='ARMATURE')
 for f in [s.frame_start,(s.frame_start+s.frame_end)//2,s.frame_end]:
  s.frame_set(f);bpy.context.view_layer.update();o.append(dict(clip=n,frame=f,bones={b:list(rig.pose.bones[b].head) for b in ['root','pelvis','head','hand_l','hand_r','foot_l','foot_r']}))
print('POSES '+json.dumps(o))
