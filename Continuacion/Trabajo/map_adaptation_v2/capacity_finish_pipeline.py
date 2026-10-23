from pathlib import Path
import unreal
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2')
for name in ['fix_shared_corridors.py','fix_exit_capacity.py','rebuild_clearance_callers.py','fix_external_obstacles.py','respace_clear_stoplines.py','fix_manager_instance.py','build_debug_traffic.py']:
 unreal.log('V2_CAPACITY_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
