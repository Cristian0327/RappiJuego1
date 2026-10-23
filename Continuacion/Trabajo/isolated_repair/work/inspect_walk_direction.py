import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
for file in [r/'outputs/DeliveryArt/Animation/AN_MixamoWalk.blend',r/'outputs/unreal_v2/VoxelExplorer_GameRig.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(file));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
 if 'GameRig' in file.name:rig.animation_data.action=bpy.data.actions['Walk_InPlace']
 print('TOE_FORWARD',tuple(rig.data.bones['ball_l'].tail_local-rig.data.bones['foot_l'].head_local),flush=True)
 action=rig.animation_data.action;start,end=map(int,action.frame_range);samples=[]
 for f in range(start,end+1):
  bpy.context.scene.frame_set(f);p=rig.pose.bones['ball_l'].matrix.translation;samples.append((p.y,p.z))
 floor=min(p[1] for p in samples);tol=max(.03,(max(p[1] for p in samples)-floor)*.25);steps=[b[0]-a[0] for a,b in zip(samples,samples[1:]) if a[1]<floor+tol and b[1]<floor+tol]
 print('STANCE_DIRECTION',file.name,'Y',sum(steps)/max(1,len(steps)), 'CONTACT_FRAMES',len(steps),flush=True)
