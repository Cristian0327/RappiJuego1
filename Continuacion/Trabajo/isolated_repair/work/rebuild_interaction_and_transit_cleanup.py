from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for n in ['build_visible_transit_passenger.py','build_player_interaction_runtime_test.py']:
 p=r/'work'/n;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__name__':'__main__'})
