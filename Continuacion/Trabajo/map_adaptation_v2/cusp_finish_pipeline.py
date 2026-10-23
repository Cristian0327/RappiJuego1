from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for n in ['install_smooth_lanes.py','install_body_zones_and_platoons.py','fix_shared_corridors.py','fix_exit_capacity.py','rebuild_clearance_callers.py','fix_external_obstacles.py','fix_service_braking.py','install_signals.py','respace_clear_stoplines.py','fix_manager_instance.py','build_proxy_debug.py']:
 unreal.log('V2_CUSP_STAGE '+n);exec(compile((P/n).read_text(),n,'exec'),{})
