from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for name in ['fix_external_obstacles.py','build_overview.py','build_current_physics.py','build_food_lifecycle.py','build_debug_traffic.py']:
 unreal.log('V2_EXTERNAL_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
