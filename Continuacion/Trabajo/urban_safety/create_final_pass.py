from pathlib import Path
p=Path('urban_safety/implement_fixes.py');s=p.read_text();header=s[:s.index('# The previous material')];a=s.index('for file,dest in imports:');b=s.index('# Every urban plot',a);imports="imports=[(v,'/Game/Maps/MapaCompleto/Geometry') for v in sorted((P/'export_clean').glob('SM_Mapa_*.fbx'))]\n";body=s[a:b]+s[b:];# component identification uses clean files for all architecture meshes.
body=body.replace("(P/'export'/(mesh.get_name()+'.fbx')).exists()","(P/'export_clean'/(mesh.get_name()+'.fbx')).exists()")
Path('urban_safety/finalize_fixes.py').write_text(header+imports+body)
