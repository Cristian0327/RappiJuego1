from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['test_pure_store_all_themes.py','test_pure_delivery_data_core.py','test_pure_delivery_progress.py']:
 unreal.log('PURE_SUBSYSTEM_QA '+name);exec(compile((r/'work'/name).read_text(encoding='utf-8-sig'),str(r/'work'/name),'exec'),{})
unreal.log('PURE_SUBSYSTEM_ALL_QA_PASS')
