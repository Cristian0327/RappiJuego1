import bpy,json
from pathlib import Path
r=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');a=[]
for name in ['SK_PolicePatrol','SK_PoliceOfficer']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(r/'outputs/DeliveryArt/Services'/(name+'.fbx')))
 m=next(o for o in bpy.data.objects if o.type=='MESH').data;a.append({'name':name,'colors':[{'name':c.name,'count':len(c.data),'min':[min(x.color[i] for x in c.data) for i in range(4)],'max':[max(x.color[i] for x in c.data) for i in range(4)]} for c in m.color_attributes]})
(r/'work/fbx_service_colors.json').write_text(json.dumps(a,indent=2))
