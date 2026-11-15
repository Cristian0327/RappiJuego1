import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_pure_transit_passenger_visual.py','build_pure_station_passenger.py','build_pure_station_passenger_qa.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{})

