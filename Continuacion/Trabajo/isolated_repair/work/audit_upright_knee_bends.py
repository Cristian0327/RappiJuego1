import bpy,json,math
from pathlib import Path
from mathutils import Vector
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');folder=r/'outputs/DeliveryArt/AnimationRebuild/Upright';report=[]
for file in sorted(folder.glob('*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(file));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');sc=bpy.context.scene;legs=[]
 for side in (['l','r'] if 'thigh_l' in rig.pose.bones else ['L','R']):
  names=['thigh_'+side,('calf_' if 'calf_'+side in rig.pose.bones else 'shin_')+side,'foot_'+side]
  if not all(x in rig.pose.bones for x in names):continue
  data=[];angles=[]
  for frame in range(sc.frame_start,sc.frame_end+1):
   sc.frame_set(frame);bpy.context.view_layer.update();hip,knee,foot=[rig.pose.bones[x].head.copy() for x in names];axis=foot-hip
   if axis.length<.001:continue
   deviation=knee-(hip+axis*(knee-hip).dot(axis)/axis.length_squared);ratio=deviation.dot(Vector((0,-1,0)))/axis.length;data.append(ratio);angles.append((knee-hip).angle(foot-knee))
  legs.append({'side':side,'frames':len(data),'forward_flexed_frames':sum(v>.015 for v in data),'backward_flexed_frames':sum(v<-.015 for v in data),'minimum_knee_projection':min(data),'maximum_knee_projection':max(data),'maximum_flexion_degrees':math.degrees(max(angles))})
 assert len(legs)==2,(file.stem,[b.name for b in rig.pose.bones]);report.append({'clip':file.stem,'legs':legs});print('KNEE_AUDIT '+file.stem+' '+json.dumps(legs),flush=True)
(folder/'knee_bend_validation.json').write_text(json.dumps(report,indent=2));print('ALL_UPRIGHT_KNEE_AUDIT_FINISHED',flush=True)
