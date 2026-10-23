import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_pure_traffic_junction.py','test_pure_traffic_junction.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
