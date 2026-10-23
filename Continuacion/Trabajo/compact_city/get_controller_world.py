import bpy,json
from pathlib import Path
out=[]
for o in bpy.data.objects:
 if o.type=='EMPTY' and 'CONTROL' in o.name:out.append(dict(name=o.name,world=list(o.matrix_world.translation),scale=list(o.matrix_world.to_scale()),parent=o.parent.name if o.parent else None))
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/compact_city/hill_controller_world.json').write_text(json.dumps(out,indent=2));print(out)
