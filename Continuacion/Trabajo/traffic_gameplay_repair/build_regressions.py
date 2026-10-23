from pathlib import Path
import unreal
assert 'isolated_repair' in Path(unreal.Paths.project_dir()).parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair')
for name in ['build_lifecycle_probe.py','build_physics_probe.py']:
 exec(compile((P/name).read_text(),name,'exec'),{})
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
