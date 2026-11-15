from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for n in ['fix_shared_corridors.py','rebuild_clearance_callers.py','fix_external_obstacles.py','fix_service_braking.py','build_proxy_debug.py']:
 unreal.log('V2_PHYSICAL_FOLLOW_STAGE '+n);exec(compile((P/n).read_text(),n,'exec'),{})
