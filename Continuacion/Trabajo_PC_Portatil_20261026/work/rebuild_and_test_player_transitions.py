import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_player_vehicle_transition.py','build_player_interaction_runtime_test.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
