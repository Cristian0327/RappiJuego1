import bpy,json
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto')
a=[]
for name in ['Crowd/SK_Citizen12','Services/SK_PoliceOfficer']:
 bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt'/(name+'.blend')))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
 a.append({'name':name,'matrix':str(rig.matrix_world),'bones':[{'name':b.name,'deform':b.bone.use_deform,'mode':b.rotation_mode,'euler':list(b.rotation_euler),'quat':list(b.rotation_quaternion),'rest':str(b.bone.matrix_local)} for b in rig.pose.bones]})
(r/'work/police_blender_rig_comparison.json').write_text(json.dumps(a,indent=2))
