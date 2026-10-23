import bpy,json,numpy as np,math
from pathlib import Path
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');f=json.loads((W/'manifest.json').read_text())['spacing_expansion'];out=[];count=0
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_get() or o.name.startswith('Plane'):continue
 mesh=o.data;v=np.empty(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.array(o.matrix_world);v=v@mat[:3,:3].T+mat[:3,3];v*=100;v[:,1]*=-1;starts=np.empty(len(mesh.polygons),np.int32);sizes=np.empty(len(mesh.polygons),np.int32);mesh.polygons.foreach_get('loop_start',starts);mesh.polygons.foreach_get('loop_total',sizes);li=np.empty(len(mesh.loops),np.int32);mesh.loops.foreach_get('vertex_index',li);z=v[li,2];lo=np.minimum.reduceat(z,starts);hi=np.maximum.reduceat(z,starts);chosen=np.where((hi>30)&(lo<220)&(sizes<=4))[0]
 if not len(chosen):continue
 ix=starts[chosen,None]+np.minimum(np.arange(4)[None,:],sizes[chosen,None]-1);pts=v[li[ix],:2];pts[:,:,0]=(pts[:,:,0]+40000*f)/100;pts[:,:,1]=(pts[:,:,1]+50000*f)/100;out.append(pts.astype(np.float32));count+=len(pts)
np.save(W/'expanded_wall_quads.npy',np.concatenate(out));print('EXPANDED_WALL_QUADS',count)
