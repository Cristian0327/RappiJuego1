import bpy,json,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');P=R/'map_adaptation_v2';m=json.loads((R/'urban_safety/leveled_manifest.json').read_text());out=[]
for item in m['instances']:
 if 'bounds' not in item or 'Relieve' in item['source'] or item['mesh'].startswith('SM_Mapa_Road'):continue
 o=bpy.data.objects.get(item['source'])
 if not o or o.type!='MESH':continue
 me=o.data;v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);mat=np.array(o.matrix_world);v=v@mat[:3,:3].T+mat[:3,3];v*=np.array([100,-100,100]);starts=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('loop_start',starts);li=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',li);z=v[li,2];lo=np.minimum.reduceat(z,starts);hi=np.maximum.reduceat(z,starts)
 polys={}
 for name,height in [('low',100),('tall',240)]:
  ids=np.where((lo<height+10)&(hi>height-10))[0];polys[name]=[v[list(me.polygons[int(i)].vertices),:2].tolist() for i in ids]
 out.append(dict(source=item['source'],mesh=item['mesh'],location=list(o.location),polygons=polys))
(P/'current_building_sections.json').write_text(json.dumps(out))
terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));v=np.array([list(terrain.matrix_world@q.co) for q in terrain.data.vertices]);tree=BVHTree.FromPolygons([Vector(q) for q in v],[list(p.vertices) for p in terrain.data.polygons]);rows=json.loads((R/'compact_city/authored_street_curves.json').read_text())
for row in rows:
 zs=[]
 for p in row['samples']:
  co,_,_,_=tree.ray_cast(Vector((p[0]/100,-p[1]/100,250)),Vector((0,0,-1)));zs.append(co.z*100 if co is not None else None)
 row['terrain_heights']=zs
(P/'authored_streets_ground.json').write_text(json.dumps(rows));print('V2_BLENDER_EXTRACT_READY',len(rows),len(out))
