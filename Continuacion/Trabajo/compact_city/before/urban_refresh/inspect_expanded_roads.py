import bpy,json
from pathlib import Path
x=[dict(name=o.name,verts=len(o.data.vertices),faces=len(o.data.polygons),location=list(o.location)) for o in bpy.data.objects if o.type=='MESH' and ('Road' in o.name or 'Calle' in o.name or 'SM_Mapa' in o.name)]
Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh/road_objects.json').write_text(json.dumps(x));print(x[-8:])
