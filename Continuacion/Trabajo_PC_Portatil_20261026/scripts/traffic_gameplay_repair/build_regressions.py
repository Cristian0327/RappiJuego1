from pathlib import Path
import unreal
assert 'isolated_repair' in Path(unreal.Paths.project_dir()).parts
P=Path('C:/Users/Cristian/Downloads/BogotaVoxel_test_Michaelxd_2026-10-23/isolated_repair/scripts/traffic_gameplay_repair')
for name in ['build_lifecycle_probe.py','build_physics_probe.py']:
 exec(compile((P/name).read_text(),name,'exec'),{})
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
