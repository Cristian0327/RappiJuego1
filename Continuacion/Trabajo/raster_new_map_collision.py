import bpy,json,numpy as np

from pathlib import Path
W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');N=800;H=1000;OX=-40000;OY=-50000;STEP=100
walls=[];floors=[];cnt=0
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_get() or o.name.startswith('Plane'):continue
 mesh=o.data;v=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.array(o.matrix_world);v=v@mat[:3,:3].T+mat[:3,3];v=(v-np.array([121.6244,55.6001,0]))*300;v[:,1]*=-1
 starts=np.empty(len(mesh.polygons),np.int32);mesh.polygons.foreach_get('loop_start',starts);li=np.empty(len(mesh.loops),np.int32);mesh.loops.foreach_get('vertex_index',li);z=v[li,2];lo=np.minimum.reduceat(z,starts);hi=np.maximum.reduceat(z,starts);terrain=o.name.startswith('Relieve');selected=np.where(((hi>30)&(lo<220))|((lo>-30)&(hi<30)))[0]
 for i in selected:
  p=mesh.polygons[i];points=[((v[j,0]-OX)/STEP,(v[j,1]-OY)/STEP) for j in p.vertices]
  if lo[i]>-30 and hi[i]<30:
   floors.append(points)
  elif hi[i]>30 and lo[i]<220:
   walls.append(points);cnt+=1

np.save(W/'wall_polygons.npy',np.array(walls,dtype=object),allow_pickle=True);np.save(W/'floor_polygons.npy',np.array(floors,dtype=object),allow_pickle=True);print('PHYSICAL_FOOTPRINTS',cnt)
