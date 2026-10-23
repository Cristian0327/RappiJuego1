import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['extend_pure_traffic_movement.py','extend_pure_traffic_exit_clear.py','integrate_pure_traffic_signals.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
