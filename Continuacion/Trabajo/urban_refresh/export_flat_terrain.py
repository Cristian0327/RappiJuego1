import bpy,numpy as np
from pathlib import Path
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');o=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));m=o.data;v=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',v);v=v.reshape(-1,3);M=np.array(o.matrix_world);v=v@M[:3,:3].T+M[:3,3];v*=np.array([100,-100,100]);li=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',li);starts=np.empty(len(m.polygons),np.int32);m.polygons.foreach_get('loop_start',starts);lo=np.minimum.reduceat(v[li,2],starts);hi=np.maximum.reduceat(v[li,2],starts);sel=np.where((lo> -35)&(hi<35))[0];out=[]
for i in sel:
 q=v[list(m.polygons[i].vertices),:2]
 if len(q)==3:q=np.concatenate([q,q[-1:]])
 if len(q)==4:out.append(q)
np.save(U/'terrain_flat_quads.npy',np.asarray(out,np.float32));print('FLAT_TERRAIN_QUADS',len(out))
raised=[]
for i in np.where(hi>35)[0]:
 q=v[list(m.polygons[i].vertices),:2]
 if len(q)==3:q=np.concatenate([q,q[-1:]])
 if len(q)==4:raised.append(q)
np.save(U/'terrain_raised_quads.npy',np.asarray(raised,np.float32))
