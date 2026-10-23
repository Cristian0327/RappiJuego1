import bpy,json,numpy as np
from pathlib import Path
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');out=[]
for o in bpy.data.objects:
 if not o.name.startswith('SM_Mapa_Road_'):continue
 m=o.data;attr=m.color_attributes.active_color;out.append(dict(name=o.name,verts=[list(v.co) for v in m.vertices],faces=[list(p.vertices) for p in m.polygons],colors=[list(attr.data[p.loop_start].color) for p in m.polygons]))
(U/'road_mesh_source.json').write_text(json.dumps(out));print('ROAD_MESH_SOURCE_READY')
