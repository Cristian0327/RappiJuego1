import bpy,json
from pathlib import Path
for o in bpy.data.objects:
 if o.name.startswith('Plane'):print('PLANE',o.name,'hide',o.hide_viewport,o.hide_render,o.hide_get(),'collections',[c.name for c in o.users_collection], 'mat',[(m.name,[(n.type) for n in m.node_tree.nodes] if m.use_nodes else []) for m in o.data.materials]);o.hide_render=True
print('COLLECTIONS',[(c.name,c.hide_render,c.hide_viewport) for c in bpy.data.collections])
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/inspect_new_map.py').read_text().replace("'overview.png'","'overview_no_planes.png'"))
