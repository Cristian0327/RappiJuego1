import bpy,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');rows=[]
for name in ['Mapa_Bogota_Calles_Completas.blend','Estacion_Compacta.blend']:
 source=P/name;target=P/'portable_package/BogotaVoxel/Fuentes_Blender'/name;bpy.ops.wm.open_mainfile(filepath=str(source));missing=[i for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()];
 for i in missing:
  assert not any(m.use_nodes and any(getattr(n,'image',None)==i for n in m.node_tree.nodes) for m in bpy.data.materials);bpy.data.images.remove(i)
 bpy.ops.file.pack_all();images=[dict(name=i.name,path=i.filepath,packed=bool(i.packed_file),source=i.source) for i in bpy.data.images if i.source=='FILE'];assert all(i['packed'] for i in images),images;bpy.ops.wm.save_as_mainfile(filepath=str(target));rows.append(dict(file=name,images=images,libraries=[l.filepath for l in bpy.data.libraries]));assert not bpy.data.libraries
(P/'portable_blender_check.json').write_text(json.dumps(rows,indent=2));print('PORTABLE_BLENDER_SELF_CONTAINED')
