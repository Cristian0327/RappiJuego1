from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for name in ['fix_shared_corridors.py','fix_exit_capacity.py','rebuild_clearance_callers.py','fix_external_obstacles.py','respace_clear_stoplines.py','fix_manager_instance.py','build_debug_traffic.py']:
 unreal.log('V2_CAPACITY_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
