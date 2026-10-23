import bpy,json
from pathlib import Path
out=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  m=o.data
  if len(m.polygons)<10 or o.display_type=='WIRE':
   out.append(dict(name=o.name,hidden=o.hide_get(),display=o.display_type,verts=len(m.vertices),faces=len(m.polygons),edges=[[(o.matrix_world@m.vertices[i].co)[: ] for i in e.vertices] for e in m.edges] if len(m.edges)<600 else []))
 elif o.type=='CURVE':out.append(dict(name=o.name,type='CURVE',splines=[dict(cyclic=s.use_cyclic_u,points=[list(o.matrix_world@p.co) for p in s.bezier_points] if s.type=='BEZIER' else [list(o.matrix_world@p.co.xyz) for p in s.points]) for s in o.data.splines]))
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh/source_lines.json').write_text(json.dumps(out))
print('SOURCE_LINE_AUDIT',[(x['name'],x.get('verts'),x.get('faces')) for x in out])
