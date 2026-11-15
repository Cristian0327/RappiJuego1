from pathlib import Path
import unreal
r=Path(unreal.Paths.project_dir()).parent
for n in ['create_blueprint_gameplay_schema.py','migrate_blueprint_data_tables.py']:
 p=r/'work'/n;exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__name__':'__main__'})
