import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['extend_pure_traffic_doors.py','extend_pure_traffic_wheel_pose.py','test_pure_traffic_doors.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
