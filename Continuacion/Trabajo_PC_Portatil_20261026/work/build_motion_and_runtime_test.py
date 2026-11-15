import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for n in ['build_rider_motion_coordinator.py','build_player_interaction_runtime_test.py']:
 exec(compile((r/'work'/n).read_text(encoding='utf-8-sig'),str(r/'work'/n),'exec'),{'__file__':str(r/'work'/n)})
