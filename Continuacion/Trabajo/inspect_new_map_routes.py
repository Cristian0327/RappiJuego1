import bpy,json
from mathutils import Vector
from pathlib import Path
out={'roads':[],'curves':[],'objects':[]};dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.hide_get():continue
 if o.type=='MESH':
  e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];out['objects'].append({'name':o.name,'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)],'polys':len(m.polygons)});e.to_mesh_clear()
 if o.name.startswith('Plane'):
  out['roads'].append({'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'dimensions':list(o.dimensions),'mods':[{'type':m.type,'curve':m.object.name if m.type=='CURVE' and m.object else None,'axis':m.deform_axis if m.type=='CURVE' else None} for m in o.modifiers]})
 if o.type=='CURVE':
  out['curves'].append({'name':o.name,'location':list(o.location),'scale':list(o.scale),'splines':[{'type':s.type,'cyclic':s.use_cyclic_u,'points':[{'co':list(o.matrix_world@p.co),'left':list(o.matrix_world@p.handle_left),'right':list(o.matrix_world@p.handle_right)} for p in s.bezier_points]} for s in o.data.splines]})
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/evaluated.json').write_text(json.dumps(out))
