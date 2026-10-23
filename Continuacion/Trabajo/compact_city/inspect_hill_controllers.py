import bpy,json
from pathlib import Path
out=[]
for o in bpy.data.objects:
 if any(w in o.name.lower() for w in ['monser','camino','sender','cerro','control','relieve']):out.append(dict(name=o.name,type=o.type,loc=list(o.location),props=str(dict(o.items()))))
t=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));mods=[]
for m in t.modifiers:
 if m.type=='NODES':mods.append(dict(name=m.name,group=m.node_group.name,nodes=[dict(name=n.name,type=n.type,inputs=[dict(name=i.name,value=str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_group.nodes]))
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/compact_city/hill_controllers.json').write_text(json.dumps(dict(objects=out,modifiers=mods),indent=2));print('HILL_CONTROLLERS_READY')
