from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for n in ['unify_service_controllers.py','fix_service_braking.py','build_proxy_debug.py']:
 unreal.log('V2_UNIFIED_STAGE '+n);exec(compile((P/n).read_text(),n,'exec'),{})
