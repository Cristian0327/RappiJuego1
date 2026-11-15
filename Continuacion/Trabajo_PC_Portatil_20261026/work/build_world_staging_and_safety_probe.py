from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for n in ['migrate_city_geometry_blueprint.py','build_rider_safety_runtime_test.py']:
 p=r/'work'/n;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__name__':'__main__'})
