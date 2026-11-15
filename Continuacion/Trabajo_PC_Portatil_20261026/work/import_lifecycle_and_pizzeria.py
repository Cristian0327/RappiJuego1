from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir()).parents[1]
for filename in ['migrate_lifecycle_blueprints.py','import_pizzeria_final.py']:
 exec(compile((root/'work'/filename).read_text(encoding='utf-8-sig'),str(root/'work'/filename),'exec'),{'__name__':'__main__'})
