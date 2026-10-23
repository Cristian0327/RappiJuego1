import bpy,json
from pathlib import Path
out=[]
for o in bpy.data.objects:
 if o.name.startswith('Plane'):
  out.append({'name':o.name,'hide':o.hide_get(),'mods':[(m.name,m.type) for m in o.modifiers],'verts':len(o.data.vertices),'edges':len(o.data.edges),'faces':len(o.data.polygons),'materials':[{'name':m.name,'color':list(m.diffuse_color),'nodes':[{'type':n.type,'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes]} for m in o.data.materials],'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'polygons':[list(f.vertices) for f in o.data.polygons]})
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/planes.json').write_text(json.dumps(out))
# Render exactly the visible working scene, including its road object.
for o in bpy.data.objects:o.hide_render=o.hide_get()
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/inspect_new_map.py').read_text().replace("'overview.png'","'overview_visible.png'"))
