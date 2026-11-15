from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['test_pure_phone_map.py','audit_pure_dependency_closure.py']:
 exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),name,'exec'),{})
unreal.log('PURE_PHONE_DEPENDENCY_AND_MAP_VALIDATION_PASS')
