import bpy,json
from pathlib import Path
out=[];dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.name.startswith('Plane') and not o.hide_get():
  e=o.evaluated_get(dg);m=e.to_mesh();curve=next((v.object for v in o.modifiers if v.type=='CURVE'),None)
  out.append({'name':o.name,'raw':[list(v.co) for v in o.data.vertices[:65]],'nraw':len(o.data.vertices),'neval':len(m.vertices),'evaluated':[list(o.matrix_world@v.co) for v in m.vertices[:65]],'curve':{'name':curve.name,'splines':[{'cyclic':s.use_cyclic_u,'points':[{'co':list(curve.matrix_world@p.co),'left':list(curve.matrix_world@p.handle_left),'right':list(curve.matrix_world@p.handle_right)} for p in s.bezier_points]} for s in curve.data.splines]} if curve else None});e.to_mesh_clear()
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/road_structure.json').write_text(json.dumps(out))
