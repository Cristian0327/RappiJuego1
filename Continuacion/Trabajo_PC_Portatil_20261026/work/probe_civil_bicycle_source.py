import bpy,json
from pathlib import Path
r=Path(r"C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto");bpy.ops.wm.open_mainfile(filepath=str(r/'outputs/DeliveryArt/Progression/SM_BikeStage0.blend'))
data=[{'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],'attributes':[a.name for a in o.data.attributes] if o.type=='MESH' else []} for o in bpy.data.objects];(r/'work/civil_bicycle_source.json').write_text(json.dumps(data,indent=2));print('CIVIL_BICYCLE_SOURCE_PROBE_PASS')
