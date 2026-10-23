from pathlib import Path
import unreal
assert 'isolated_repair' in Path(unreal.Paths.project_dir()).parts
p=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair')
for name in ['final_asset_audit.py','build_patrol_probe.py']:
 exec(compile((p/name).read_text(),name,'exec'),{})
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
