import bpy,json,numpy as np
from pathlib import Path
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');C=W/'compact_city';m=json.loads((W/'new_map_audit/before_spacing_expansion/manifest.json').read_text());out=[];polys=[]
for idx,item in enumerate(m['instances']):
 if 'bounds' not in item or 'Relieve' in item['source']:continue
 o=bpy.data.objects.get(item['source'])
 if not o:continue
 me=o.data;v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.array(o.matrix_world);v=(v@mat[:3,:3].T+mat[:3,3])*[100,-100,100];starts=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_start',starts);li=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',li);z=v[li,2];lo=np.minimum.reduceat(z,starts);hi=np.maximum.reduceat(z,starts);sel=np.where((hi>30)&(lo<220))[0];rows=[]
 for j in sel:rows.append(v[list(me.polygons[j].vertices),:2].tolist())
 out.append(dict(source=item['source'],polygons=rows))
(C/'original_object_wall_polygons.json').write_text(json.dumps(out));print('INDIVIDUAL_WALL_FOOTPRINTS_READY',len(out))
