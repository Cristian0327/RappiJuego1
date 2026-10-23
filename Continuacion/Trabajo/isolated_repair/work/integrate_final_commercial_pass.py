import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/import_refined_large_shelves.py').read_text(encoding='utf-8-sig'))
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig'))
exec((root/'work/place_large_commercial_spaces.py').read_text(encoding='utf-8-sig'))
