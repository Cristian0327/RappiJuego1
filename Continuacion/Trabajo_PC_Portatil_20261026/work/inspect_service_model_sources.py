import bpy,json
from pathlib import Path
root=Path('C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto');report=[]
for p in [root/'outputs/DeliveryArt/TrafficDetailed/SK_PrivateSUV.blend',root/'outputs/DeliveryArt/People/SK_Citizen00.blend',root/'outputs/DeliveryArt/Crowd/AN_CrowdIdle.blend',root/'outputs/DeliveryArt/Progression/MotoRide.blend']:
 if not p.exists():
  report.append({'path':str(p),'exists':False});continue
 bpy.ops.wm.open_mainfile(filepath=str(p));report.append({'path':str(p),'objects':[{'name':o.name,'type':o.type,'dim':list(o.dimensions),'colors':[c.name for c in o.data.color_attributes] if o.type=='MESH' else [],'materials':[s.material.name if s.material else '' for s in o.material_slots] if o.type=='MESH' else [],'bones':[b.name for b in o.data.bones][:14] if o.type=='ARMATURE' else []} for o in bpy.data.objects]})
(root/'work/service_model_source_inspection.json').write_text(json.dumps(report,indent=2))
