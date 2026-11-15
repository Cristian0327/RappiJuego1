from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for n in ['migrate_weather_state_pure_blueprint.py','test_pure_weather_state.py']:
 p=r/'work'/n;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__name__':'__main__'})
