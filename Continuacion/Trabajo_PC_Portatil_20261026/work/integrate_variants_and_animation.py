from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for name in ['import_all_store_rebuilt.py','distribute_city_services.py','build_city_services_runtime_test.py']:
 p=r/'work'/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
unreal.log('VARIANTS_AND_ALL_STORE_ANIMATIONS_PIPELINE_PASS')
