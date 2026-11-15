import bpy
from pathlib import Path
r=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/AnimationRebuild/AN_CrowdCarDrive_Rebuilt.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH')
for f in [1,2,10,49,97,145,193]:
 bpy.context.scene.frame_set(f);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());print('FIT',f,'bounds',min(v.co.z for v in ev.data.vertices),max(v.co.z for v in ev.data.vertices),'root',list(rig.pose.bones['root'].location),'feet',[list(rig.pose.bones[n].head) for n in ['foot_l','foot_r']],'legs',[rig.pose.bones[n].length for n in ['thigh_l','calf_l']])
