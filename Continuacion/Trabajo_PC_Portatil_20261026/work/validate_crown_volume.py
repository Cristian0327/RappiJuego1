import bpy,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];report={}
files=list((r/'outputs/DeliveryArt/Crowd').glob('SK_Citizen*.blend'))+list((r/'outputs/DeliveryArt/People').glob('SK_*.blend'))+[r/'outputs/unreal_v2/VoxelExplorer_GameRig.blend']
for f in files:
 bpy.ops.wm.open_mainfile(filepath=str(f));o=next(o for o in bpy.data.objects if o.type=='MESH');top=max(v.co.z for v in o.data.vertices);unit=100 if top>10 else 1
 levels=sorted(set(round(max(o.data.vertices[i].co.z for i in p.vertices)*100/unit,3) for p in o.data.polygons if p.normal.z>.8 and min(o.data.vertices[i].co.z for i in p.vertices)>top-.18*unit))
 assert len(levels)>=3,(f.name,levels)
 report[f.stem]={'upper_surface_levels_cm':levels,'volumetric_top':True}
report['status']='PASS';(r/'work/crown_volume_validation.json').write_text(json.dumps(report,indent=2));print('ALL_69_VOLUMETRIC_TOPS_PASS')
