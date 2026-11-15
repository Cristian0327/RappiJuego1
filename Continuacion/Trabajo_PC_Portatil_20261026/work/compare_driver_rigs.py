import bpy,json
from pathlib import Path
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");report=[]
for f in [r/'outputs/DeliveryArt/AnimationRebuild/AN_CrowdCarDrive_Rebuilt.blend',r/'outputs/DeliveryArt/Services/SK_PoliceOfficer.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(f));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH');d={'file':f.name,'rig_scale':list(rig.scale),'mesh_scale':list(mesh.scale),'rig_rotation':list(rig.rotation_euler),'mesh_rotation':list(mesh.rotation_euler),'rig_nla':len(rig.animation_data.nla_tracks) if rig.animation_data else 0,'parent_inverse':[list(row) for row in mesh.matrix_parent_inverse],'bone_rest':{n:[list(row) for row in rig.data.bones[n].matrix_local] for n in ['root','pelvis','foot_l']},'modes':{n:rig.pose.bones[n].rotation_mode for n in ['root','pelvis','foot_l']}}
 if 'Police' in f.name:
  with bpy.data.libraries.load(str(r/'outputs/DeliveryArt/AnimationRebuild/AN_CrowdCarDrive_Rebuilt.blend'),link=False) as (a,b):b.actions=['AN_CrowdCarDrive_Rebuilt']
  rig.animation_data_create();rig.animation_data.action=b.actions[0]
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());d['bounds']=[min(v.co.z for v in ev.data.vertices),max(v.co.z for v in ev.data.vertices)];d['pose']={n:list(rig.pose.bones[n].head) for n in ['root','pelvis','foot_l']};report.append(d)
(r/'work/driver_rig_comparison.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
