from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['extend_pure_traffic_paint_lights.py','test_pure_traffic_doors.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
