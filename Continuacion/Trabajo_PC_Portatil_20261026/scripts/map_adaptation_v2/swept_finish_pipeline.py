from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for name in ['lamp_lens_finish.py','respace_clear_stoplines.py','fix_manager_instance.py','build_debug_traffic.py','build_product_lifecycle.py']:
 unreal.log('V2_SWEEP_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
