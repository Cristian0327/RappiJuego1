import bpy,json
from pathlib import Path
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2');bpy.ops.wm.open_mainfile(filepath=str(P/'Mapa_Bogota_Calles_Completas.blend'));rows=[]
for image in bpy.data.images:
 if image.source!='FILE' or image.packed_file or Path(bpy.path.abspath(image.filepath)).exists():continue
 mats=[m for m in bpy.data.materials if m.use_nodes and any(getattr(n,'image',None)==image for n in m.node_tree.nodes)];objects=[o.name for o in bpy.data.objects if any(s.material in mats for s in o.material_slots) or (o.type=='EMPTY' and o.data==image)];rows.append(dict(image=image.name,path=image.filepath,materials=[m.name for m in mats],objects=objects))
(P/'blender_missing_dependencies.json').write_text(json.dumps(rows,indent=2));print(rows)
