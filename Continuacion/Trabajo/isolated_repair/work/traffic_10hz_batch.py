import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['optimize_pure_traffic_interpolated_rate.py','test_pure_traffic_10hz_stress.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{})
