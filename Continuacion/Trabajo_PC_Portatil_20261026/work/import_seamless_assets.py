from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/import_shopfronts_final.py').read_text(encoding='utf-8-sig'))
exec((root/'work/import_customer_walk.py').read_text(encoding='utf-8-sig'))
