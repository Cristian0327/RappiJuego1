import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
for n in ['import_upright_postures.py','build_developer_door_controller.py','build_player_vehicle_transition.py','build_two_wheeler_citizen.py','build_combined_vehicle_controls.py']:
 exec(compile((r/'work'/n).read_text(encoding='utf-8-sig'),str(r/'work'/n),'exec'),{'__file__':str(r/'work'/n)})
unreal.log('POSTURE_TIMING_DOORS_CONTROLS_BUILD_PASS')
