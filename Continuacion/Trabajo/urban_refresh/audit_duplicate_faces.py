import bpy,numpy as np
for o in [next(o for o in bpy.data.objects if o.name.startswith('Relieve')),next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('M005_LOD0'))]:
 me=o.data;v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);centers=np.array([p.center[:] for p in me.polygons]);_,counts=np.unique(np.round(centers,4),axis=0,return_counts=True);print('GEOMETRY_AUDIT',o.name,'faces',len(me.polygons),'coincident_centres',int(np.sum(counts-1)),'smooth_faces',sum(p.use_smooth for p in me.polygons))
