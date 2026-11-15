from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for name in ['build_overview.py','build_food_lifecycle.py']:
 exec(compile((P/name).read_text(),name,'exec'),{})
