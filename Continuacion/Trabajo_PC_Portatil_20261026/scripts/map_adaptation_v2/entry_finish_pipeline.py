from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for name in ['fix_entry_obstacles.py','integrate_navigation.py','verify_physical_streets.py','build_debug_traffic.py','build_product_lifecycle.py']:
 unreal.log('V2_ENTRY_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
