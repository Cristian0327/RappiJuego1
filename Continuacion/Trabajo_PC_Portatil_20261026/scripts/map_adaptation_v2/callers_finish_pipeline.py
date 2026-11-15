from pathlib import Path
import unreal
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/map_adaptation_v2')
for name in ['rebuild_clearance_callers.py','build_investigation_probe.py','verify_physical_streets.py','build_overview.py']:
 unreal.log('V2_CALLER_STAGE '+name);exec(compile((P/name).read_text(),name,'exec'),{})
