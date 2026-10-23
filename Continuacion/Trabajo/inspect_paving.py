import bpy,json,numpy as np
from pathlib import Path
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit')
o=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Relieve'))
m=o.data;v=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',v);v=v.reshape(-1,3);print('TERRAIN',o.name,len(m.polygons),len(m.vertices),list(o.matrix_world.translation),v.min(0),v.max(0),[(a.name,a.domain,a.data_type) for a in m.color_attributes]);print('MATRIX',list(map(list,o.matrix_world)));print('ZS',np.unique(np.round(v[:,2],2))[:25])
