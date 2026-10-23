import bpy,json,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');C=R/'compact_city';curves=[]
for o in bpy.data.objects:
 if o.type!='CURVE':continue
 for si,s in enumerate(o.data.splines):
  if not s.bezier_points:continue
  pts=list(s.bezier_points);controls=np.array([list(o.matrix_world@p.co) for p in pts])
  if np.max(abs(controls[:,2]))>.01 or np.max(controls[:,0])<10:continue
  samples=[];count=len(pts) if s.use_cyclic_u else len(pts)-1
  for i in range(count):
   p=pts[i];q=pts[(i+1)%len(pts)];a=o.matrix_world@p.co;b=o.matrix_world@p.handle_right;c=o.matrix_world@q.handle_left;d=o.matrix_world@q.co;n=max(3,int((d-a).length*3/.5))
   for t in np.linspace(0,1,n,endpoint=False):samples.append(list((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d))
  samples.append(list(o.matrix_world@pts[-1].co));v=(np.array(samples)-[121.6244,55.6001,0])*[300,-300,300];curves.append(dict(name=o.name+'_'+str(si),samples=v.tolist(),cyclic=s.use_cyclic_u))
(C/'authored_street_curves.json').write_text(json.dumps(curves));terrain=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));tree=BVHTree.FromPolygons([v.co for v in terrain.data.vertices],[list(p.vertices) for p in terrain.data.polygons]);inv=terrain.matrix_world.inverted();direction=inv.to_3x3()@Vector((0,0,-1));height=np.ones((500,400),np.float32)*np.nan
# Read the untouched terrain with the original three-times map transform.
for y in range(500):
 for x in range(400):
  xx=x*200-40000;yy=y*200-50000;raw=Vector((xx/300+121.6244,-yy/300+55.6001,200));hit,n,j,dist=tree.ray_cast(inv@raw,direction)
  if hit is not None:height[y,x]=(terrain.matrix_world@hit).z*300
np.save(C/'original_terrain_heights_2m.npy',height)
meta=dict(curves=len(curves),terrain_properties=str(dict(terrain.items())),modifiers=[(v.name,v.type) for v in terrain.modifiers],texts=[dict(name=t.name,lines=[line for line in t.as_string().splitlines() if any(w in line.lower() for w in ['monser','zig','sender','camino','hill','summit','trail'])]) for t in bpy.data.texts]);(C/'hill_source_metadata.json').write_text(json.dumps(meta,indent=2));print('AUTHORED_STREETS_AND_ORIGINAL_HEIGHTS_READY',len(curves))
