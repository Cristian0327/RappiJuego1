import bpy, json
from pathlib import Path
out=[];dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.name.startswith('Plane') and not o.hide_get():
  e=o.evaluated_get(dg);m=e.to_mesh();n=len(o.data.vertices);groups={}
  for v in o.data.vertices:groups.setdefault(round(v.co.x,5),[]).append(v)
  pairs=[]
  for x,vs in sorted(groups.items()):pairs.append((min(vs,key=lambda v:v.co.y).index,max(vs,key=lambda v:v.co.y).index))
  rows=[]
  for j in range(len(m.vertices)//n):
   for a,b in pairs:
    l=o.matrix_world@m.vertices[j*n+a].co;rr=o.matrix_world@m.vertices[j*n+b].co;c=(l+rr)/2
    if not rows or (c-__import__('mathutils').Vector(rows[-1]['center'])).length>1:
     rows.append({'center':list(c),'left':list(l),'right':list(rr)})
  out.append({'name':o.name,'rows':rows});e.to_mesh_clear()
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/road_rows.json').write_text(json.dumps(out))
print('ROAD_SAMPLES',[(o['name'],len(o['rows'])) for o in out])
