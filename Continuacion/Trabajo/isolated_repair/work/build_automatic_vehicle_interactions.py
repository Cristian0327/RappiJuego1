from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['build_developer_door_controller.py','build_player_vehicle_transition.py']:
 p=r/'work'/name;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
unreal.log('AUTOMATIC_VEHICLE_TRANSITION_ASSETS_PASS')
