import bpy,json,numpy as np
from pathlib import Path
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');m=json.loads((R/'new_map_audit/before_spacing_expansion/manifest.json').read_text());out=[]
for item in m['instances']:
 if 'bounds' not in item or 'Relieve' in item['source']:continue
 lo,hi=np.array(item['bounds']);
 if max(hi[:2]-lo[:2])<18:continue
 o=bpy.data.objects.get(item['source']);me=o.data;v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.array(o.matrix_world);v=v@mat[:3,:3].T+mat[:3,3];v=(v-[121.6244,55.6001,0])*[300,-300,300];starts=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_start',starts);li=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',li);z=v[li,2];a=np.minimum.reduceat(z,starts);b=np.maximum.reduceat(z,starts);sel=np.where((a<255)&(b>245))[0];rows=[v[list(me.polygons[i].vertices),:2].tolist() for i in sel];out.append(dict(source=item['source'],polygons=rows))
(R/'compact_city/large_building_tall_footprints.json').write_text(json.dumps(out));print('LARGE_BUILDING_TALL_FOOTPRINTS_READY',len(out))
