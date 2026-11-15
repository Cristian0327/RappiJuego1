import bpy,json
from pathlib import Path
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");out=r/'outputs/DeliveryArt/AnimationRebuild';reports=[]
for name in ['SK_PoliceOfficer','SK_PoliceOfficerMale02','SK_PoliceOfficerFemale01','SK_PoliceOfficerFemale02']:
 bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/Services'/(name+'.blend')));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH')
 with bpy.data.libraries.load(str(out/'AN_CrowdCarDrive_Rebuilt.blend'),link=False) as (a,b):b.actions=['AN_CrowdCarDrive_Rebuilt']
 rig.animation_data_create();rig.animation_data.action=b.actions[0];zs=[];feet=[]
 for f in range(1,194):
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());zs.append(max(v.co.z for v in ev.data.vertices));feet.append(min(v.co.z for v in ev.data.vertices))
 item={'model':name,'roof_limit_cm':180,'max_head_cm':max(zs),'minimum_foot_cm':min(feet),'fits_roof':max(zs)<180,'feet_above_floor':min(feet)>=36};reports.append(item);print(item,flush=True)
assert all(x['fits_roof'] and x['feet_above_floor'] for x in reports),reports
(out/'police_driver_fit_validation.json').write_text(json.dumps({'status':'PASS','models':reports},indent=2));print('ALL_POLICE_DRIVERS_FIT_ROOF_PASS',flush=True)
